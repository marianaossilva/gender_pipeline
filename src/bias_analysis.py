
import math

from scipy.stats import chi2_contingency
from collections import Counter, defaultdict

ATTRIBUTES = ['lemmas', 'verbs', 'adjectives', 'categories', 'pchs']
ADJ_PATH = '../data/dictionaries/adjectives.txt'
VERB_PATH = '../data/dictionaries/verbs.txt'

with open(ADJ_PATH, 'r', encoding='utf-8') as f:
    ADJECTIVES = set(f.read().splitlines())

with open(VERB_PATH, 'r', encoding='utf-8') as f:
    VERBS = set(f.read().splitlines())

def bias_analysis(entities):
    
    gender_total, overall_stats, gender_dict, attr_dict = initialize_results_dict()

    for entity in entities:
        gender = entity["gender"]
        person = entity["entity"]
        gender_total[gender] += 1
        gender_dict[gender]["total"] += 1
        
        # Get the occurrences of each PCH
        pch_occurrences = entity.get('pch_occurrences', {})

        for dep in entity.get("dependencies", []):            
            process_dependency(dep, person, gender, gender_dict, overall_stats, pch_occurrences)
            
            # Compute agency scores
            agency = gender_dict[gender]["agency"]
            if agency["total"] > 0:
                score = (agency["nsubj"] - agency["dobj"]) / agency["total"]
                agency["score"].append(score)

    # Compute metrics for all attributes
    attr_dict = compute_metrics(attr_dict, gender_dict, gender_total)
    return gender_total, overall_stats, gender_dict, attr_dict

def create_gender_data():
    """Create the structure for gender-specific data."""
    return {
        "total": 0,
        "agency": defaultdict(int, {"score": []}),
        **{attribute: {"counter": Counter(), "total": 0} for attribute in ATTRIBUTES},
    }

def initialize_results_dict():
    """Initialize a results dictionary with default values."""
    gender_total = defaultdict(int)
    overall_stats = defaultdict(lambda: defaultdict(int))
    gender_dict = {gender: create_gender_data() for gender in ["male", "female", "unknown"]}
    attr_dict = {att: {} for att in ATTRIBUTES}
    return gender_total, overall_stats, gender_dict, attr_dict

def update_counters(value1, value2, attribute, gender, gender_dict, overall_stats):
    """Update counters for a specific attribute."""
    for value in [value1, value2]:
        if value:
            gender_dict[gender][attribute]["counter"][value] += 1
            gender_dict[gender][attribute]["total"] += 1
            overall_stats[attribute][gender] += 1
            
def update_categories(categories, gender, gender_dict, overall_stats):
    """Update category counters."""
    for category in categories:
        gender_dict[gender]["categories"]["counter"][category] += 1
        gender_dict[gender]["categories"]["total"] += 1
        overall_stats["categories"][gender] += 1
        
def update_pch_dependencies(pch, gender, gender_dict, overall_stats):
    """Update PCH dependency counters."""
    gender_dict[gender]["pchs"]["counter"][pch] += 1
    gender_dict[gender]["pchs"]["total"] += 1
    overall_stats["pchs"][gender] += 1
        
def update_agency(dep, gender, gender_dict):
    """Update agency counters."""
    if dep == "nsubj":
        gender_dict[gender]["agency"]["nsubj"] += 1
    elif dep == "obj":
        gender_dict[gender]["agency"]["dobj"] += 1
    gender_dict[gender]["agency"]["total"] += 1

def process_dependency(dep, person, gender, gender_dict, overall_stats, pch_occurrences):
    """Process a single dependency and update statistics."""
    update_counters(dep["lemma_h"], dep["lemma_c"], "lemmas", gender, gender_dict, overall_stats)
    update_categories(dep.get("categories", []), gender, gender_dict, overall_stats)    

    # Process dependency based on head/child relation
    if person in dep["head"]:
        if dep["pos_c"] in {"VERB", "AUX"} and dep["lemma_c"] in VERBS:
            update_counters(dep["lemma_c"], None, "verbs", gender, gender_dict, overall_stats)
        if dep["pos_c"] in "ADJ" and dep["lemma_c"] in ADJECTIVES:
            update_counters(dep["lemma_c"], None, "adjectives", gender, gender_dict, overall_stats)
        if len(dep.get('pch_dependencies', [])) > 0 and dep['lemma_c'].lower() in pch_occurrences.keys():
            update_pch_dependencies(dep["lemma_c"], gender, gender_dict, overall_stats)
        update_agency(dep["dep_h"], gender, gender_dict)
    elif person in dep["child"]:
        if dep["pos_h"] in {"VERB", "AUX"} and dep["lemma_h"] in VERBS:
            update_counters(dep["lemma_h"], None, "verbs", gender, gender_dict, overall_stats)
        if len(dep.get('pch_dependencies', [])) > 0 and dep['lemma_h'].lower() in pch_occurrences.keys():
            update_pch_dependencies(dep["lemma_h"], gender, gender_dict, overall_stats)
        update_agency(dep["dep_c"], gender, gender_dict)
        
def calculate_percentage(count, total):
    return count / total if total > 0 else 0

def calculate_skewness(pct_f, pct_m):
    return (pct_f - pct_m) / (pct_f + pct_m) if (pct_f + pct_m) > 0 else 0

def calculate_pmi(joint, marginal_x, marginal_g):
    if joint == 0 or marginal_x == 0 or marginal_g == 0:
        return 0
    return math.log(joint / (marginal_x * marginal_g))
        
def calculate_metrics(attr, attribute, total_occurrences, gender_dict, gender_total):
    """Calculate skewness, PMI, and chi-square for a given attribute."""
    total_entities = sum(gender_total.values())  # Total number of entities
    
    # Raw counts
    female_count = gender_dict["female"][attribute]["counter"].get(attr, 0)
    male_count = gender_dict["male"][attribute]["counter"].get(attr, 0)
    unknown_count = gender_dict["unknown"][attribute]["counter"].get(attr, 0)
    
    # Probabilities
    joint_f = calculate_percentage(female_count, total_entities)
    joint_m = calculate_percentage(male_count, total_entities)
    joint_u = calculate_percentage(unknown_count, total_entities)
    marginal_x = calculate_percentage(total_occurrences, total_entities)
    marginal_f = calculate_percentage(gender_total["female"], total_entities)
    marginal_m = calculate_percentage(gender_total["male"], total_entities)
    marginal_u = calculate_percentage(gender_total["unknown"], total_entities)
    
    # Calculate PMI
    pmi_f = calculate_pmi(joint_f, marginal_x, marginal_f)
    pmi_m = calculate_pmi(joint_m, marginal_x, marginal_m)
    pmi_u = calculate_pmi(joint_u, marginal_x, marginal_u)

    # Percentages and skewness
    pct_f = calculate_percentage(female_count, gender_dict["female"]["total"])
    pct_m = calculate_percentage(male_count, gender_dict["male"]["total"])
    skewness = calculate_skewness(pct_f, pct_m)

    # pmi_f = calculate_pmi(female_count, total_occurrences, gender_total["female"])
    # pmi_m = calculate_pmi(male_count, total_occurrences, gender_total["male"])
    # pmi_u = calculate_pmi(unknown_count, total_occurrences, gender_total["unknown"])

    contingency_table = [[female_count, male_count], [unknown_count, total_occurrences]]
    try:
        chi2, p_value, _, _ = chi2_contingency(contingency_table)
    except ValueError:
        chi2, p_value = 0, 0

    return {
        "female": female_count,
        "male": male_count,
        "unknown": unknown_count,
        "total": total_occurrences,
        "skewness": skewness,
        "pct_f": pct_f,
        "pct_m": pct_m,
        "chi2": chi2,
        "p_value": p_value,
        "pmi_f": pmi_f,
        "pmi_m": pmi_m,
        "pmi_u": pmi_u,
    }

def compute_metrics(attr_dict, gender_dict, gender_total):
    """Compute metrics for all attributes."""
    for attribute_type in ATTRIBUTES:
        all_attributes = sum(
            (gender_dict[gender][attribute_type]["counter"] for gender in gender_dict), Counter()
        )
        for attr, total_occurrences in all_attributes.items():
            metrics = calculate_metrics(attr, attribute_type, total_occurrences, gender_dict, gender_total)
            attr_dict[attribute_type][attr] = metrics        
    return attr_dict
