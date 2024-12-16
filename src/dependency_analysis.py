import re
import json
import spacy
import pandas as pd

from itertools import chain
from utils import depend

# Load NLP model
nlp = spacy.load("pt_core_news_sm", exclude=['ner', 'textcat'])

# Constants for dictionary paths
BD_DICT = "../data/dictionaries/parte_corpo_humano.json"
LEXICON = "../data/dictionaries/lexicon.csv"

# Load external resources
pch_dict = json.load(open(BD_DICT, "r", encoding="utf-8"))
lexicons = pd.read_csv(LEXICON, sep="\t", encoding="utf-8")
lexicons_dict = dict(zip(lexicons["lexico"], lexicons["category"]))

def analyze_dependencies(entities):
    """
    Analyze syntactic dependencies for entities in their excerpts.

    Args:
        entities (list): List of entities with their excerpts and other metadata.

    Returns:
        list: Entities with updated dependency and PCH (body part) information.
    """

    for entity in entities:
        excerpt = entity.get("excerpt")
        person = entity.get("entity")
        
        if not excerpt or not person:
            continue
        
        # Handle large excerpts
        nlp.max_length = len(excerpt)
        doc = nlp(excerpt)
        
        # Analyze PCH (body part) occurrences
        pch_occurrences = get_pch_occurrences(excerpt, pch_dict)
        pch_list = list(chain.from_iterable([v["syns"] for v in pch_occurrences.values()]))
        entity["pch_occurrences"] = pch_occurrences if pch_occurrences else None
        
        # Extract dependencies
        dep = depend.get_dependencies_for_noun(doc, person)
        if dep:
            process_dependencies(doc, dep, pch_list)
        entity["dependencies"] = dep
        
    return entities

def process_dependencies(doc, dependencies, pch_list):
    """
    Process dependencies by categorizing and detecting PCH-related ones.

    Args:
        dependencies (list): List of dependency dictionaries.
        pch_list (list): List of PCH synonyms.

    Returns:
        None (updates dependencies in-place).
    """
    for dep in dependencies:
        # Categorize based on lexicon
        category_h = lexicons_dict.get(dep["lemma_h"], None)
        category_c = lexicons_dict.get(dep["lemma_c"], None)
        categories = [category for category in [category_h, category_c] if category]
        dep["categories"] = categories
        
        # Detect PCH-related dependencies
        if dep["head"] in pch_list or dep["child"] in pch_list:
            pch_dep = depend.get_dependencies_for_noun(doc,
                dep["head"] if dep["head"] in pch_list else dep['child']
            )
            dep["pch_dependencies"] = pch_dep    
    
    
def get_pch_occurrences(text, syn_list):
    """
    Detect occurrences of PCH terms in text.

    Args:
        text (str): The input text.
        syn_list (dict): Dictionary of PCH terms and their synonyms.

    Returns:
        dict: Dictionary with PCH terms and their occurrences.
    """
    pchs_occurrences = {}
    for pch, syns in syn_list.items():
        # Precompile regex for all synonyms
        pattern = re.compile(rf"(?:\s|^)({'|'.join(map(re.escape, [pch] + syns))})(?:\s|$)", flags=re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            pchs_occurrences[pch] = {
                "syns": syns,
                "occurrences": [m.strip().replace("\n", "") for m in matches],
                "occurrences_n": len(matches),
            }
    return pchs_occurrences

# if __name__ == '__main__':
#     entities = [
#         {
#             "excerpt": "O homem forte caiu. O rato roeu a roupa do Rei de Roma. Ela pode ser enganosa. Cheiram também aos olhos de ressaca de Capitu. Capitu possui olhos de cigana e dissimulada.",
#             "entity": "Capitu"
#         },
#         {
#             "excerpt": "O homem forte caiu. O rato roeu a roupa do Rei de Roma. Ela pode ser enganosa. Cheiram também aos olhos de ressaca de Capitu. Capitu possui olhos de cigana e dissimulada.",
#             "entity": "O homem"
#         },
#         {
#             "excerpt": "A minha mãe é muito bonita e cheirosa.",
#             "entity": "A minha mãe"
#         }
        
#     ]
#     entities = analyze_dependencies(entities)
#     print("\n\n\n")
#     print(entities)