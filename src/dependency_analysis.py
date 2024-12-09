import re
import json
import spacy
import pandas as pd

from itertools import chain
from utils import depend

nlp = spacy.load("pt_core_news_sm", exclude=['ner', 'textcat'])
BD_DICT = '../data/dictionaries/parte_corpo_humano.json'
LEXICON = '../data/dictionaries/lexicon.csv'
pch_dict = json.load(open(BD_DICT, 'r', encoding='utf-8'))
lexicons = pd.read_csv(LEXICON, sep='\t', encoding='utf-8')
lexicons_dict = dict(zip(lexicons['lexico'], lexicons['category']))

def analyze_dependencies(entities):

    for entity in entities:
        excerpt = entity['excerpt']
        person = entity['entity']
        nlp.max_length = len(excerpt)
        doc = nlp(excerpt)
        
        pch_occurrences = get_pch_occurrences(excerpt, pch_dict)
        pch_list = list(chain.from_iterable([v['syns'] for _, v in pch_occurrences.items()]))
        entity['pch_occurrences'] = pch_occurrences if pch_occurrences else None
        
        dep = depend.get_dependencies_for_noun(doc, person)
        if dep:
            for d in dep:
                category_h = lexicons_dict.get(d['lemma_h'], None)
                category_c = lexicons_dict.get(d['lemma_c'], None)
                categories = [category_h, category_c]
                categories = [i for i in categories if i] # Remove None values                
                d['categories'] = categories
                
                pch_dep = []
                if d['head'] in pch_list or d['child'] in pch_list:
                    pch_dep = depend.get_dependencies_for_noun(doc, d['head']) if d['head'] in pch_list else depend.get_dependencies_for_noun(doc, d['child']) 
                d['pch_dependencies'] = pch_dep
        
        entity['dependencies'] = dep
    return entities

def get_pch_occurrences(text, syn_list):
    pchs_occurrences = {}
    for pch, syns in syn_list.items():
        syns_list = list(set([pch] + syns))
        matches = []
        for syn in syns_list:
            matches += re.findall(fr'(?:\s|^){syn}(?:\s|)', text, flags=re.IGNORECASE)
        matches = [i.strip() for i in matches]
        matches = [i.replace('\n', '') for i in matches]
        if matches:
            pchs_occurrences[pch] = {
                'syns': syns,
                'occurrences': matches,
                'occurrences_n': len(matches)
            }
    return pchs_occurrences

# if __name__ == '__main__':
#     entities = [
#         {
#             "excerpt": "O homem forte caiu. O rato roeu a roupa do Rei de Roma. Ela pode ser enganosa. Cheiram também aos olhos de ressaca de Capitu. Capitu possui olhos de cigana e dissimulada.",
#             "person": "Capitu"
#         },
#         {
#             "excerpt": "O homem forte caiu. O rato roeu a roupa do Rei de Roma. Ela pode ser enganosa. Cheiram também aos olhos de ressaca de Capitu. Capitu possui olhos de cigana e dissimulada.",
#             "person": "O homem"
#         },
#         {
#             "excerpt": "A minha mãe é muito bonita e cheirosa.",
#             "person": "A minha mãe"
#         }
        
#     ]
#     entities = analyze_dependencies(entities)
#     print("\n\n\n")
#     print(entities)