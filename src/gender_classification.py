import spacy

from utils import depend
from collections import Counter
from br_gender.base import br_gender_info

nlp = spacy.load('pt_core_news_sm', exclude=['ner', 'textcat'])

def classify_gender(entities):
    """
    Classify the gender of the entities based on the excerpts and the dependency analysis.

    Args:
        entities (dict): Dictionary with the entities extracted from the text.

    Returns:
        list: List of entities with gender classification.
    """
    
    if not entities:
        return []

    gender_dict = {}
    for entity in entities:        
        if 'entity' not in entity or 'excerpt' not in entity:
            continue
        
        person = entity['entity']
        br_gender = get_gender_br(person)
        
        if br_gender == 'unknown':
            # Aggregate excerpts for this entity
            excerpts = [e['excerpt'] for e in entities if e['entity'].lower() == person.lower()]
            entity['gender'] = get_dependency_gender(person, excerpts, gender_dict)
        else:
            entity['gender'] = br_gender

    return entities

def get_gender_br(name):
    first_name = name.split(' ')[0]
    try:
        gender = br_gender_info.get_gender(first_name).lower()
    except Exception as e:
        print(f"Warning: Failed to get gender for name '{first_name}' - {e}")
        gender = 'unknown'
    
    return 'unknown' if gender in ['unk', 'unisex'] else gender

def get_dependency_gender(person, excerpts, gender_dict): 
    
    gender_list = []
    person_key = person.lower()
    
    if person_key not in gender_dict:
        processed_excerpts = {}
        
        for excerpt in excerpts:
            if excerpt not in processed_excerpts:
                nlp.max_length = len(excerpt)
                doc = nlp(excerpt)
                processed_excerpts[excerpt] = depend.get_gendered_for_entity(doc, person)
            gender_list.append(processed_excerpts[excerpt])
        
        if len(person.split(' ')) > 1:  # Analyze nested entities (e.g., full names)
            nlp.max_length = len(person)
            doc = nlp(person)
            gender_list.append(depend.get_gendered_for_nested_entity(doc))
                    
        # Determine majority gender or fallback to unknown
        if gender_list:
            gender = Counter(gender_list).most_common(1)[0][0]
            gender_dict[person_key] = gender
            return gender
        else:
            return 'unknown'
    else:
        return gender_dict[person_key]