import json
import requests
import xmltodict
import pandas as pd

from tqdm import tqdm

client_key='1vo0vPP17sXFZfKTdlpQ'
client_secret='KvH8vHatXqn6oq2DZtRe0Osblizm3keMkxXCJFaiVBY'

def get_book_metadata(book_id):
    base_url = "https://www.goodreads.com/"
    complement = "book/show/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    params = {'id': book_id}
    response = requests.get(base_url + complement, headers=headers, params=params)
    
    if response.status_code == 200:
        data_dict = xmltodict.parse(response.content)
        results = data_dict['GoodreadsResponse']['book']
        return results
    return None

thesis_corpus = pd.read_csv('../data/thesis_corpus.tsv', sep='\t', encoding='utf-8')
titles = thesis_corpus['title']
authors = thesis_corpus['author']

with open('../data/book_metadata_goodreads.jsonl', 'w', encoding='utf-8') as f:
    for title, author in tqdm(zip(titles, authors), total=len(titles)):
        metadata = get_metadata(title, client_key)
        book_metadata = {'title': title, 'author': author, 'metadata': metadata}
        f.write(json.dumps(book_metadata, ensure_ascii=False, indent=4) + '\n')