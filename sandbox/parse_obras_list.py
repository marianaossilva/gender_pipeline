import pandas as pd

with open("../data/lista_de_obras.txt", "r") as f:
    obras = f.readlines()

obras_titles = []
obras_authors = []
for obra in obras:
    if 'tit=' in obra:
        obras_titles.append(obra.split('tit=')[1].replace('\n', ''))
    elif 'aut=' in obra:
        obras_authors.append(obra.split('aut=')[1].replace('\n', ''))

obras_corpus = pd.DataFrame({
        "title": obras_titles,
        "author": obras_authors
    })

obras_corpus.to_csv("../data/obras_corpus.csv", sep="\t", encoding="utf-8", index=False)
