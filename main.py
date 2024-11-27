import os
import json
import time
import logging
import datetime as dt

from tqdm import tqdm
from src.preprocessing import preprocess_text
from src.ner import extract_person_entities
from src.segmentation import segment_excerpts
from src.gender_classification import classify_gender
from src.dependency_analysis import analyze_dependencies
from src.bias_analysis import bias_analysis
from src.utils.files import read_file, write_file, write_json
from src.utils.log_utils import set_logging_config
set_logging_config()

def create_book_id(filename):
    return filename.split('.')[0]

def main(input_folder, preprocessed_folder, output_folder):
    
    # Step 1: Preprocessing and Sentencer
    # logging.info('Iniciando etapa de pré-processamento')
    # start = time.time()
    # preprocessed_texts = {}
    # files = os.listdir(input_folder)[:1]
    # for filename in tqdm(files, total=len(files), desc='Pré-processamento'):
    #     filepath = os.path.join(input_folder, filename)
    #     book_id = create_book_id(filename)
    #     text = read_file(filepath)
    #     preprocessed_sentences = preprocess_text(text)
    #     preprocessed_texts[book_id] = preprocessed_sentences
    #     write_file(os.path.join(preprocessed_folder, filename), '\n'.join(preprocessed_sentences))
    # end = time.time()
    # elapsed = end - start
    # logging.info(f'Etapa 1 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    # # Step 2: Entity Recognition
    # logging.info('Iniciando etapa de reconhecimento de entidades')
    # start = time.time()
    # all_entities = {}
    # for book_id, sentences in tqdm(preprocessed_texts.items(), total=len(preprocessed_texts), desc='Reconhecimento de entidades'):
    #     all_entities[book_id] = extract_person_entities(sentences)
    #     write_json(os.path.join(output_folder + '/book_dicts', f'{book_id}.json'), all_entities[book_id])
    # end = time.time()
    # elapsed = end - start
    # logging.info(f'Etapa 2 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    # # Step 3: Excerpt Segmentation
    # logging.info('Iniciando etapa de segmentação de trechos')
    # start = time.time()
    # for book_id, entities in tqdm(all_entities.items(), total=len(all_entities), desc='Segmentação de trechos'):
    #     all_entities[book_id] = segment_excerpts(preprocessed_texts[book_id], entities)
    #     write_json(os.path.join(output_folder + '/book_dicts', f'{book_id}.json'), all_entities[book_id])
    # end = time.time()
    # elapsed = end - start
    # logging.info(f'Etapa 3 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    # # Step 4: Gender Classification
    # logging.info('Iniciando etapa de classificação de gênero')
    # start = time.time()
    # for book_id, entities in tqdm(all_entities.items(), total=len(all_entities), desc='Classificação de gênero'):
    #     all_entities[book_id] = classify_gender(entities)
    #     write_json(os.path.join(output_folder + '/book_dicts', f'{book_id}.json'), all_entities[book_id])
    # end = time.time()
    # elapsed = end - start
    # logging.info(f'Etapa 4 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    with open('data/results/book_dicts/103030.json', 'r', encoding='utf-8') as f:
        all_entities = {'103030': json.load(f)}
    
    # Step 5: Dependency Analysis
    # logging.info('Iniciando etapa de análise de dependências')
    # start = time.time()
    # for book_id, entities in tqdm(all_entities.items(), total=len(all_entities), desc='Análise de dependências'):
    #     all_entities[book_id] = analyze_dependencies(entities)        
    #     write_json(os.path.join(output_folder + '/book_dicts', f'{book_id}.json'), all_entities[book_id])
    # end = time.time()
    # elapsed = end - start
    # logging.info(f'Etapa 5 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    # Step 6: Gender Skewness
    logging.info('Iniciando etapa de cálculo de viés de gênero')
    start = time.time()
    gender_bias_dict = {}
    for book_id, entities in tqdm(all_entities.items(), total=len(all_entities), desc='Cálculo de viés de gênero'):
        gender_bias_dict[book_id] = bias_analysis(entities, output_folder + '/gender_bias')
        write_json(os.path.join(output_folder + '/gender_bias', f'{book_id}.json'), gender_bias_dict[book_id])
    end = time.time()
    elapsed = end - start
    logging.info(f'Etapa 6 executada em {str(dt.timedelta(seconds=elapsed))}')
    
    # # Step 7: Plot Results
    # TODO: Implementar função plot_results
    # plot_results(dependency_results, skewness_results, output_folder)

if __name__ == "__main__":
    
    logging.info('Iniciando execução do pipeline')
    start_geral = time.time()   
    input_folder = 'data/raw'
    preprocessed_folder = 'data/preprocessed'
    os.makedirs(preprocessed_folder, exist_ok=True)
    output_folder = 'data/results'
    os.makedirs(output_folder, exist_ok=True)
    main(input_folder, preprocessed_folder, output_folder)
    end_geral = time.time()
    elapsed_geral = end_geral - start_geral
    logging.info(f'Pipeline executado em {str(dt.timedelta(seconds=elapsed_geral))}')