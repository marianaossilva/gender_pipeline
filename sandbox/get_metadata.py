import json
import requests
import pandas as pd

from tqdm import tqdm

def get_metadata(title, author):
    base_url = "https://openlibrary.org/search.json"
    params = {
        'title': title,
        'author': author,
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data  = response.json()
        if data['docs']:
            return data['docs'][0]
            # subjects = data['docs'][0].get('subject', [])
            # return subjects if subjects else None
    return None

thesis_corpus = pd.read_csv('../data/thesis_corpus.tsv', sep='\t', encoding='utf-8')
titles = thesis_corpus['title']
authors = thesis_corpus['author']

with open('../data/book_metadata.jsonl', 'w', encoding='utf-8') as f:
    for title, author in tqdm(zip(titles, authors), total=len(titles)):
        metadata = get_metadata(title, author)
        book_metadata = {'title': title, 'author': author, 'metadata': metadata}
        f.write(json.dumps(book_metadata, ensure_ascii=False, indent=4) + '\n')