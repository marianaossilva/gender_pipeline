import os
import time
import spacy
import logging
import datetime as dt

from tqdm import tqdm
from preprocessing import preprocess_text
from ner import extract_person_entities
from segmentation import segment_excerpts
from gender_classification import classify_gender
from dependency_analysis import analyze_dependencies
from bias_analysis import bias_analysis
from utils.files import  write_file, write_json, load_texts, load_jsons

def process_step(step_number, description, data, process_func, output_path):
    logging.info(f'Iniciando etapa {step_number}: {description}')
    start = time.time()
    data_dict = {}
    for book_id, item in tqdm(data.items(), desc=description):
        data_dict[book_id] = process_func(item)
        write_json(os.path.join(output_path, f'{book_id}.json'), data_dict[book_id])
    elapsed = time.time() - start
    logging.info(f'Etapa {step_number} executada em {str(dt.timedelta(seconds=elapsed))}')
    return data_dict

def update_step(step_number, description, data, process_func, output_path):
    logging.info(f'Iniciando etapa {step_number}: {description}')
    start = time.time()
    for book_id, item in tqdm(data.items(), desc=description):
        data[book_id] = process_func(item)
        write_json(os.path.join(output_path, f'{book_id}.json'), data[book_id])
    elapsed = time.time() - start
    logging.info(f'Etapa {step_number} executada em {str(dt.timedelta(seconds=elapsed))}')
    return data

def run_pipeline(input_folder, preprocessed_folder, output_folder, group_results, steps):
    os.makedirs(preprocessed_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Load spaCy model once
    nlp = spacy.load('pt_core_news_lg', exclude=['ner', 'textcat'])
    
    texts = {}
    preprocessed_texts = {}
    all_entities = {}
    excerpts = {}
    gender_total_dict = {}
    overall_stats_dict = {}
    gender_bias_dict = {}
    attribute_dict = {}

    if 1 in steps:
        logging.info('Iniciando etapa de pré-processamento')
        start = time.time()
        texts = load_texts(input_folder)
        for book_id, text in tqdm(texts.items(), desc='Pré-processamento'):
            preprocessed_texts[book_id] = {'sentences': preprocess_text(text, nlp)}
            write_file(os.path.join(preprocessed_folder, f'{book_id}.txt'), '\n'.join(preprocessed_texts[book_id]['sentences']))
            write_json(os.path.join(output_folder + '/sentences', f'{book_id}.json'), preprocessed_texts[book_id])
        end = time.time()
        elapsed = end - start
        logging.info(f'Etapa 1 executada em {str(dt.timedelta(seconds=elapsed))}')
    elif 1 not in steps and (2 in steps or 3 in steps):
        preprocessed_texts = load_jsons(output_folder + '/sentences')
        logging.info('Pré-processamento carregado')

    if 2 in steps:
        all_entities = process_step(2, 'Identificação de indivíduos', preprocessed_texts, extract_person_entities, output_folder + '/sentences')
    elif 2 not in steps and 3 in steps:
        all_entities = load_jsons(output_folder + '/sentences')
        logging.info('Entidades carregadas')
    
    if 3 in steps:
        excerpts = process_step(3, 'Segmentação de trechos', all_entities, segment_excerpts, output_folder + '/book_dicts')
    elif 3 not in steps and 4 in steps:
        excerpts = load_jsons(output_folder + '/book_dicts')
        logging.info('Trechos carregados')
    
    if 4 in steps:
        excerpts = update_step(4, 'Inferência de gênero', excerpts, classify_gender, output_folder + '/book_dicts')
    elif 4 not in steps and 5 in steps:
        excerpts = load_jsons(output_folder + '/book_dicts')
        logging.info('Gêneros carregados')
    
    if 5 in steps:
        excerpts = update_step(5, 'Análise de dependências', excerpts, analyze_dependencies, output_folder + '/book_dicts')
    elif 5 not in steps and 6 in steps:
        excerpts = load_jsons(output_folder + '/book_dicts')
        logging.info('Dependências carregadas')
    
    if 6 in steps:
        logging.info('Iniciando etapa de cálculo de viés de gênero')
        start = time.time()
        if group_results == True:
            book_id = 'all_books'
            excerpts = {book_id: [entity for entities in excerpts.values() for entity in entities]}
        
        for book_id, entities in tqdm(excerpts.items(), total=len(excerpts), desc='Cálculo de viés de gênero'):
            gender_total_dict[book_id], overall_stats_dict[book_id], gender_bias_dict[book_id], attribute_dict[book_id] = bias_analysis(entities)        
            write_json(os.path.join(output_folder + '/gender_total', f'{book_id}.json'), gender_total_dict[book_id])
            write_json(os.path.join(output_folder + '/overall_stats', f'{book_id}.json'), overall_stats_dict[book_id])
            write_json(os.path.join(output_folder + '/gender_bias', f'{book_id}.json'), gender_bias_dict[book_id])
            write_json(os.path.join(output_folder + '/attributes', f'{book_id}.json'), attribute_dict[book_id])
        end = time.time()
        elapsed = end - start
        logging.info(f'Etapa 6 executada em {str(dt.timedelta(seconds=elapsed))}')
        
    logging.info('Pipeline concluído')