import re
import json
import spacy
import pandas as pd

from itertools import chain

nlp = spacy.load("pt_core_news_lg")
BD_DICT = './data/dictionaries/parte_corpo_humano.json'
LEXICON = './data/dictionaries/lexicon.csv'
pch_dict = json.load(open(BD_DICT, 'r', encoding='utf-8'))
lexicons = pd.read_csv(LEXICON, sep='\t', encoding='utf-8')
lexicons_dict = dict(zip(lexicons['lexico'], lexicons['category']))

def analyze_dependencies(entities):

    for entity in entities:
        excerpt = entity['excerpt']
        person = entity['person']
        
        pch_occurrences = get_pch_occurrences(excerpt, pch_dict)
        pch_list = list(chain.from_iterable([v['syns'] for k, v in pch_occurrences.items()]))
        entity['pch_occurrences'] = pch_occurrences if pch_occurrences else None
        
        dep = get_dependencies_for_noun(excerpt, person)
        if dep:
            for d in dep:
                category_h = lexicons_dict.get(d['lemma_h'], None)
                category_c = lexicons_dict.get(d['lemma_c'], None)
                categories = [category_h, category_c]
                categories = [i for i in categories if i] # Remove None values                
                d['categories'] = categories
                
                pch_dep = []
                if d['head'] in pch_list or d['child'] in pch_list:
                    pch_dep = get_dependencies_for_noun(excerpt, d['head']) if d['head'] in pch_list else get_dependencies_for_noun(excerpt, d['child']) 
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

def get_dependencies_for_noun(text, noun):
       
    doc = nlp(text)
    doc = merge_phrases(doc)    
    dependencies = []
    
    for token in doc:
        if (noun in token.text or noun in token.head.text) and (token.pos_ == "NOUN" or token.pos_ == "PROPN") and (token.head.pos_ == "VERB" or token.head.pos_ == "AUX"):
            dependencies.append({
                "head": token.head.text,
                "child": token.text,
                "dep_h": token.head.dep_,
                "pos_h": token.head.pos_,
                "lemma_h": token.head.lemma_,
                "dep_c": token.dep_,
                "pos_c": token.pos_,
                "lemma_c": token.lemma_
            })
        
        if (token.pos_ == "NOUN" or token.pos_ == "PROPN"):
            # Direct Dependencies
            for child in token.children:
                if child.pos_ == "ADJ" and (noun in token.text or noun in child.text):             
                    dependencies.append({
                        "head": token.text,
                        "child": child.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": child.dep_,
                        "pos_c": child.pos_,
                        "lemma_c": child.lemma_
                    })
                if (child.pos_ == "NOUN" or child.pos_ == "PROPN") and (noun in token.text or noun in child.text):                    
                    dependencies.append({
                        "head": token.text,
                        "child": child.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": child.dep_,
                        "pos_c": child.pos_,
                        "lemma_c": child.lemma_
                    })
            
            # Broader Relations through ancestors
            for ancestor in token.ancestors:
                if ancestor.pos_ == "ADJ" and (noun in token.text or noun in ancestor.text):                          
                    dependencies.append({
                        "head": token.text,
                        "child": ancestor.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": ancestor.dep_,
                        "pos_c": ancestor.pos_,
                        "lemma_c": ancestor.lemma_
                    })
                if (ancestor.pos_ == "NOUN" or ancestor.pos_ == "PROPN") and (noun in token.text or noun in ancestor.text):                    
                    dependencies.append({
                        "head": token.text,
                        "child": ancestor.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": ancestor.dep_,
                        "pos_c": ancestor.pos_,
                        "lemma_c": ancestor.lemma_
                    })
    
    return dependencies
    
    
def merge_phrases(doc):
    with doc.retokenize() as retokenizer:
        for np in list(doc.noun_chunks):
            tokens_to_merge = [token for token in np if token.dep_ != "amod"]
            
            if tokens_to_merge:
                span = doc[tokens_to_merge[0].i : tokens_to_merge[-1].i + 1]
                attrs = {
                    "tag": span.root.tag_,
                    "lemma": span.root.lemma_,
                    "ent_type": span.root.ent_type_,
                }
                retokenizer.merge(span, attrs=attrs)
    return doc

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