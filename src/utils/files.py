import os
import json

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

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