import spacy

from br_gender.base import br_gender_info
from difflib import SequenceMatcher

nlp = spacy.load('pt_core_news_lg')


def classify_gender(excerpts, entities):
    """
    Classify the gender of the entities based on the excerpts and the dependency analysis.

    Args:
        excerpts (list): List of excerpts.
        entities (list): List of entities.

    Returns:
        list: List of entities with gender classification.
    """
    
    try:
        doc = nlp(excerpts)
    except ValueError:
        doc = nlp(excerpts[:1000000])
    
    for entity in entities:
        person = entity['person']
        dep_gender = get_dependency_gender(doc, person, excerpts)
        br_gender = get_gender_br(person)        
        entity['gender'] = get_final_gender(dep_gender, br_gender)
    
    return entities


def get_gender_br(name):
    first_name = name.split(' ')[0]
    return br_gender_info.get_gender(first_name) if first_name[0].isupper() else 'Unk'

def get_dependency_gender(doc, person, excerpt):
    tok_l = doc.to_json()["tokens"]
    
    head = None
    for tok in tok_l:
        if excerpt[tok["start"]:tok["end"]] == person or SequenceMatcher(None, excerpt[tok["start"]:tok["end"]], person).ratio() > 0.7:
            head = tok["id"]
            break
    
    gender_list = []
    if head:
        for tok in tok_l:
            if tok["head"] == head:
                morph = tok["morph"]
                if "Gender=" in morph:
                    gender_list.append([morph.split("Gender=")[1].split("|")[0]])
    return 'Masc' if gender_list.count(['Masc']) >= gender_list.count(['Fem']) else 'Fem'
    

def get_final_gender(dp_gender, br_gender):
    if br_gender == None and dp_gender == None:
        return "Unk"    
    if (br_gender == "Unk" or br_gender == "Unisex"):
        return 'Male' if dp_gender == 'Masc' else 'Female'
    else:
        return br_gender
    
