import pandas as pd

from bs4 import BeautifulSoup

output_path = '../data/Obras Corpus/txts/'
corpus = {
    'filename': [],
    'id': [],
    'title': [],
    'author': [],
    'genre': []
}

with open('../data/Obras Corpus/corpoObras.txt', 'r', encoding='latin-1') as f:
    raw_html = f.read()
    raw_html = BeautifulSoup(raw_html, "html.parser")
    obras = raw_html.find_all('obra')    
    print(len(obras))
    for idx, obra in enumerate(obras):
        obra_id = obra["id"]
        filename = f'obra_{idx}'
        genre = obra_id.split('Prosa:')[1].split(' ')[0] if 'Prosa' in obra_id else None
        title = obra.find('tituloobra')["id"]
        author = obra.find('autor')["id"]
        
        corpus['filename'].append(filename)
        corpus['id'].append(obra_id)
        corpus['title'].append(title)
        corpus['author'].append(author)
        corpus['genre'].append(genre)        
        
        raw_html = obra.text
        with open(output_path + str(filename) + '.txt', 'w', encoding='latin-1') as out:
            out.write(raw_html)

df = pd.DataFrame(corpus)
df.to_csv('../data/Obras Corpus/corpus.csv', index=False, sep='\t')
        