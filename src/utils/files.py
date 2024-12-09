import os
import json
import pandas as pd

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_csv(data, filename, index_name='word'):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = index_name
    df.to_csv(filename, encoding='utf-8', sep='\t')
    
def write_file(filepath, content):
    
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def write_json(filepath, content):
    
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
        
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)
        
def create_book_id(filename):
    return filename.split('.')[0]

def load_texts(input_folder, split=False):
    files = os.listdir(input_folder)
    if len(files) == 0:
        raise FileNotFoundError(f'The folder {input_folder} is empty.')
    texts = {}
    for filename in files:
        book_id = create_book_id(filename)
        text = read_file(os.path.join(input_folder, filename))
        texts[book_id] = text if not split else text.split('\n')
    return texts

def load_jsons(input_folder):
    files = os.listdir(input_folder)
    if len(files) == 0:
        raise FileNotFoundError(f'The folder {input_folder} is empty.')
    jsons = {}
    for filename in files:
        book_id = create_book_id(filename)
        jsons[book_id] = read_json(os.path.join(input_folder, filename))
    return jsons