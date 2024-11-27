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