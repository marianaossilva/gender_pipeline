import re
import json
import spacy
import pandas as pd

from itertools import chain
from difflib import SequenceMatcher

dep = ['ROOT', 'conj']
nlp = spacy.load("pt_core_news_lg")
BD_DICT = './data/dictionaries/parte_corpo_humano.json'
LEXICON = './data/dictionaries/lexicon.csv'
pch_dict = json.load(open(BD_DICT, 'r', encoding='utf-8'))
lexicons = pd.read_csv(LEXICON, sep='\t', encoding='utf-8')
lexicons_dict = dict(zip(lexicons['lexico'], lexicons['category']))

def analyze_dependencies(entities):
    """
    Analyze the dependencies of the entities extracted from the text.

    Args:
        entities (dict): Dictionary with the entities extracted from the text.

    Returns:
        dict: Dictionary with the entities and their dependencies.
    """
    for entity in entities:
        excerpt = entity['excerpt']
        person = entity['person']
        
        pch_occurrences = get_pch_occurrences(excerpt, pch_dict)
        entity['pch_occurrences'] = pch_occurrences if pch_occurrences else None
        nouns = [person]
        nouns.extend(chain(*[occurrences["occurrences"] for _, occurrences in pch_occurrences.items()]))
        
        dependencies = []
        for noun in nouns:                    
            dep = get_dependencies_for_noun(excerpt, noun)             
            if dep:                
                for d in dep:
                    try:
                        category = lexicons_dict[d['lemma']]
                    except KeyError:
                        continue
                    d['category'] = category   
                
                dependencies.append({
                    "noun": noun,
                    "dependencies": dep
                })

        entity['dependencies'] = dependencies
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
    # if the noun is a phrase, get the root of the phrase
    if len(noun.split(" ")) > 1:
        doc = nlp(noun)
        # get the root of the noun
        for tok in doc.to_json()["tokens"]:
            if tok["dep"] == "ROOT":
                noun = noun[tok["start"]:tok["end"]]
                break
        
    doc = nlp(text)
    tok_l = doc.to_json()["tokens"]
    
    head = None
    for tok in tok_l:
        if text[tok["start"]:tok["end"]] == noun or SequenceMatcher(None, text[tok["start"]:tok["end"]], noun).ratio() >= 0.7:
                head = tok["head"]
                break
    
    if head is None:
        return None
    else:
        dependencies = []
        for tok in tok_l:
            if tok["head"] == head and tok["dep"] in ["nsubj", "amod", "conj", "appos"]:
                dependencies.append({
                    "id": tok["id"],
                    "head": tok["head"],
                    "text": text[tok["start"]:tok["end"]],
                    "dep": tok["dep"],
                    "pos": tok["pos"],
                    "lemma": tok["lemma"]
                })
        
        aux = dependencies.copy()
        for tok in tok_l:
            for dep in aux:
                if tok["head"] == dep["id"] and tok["dep"] in ["nsubj", "amod", "conj", "appos"]:
                    dependencies.append({
                        "id": tok["id"],
                        "head": tok["head"],
                        "text": text[tok["start"]:tok["end"]],
                        "dep": tok["dep"],
                        "pos": tok["pos"],
                        "lemma": tok["lemma"]
                    })
            
        return dependencies         