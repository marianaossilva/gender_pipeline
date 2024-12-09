
import math
import numpy as np
import scipy.stats as stats

from collections import Counter

ATTRIBUTES=['lemmas', 'verbs', 'adjectives', 'categories', 'pchs']
ADJ = '../data/dictionaries/adjectives.txt'
with open(ADJ, 'r', encoding='utf-8') as f:
    adjectives = f.read().splitlines()

def bias_analysis(entities):
    
    # Calculate the occurrences of each attribute
    gender_dict = calculate_occurrences(entities, ATTRIBUTES)
    gender_dict = get_counter(gender_dict)
    total_f, total_m = gender_dict['female']['total'], gender_dict['male']['total']
    
    # Calculate the total number of words associated with each
    gender_total = get_gender_total(gender_dict)
    
    # Calculate the overall statistics
    overall_stats = get_overall_stats(gender_dict, ATTRIBUTES)
    
    # Calculate the skewness and PMI for each attribute
    attribute_dict = {}
    for attribute in ATTRIBUTES:        
        attribute_res = get_word_occurrences(gender_dict, attribute)        
        # Calculate gender skewness
        get_gender_skewness(attribute_res, total_f, total_m)        
        # Calculate PMI
        calculate_pmi(attribute_res, total_f, total_m)
        # Save the results
        attribute_dict[attribute] = attribute_res
    
    return gender_total, overall_stats, gender_dict, attribute_dict


def get_overall_stats(data, att=[]):
    overall_stats = {
        "female": {},
        "male": {},
        "unknown": {}
    }
    for gender, items in data.items(): 
        for attribute in att:
            overall_stats[gender][attribute] = items[attribute]['total']
    return overall_stats

def get_gender_total(data):
    total_dict = {
        "female": {"total": 0},
        "male": {"total": 0},
        "unknown": {"total": 0},
        "total": {"total": 0}
    }
    for gender, items in data.items():    
        total_dict[gender]["total"] += items["total"]
        total_dict["total"]["total"] += items["total"]
    return total_dict

def get_counter(gender_dict):
    for gender, items in gender_dict.items():
        for attribute, values in items.items():
            if attribute in ATTRIBUTES:
                gender_dict[gender][attribute] = {
                    'counter': Counter(values),
                    'total': len(values)
                }               
    
    return gender_dict

def calculate_occurrences(entities, att=[]): 
       
    gender_dict = initiate_dict(att)        
    for entity in entities:        
        person = entity['entity']
        gender = entity['gender'].lower()
        gender_dict[gender]['total'] += 1
        
        # Get the occurrences of each PCH
        pch_occurrences = entity.get('pch_occurrences', {})
        
        # Get the dependencies of the entities
        dependencies = entity.get('dependencies', [])
        if dependencies:
            for d in dependencies:
                gender_dict[gender]['categories'].extend(d['categories'])
                gender_dict[gender]['lemmas'].append(d['lemma_h'].lower())
                gender_dict[gender]['lemmas'].append(d['lemma_c'].lower())
                if person in d['head']:              
                    if d['pos_c'] == 'VERB' or d['pos_c'] == 'AUX':
                        gender_dict[gender]['verbs'].append(d['lemma_c'].lower())
                    if d['pos_c'] == 'ADJ' and d['lemma_c'].lower() in adjectives:
                        gender_dict[gender]['adjectives'].append(d['lemma_c'].lower()) 
                    if d['pos_c'] != 'ADJ' and d['lemma_c'].lower() in adjectives:
                        gender_dict[gender]['adjectives'].append(d['lemma_c'].lower()) 
                    if len(d['pch_dependencies']) > 0 and d['lemma_c'].lower() in pch_occurrences.keys():
                        gender_dict[gender]['pchs'].append(d['lemma_c'].lower()) 
                    gender_dict[gender]['agency']['nsubj'] += 1 if d['dep_h'] == 'nsubj' else 0
                    gender_dict[gender]['agency']['obj'] += 1 if d['dep_h'] == 'obj' else 0
                    gender_dict[gender]['agency']['total'] += 1 if d['dep_h'] == 'nsubj' or d['dep_h'] == 'obj' else 0
                                                   
                elif person in d['child']:         
                    if d['pos_h'] == 'VERB' or d['pos_h'] == 'AUX':
                        gender_dict[gender]['verbs'].append(d['lemma_h'].lower())
                    if d['pos_h'] == 'ADJ' and d['lemma_c'].lower() in adjectives:
                        gender_dict[gender]['adjectives'].append(d['lemma_h'].lower())  
                    if d['pos_c'] != 'ADJ' and d['lemma_c'].lower() in adjectives:
                        gender_dict[gender]['adjectives'].append(d['lemma_c'].lower())   
                    if len(d['pch_dependencies']) > 0 and d['lemma_h'].lower() in pch_occurrences.keys():
                        gender_dict[gender]['pchs'].append(d['lemma_h'].lower())  
                    gender_dict[gender]['agency']['nsubj'] += 1 if d['dep_c'] == 'nsubj' else 0
                    gender_dict[gender]['agency']['obj'] += 1 if d['dep_c'] == 'obj' else 0
                    gender_dict[gender]['agency']['total'] += 1 if d['dep_c'] == 'nsubj' or d['dep_c'] == 'obj' else 0
        agency_score = get_agency_score(gender_dict, gender)
        if agency_score:
            gender_dict[gender]['agency']['score'].append(agency_score)
    return gender_dict

def initiate_dict(att=[]):
    res_dict = {
        'male': {
            'total': 0,
            'agency': {
                'nsubj': 0,
                'obj': 0,
                'total': 0,
                'score': []
            }
        }, 
        'female': {
            'total': 0,
            'agency': {
                'nsubj': 0,
                'obj': 0,
                'total': 0,
                'score': []
            }
        },
        'unknown': {
            'total': 0,
            'agency': {
                'nsubj': 0,
                'obj': 0,
                'total': 0,
                'score': []
            }
        }
    }   
     
    for attribute in att:
        res_dict['female'][attribute] = []
        res_dict['male'][attribute] = []
        res_dict['unknown'][attribute] = []
    
    return res_dict

def get_agency_score(data, gender):
    total_g = data[gender]['total']
    nsubj_g, obj_g = data[gender]['agency']['nsubj'], data[gender]['agency']['obj']
    
    p_nsubj_g = nsubj_g / total_g
    p_obj_g = obj_g / total_g
    try:
        return (p_nsubj_g-p_obj_g) / (p_nsubj_g+p_obj_g)
    except ZeroDivisionError:
        return None

def get_word_occurrences(data, attribute):
    counter_f = data['female'][attribute]['counter']
    counter_m = data['male'][attribute]['counter']    
    word_dict = {}
    for word, count in counter_f.items():
        word_dict[word] = {"female": count, "male": 0}
    
    for word, count in counter_m.items():
        if word in word_dict:
            word_dict[word]["male"] = count
        else:
            word_dict[word] = {"female": 0, "male": count}
    return word_dict

def get_gender_skewness(data, total_f, total_m, threshold=1):
    for word, items in data.items():
        data[word]["total"] = items["female"] + items["male"]
        if items["total"] > threshold:  
            word_female = items["female"]
            word_male = items["male"]
            skewness, pct_f, pct_m, chi2, p = gender_skewness(word_female, word_male, total_f, total_m)
            data[word]["skewness"] = skewness
            data[word]["pct_f"] = pct_f
            data[word]["pct_m"] = pct_m
            data[word]["chi2"] = chi2
            data[word]["p"] = p
        else:
            data[word]["skewness"] = 0
            data[word]["pct_f"] = 0
            data[word]["pct_m"] = 0
            data[word]["chi2"] = 0
            data[word]["p"] = 0
    return data

def gender_skewness(word_female, word_male, female_total, male_total):
        
    # calculate the percentages 
    pct_f = word_female / female_total
    pct_m = word_male / male_total   
    
    # calculate the skewness
    sub = pct_f - pct_m
    add = pct_f + pct_m    
    skewness = 0 if add == 0 else sub / add
    
    # prepare the data for the chi-square test
    observed = np.array([[word_female, word_male], 
                         [female_total-word_female, male_total-word_male]]) # observed frequencies
    
    # perform chi-square test for proportions
    try:
        chi2, p_value = stats.chi2_contingency(observed)[:2]  # retrieve only chi2 and p-value
    except ValueError:
        chi2, p_value = 0, 0
    return skewness, pct_f, pct_m, chi2, p_value

def calculate_pmi(data, total_f, total_m):
    for word, items in data.items():
        p_x = items["total"] / (total_f + total_m)
        p_f = total_f / (total_f + total_m)
        p_m = total_m / (total_f + total_m)
        p_f_x = items["female"] / (total_f + total_m)
        p_m_x = items["male"] / (total_f + total_m)
        
        pmi_f = pmi(p_f_x, p_f, p_x)
        pmi_m = pmi(p_m_x, p_m, p_x)
        data[word]["pmi_f"] = pmi_f
        data[word]["pmi_m"] = pmi_m
    return data

def pmi(p_g_x, p_g, p_x):
    if p_g_x > 0 and p_x > 0 and p_g > 0:
        return math.log(p_g_x / (p_g * p_x), 2)
    else:
        return -float('inf')