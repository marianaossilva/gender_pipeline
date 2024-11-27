import pandas as pd
from difflib import SequenceMatcher


pportal_corpus = pd.read_csv("../data/pportal_corpus.csv", sep="\t", encoding="utf-8")
eltec_corpus = pd.read_csv("../data/eltecpor_corpus.tsv", sep="\t", encoding="utf-8")
tycho_corpus = pd.read_csv("../data/tycho_corpus.csv", sep="\t", encoding="utf-8")
colonia_corpus = pd.read_csv("../data/colonia_corpus.csv", encoding="utf-8")
obras_corpus = pd.read_csv("../data/obras_corpus.csv", sep="\t", encoding="utf-8")

pportal_corpus['corpus'] = 'PPORTAL'
eltec_corpus['corpus'] = 'ELTeC-por'
tycho_corpus['corpus'] = 'Tycho'
colonia_corpus['corpus'] = 'Colonia'
obras_corpus['corpus'] = 'Obras'

eltec_corpus.rename(columns={"author-gender": "author_gender", "reference-year": "publication_year"}, inplace=True)
tycho_corpus.rename(columns={"autor": "author", "titulo": "title"}, inplace=True)
colonia_corpus.rename(columns={"Author": "author", "Title": "title"}, inplace=True)

# remove rows with NA values in author column
eltec_corpus = eltec_corpus.dropna(subset=["author-name"])
eltec_corpus["author"] = [str(author).split(", ")[1] + " " + str(author).split(", ")[0] for author in eltec_corpus["author-name"]]

def get_similar_titles(corpus1, corpus2):
    similar_titles = []
    for _, entries1 in corpus1.iterrows():
        for id, entries2 in corpus2.iterrows():
            
            title1 = entries1["title"]
            title2 = entries2["title"]
            author1 = entries1["author"]
            author2 = entries2["author"]
            
            similarity_t = SequenceMatcher(None, title1, title2).ratio()
            similarity_a = SequenceMatcher(None, author1, author2).ratio()
            
            if similarity_t > 0.75 and similarity_a > 0.75:
                similar_titles.append(title1)
                corpus2.loc[id, "title"] = title1
                corpus2.loc[id, "author"] = author1
                break
                
    return similar_titles

similar_titles = get_similar_titles(pportal_corpus, eltec_corpus)
print("Similar titles between PPORTAL and ELTeC:", len(similar_titles), (len(eltec_corpus)-len(similar_titles)))

merged_corpus = pd.merge(pportal_corpus, eltec_corpus[["title", "author", "author_gender", "publication_year", "corpus"]], on=["title", "author"], how="outer")

similar_titles = get_similar_titles(merged_corpus, tycho_corpus)
print("Similar titles between PPORTAL and Tycho:", len(similar_titles), (len(tycho_corpus)-len(similar_titles)))

merged_corpus = pd.merge(merged_corpus, tycho_corpus[["title", "author", "corpus"]], on=["title", "author"], how="outer")

similar_titles = get_similar_titles(merged_corpus, colonia_corpus)
print("Similar titles between PPORTAL and Colonia:", len(similar_titles), (len(colonia_corpus)-len(similar_titles)))

merged_corpus = pd.merge(merged_corpus, colonia_corpus[["title", "author", "corpus"]], on=["title", "author"], how="outer")

similar_titles = get_similar_titles(merged_corpus, obras_corpus)
print("Similar titles between PPORTAL and Obras:", len(similar_titles), (len(obras_corpus)-len(similar_titles)))

merged_corpus = pd.merge(merged_corpus, obras_corpus[["title", "author", "corpus"]], on=["title", "author"], how="outer")

print("Total number of entries in PPORTAL:", len(merged_corpus))
merged_corpus.to_csv("../data/merged_corpus.csv", sep="\t", index=False, encoding="utf-8")