import re
import numpy as np
import pandas as pd
import scipy.stats as stats

ATTRIBUTES =['adjectives', 'categories', 'pch_occurrences']
ADJ = './data/dictionaries/adjectives.txt'
with open(ADJ, 'r', encoding='utf-8') as f:
    adjectives = f.read().splitlines()

def calculate_gender_skewness(entities, output_folder):
    
    # Calculate the occurrences of each attribute
    gender_dict = calculate_occurrences(entities)
    
    # Calculate the total number of words associated with each
    gender_total = get_gender_total(gender_dict)
    save_csv(gender_total, output_folder + '/gender_total.csv', index_name='gender')
    
    # Calculate the overall statistics
    overall_stats = get_overall_stats(gender_dict)
    save_csv(overall_stats, output_folder + '/overall_stats.csv', index_name='gender')
    
    # Calculate the gender skewness for pch_occurrences
    pch_occurrences = get_pch_occurrences(gender_dict)
    pch_occurrences = get_gender_skewness(pch_occurrences)
    save_csv(pch_occurrences, output_folder + '/pch_occurrences.csv')
    
    # Calculate the gender skewness for adjectives
    adj_occurrences = get_topic_occurrences(gender_dict, 'adjectives')
    adj_occurrences = get_gender_skewness(adj_occurrences)
    save_csv(adj_occurrences, output_folder + '/adjectives.csv')
    
    # Calculate the gender skewness for categories
    cat_occurrences = get_topic_occurrences(gender_dict, 'categories')
    cat_occurrences = get_gender_skewness(cat_occurrences)
    save_csv(cat_occurrences, output_folder + '/categories.csv')
    
    return gender_dict
        

def get_gender_skewness(data, threshold=10):
    total_f, total_m = calculate_total_topic(data)
    for word, items in data.items():    
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
    chi2, p_value = stats.chi2_contingency(observed)[:2]  # retrieve only chi2 and p-value
    
    return skewness, pct_f, pct_m, chi2, p_value
 
def get_topic_occurrences(data, topic):
    topic_dict = {}
    for gender, items in data.items():
        topics = items[topic]
        for t in topics:
            t = preprocessing(t)
            if t == None:
                continue
            if t in topic_dict:                    
                topic_dict[t][gender] += 1
                topic_dict[t]["total"] += 1
            else:                    
                topic_dict[t] = {
                    "female": 0,
                    "male": 0,
                    "total": 0
                }                    
                topic_dict[t][gender] = 1
                topic_dict[t]["total"] = 1
    return topic_dict
 
 
def get_pch_occurrences(data):
    pch_dict = {}
    for gender, items in data.items():
        pch_occurrences = items['pch_occurrences']
        for pch, count in pch_occurrences.items():
            if pch in pch_dict:                    
                pch_dict[pch][gender] += count
                pch_dict[pch]["total"] += count
            else:                    
                pch_dict[pch] = {
                    "female": 0,
                    "male": 0,
                    "total": 0
                }                    
                pch_dict[pch][gender] = count
                pch_dict[pch]["total"] = count
    return pch_dict 

def get_overall_stats(data, attributes=ATTRIBUTES):
    overall_stats = {
        "female": {},
        "male": {}
    }
    for gender, items in data.items(): 
        items = {k: v for k, v in items.items() if k in attributes}
        for attribute, values in items.items():
            if gender in overall_stats:
                if attribute in overall_stats[gender]:
                    overall_stats[gender][attribute] += len(values)
                else:
                    overall_stats[gender][attribute] = len(values)
    return overall_stats

def calculate_total_topic(data):
    total_f = 0
    total_m = 0
    for _, items in data.items():
        total_f += items["female"]
        total_m += items["male"]
    return total_f, total_m

def get_gender_total(data):
    gender_dict = {
        "female": {"valor": 0},
        "male": {"valor": 0},
        "total": {"valor": 0}
    }
    for gender, items in data.items():     
        if gender in gender_dict:
            gender_dict[gender]["valor"] += items["total"]
        else:
            gender_dict[gender]["valor"] = items["total"]
    gender_dict['total']["valor"] = gender_dict['female']["valor"] + gender_dict['male']["valor"]
    return gender_dict

 
def calculate_occurrences(entities):    
    gender_dict = initiate_dict()        
    for entity in entities:        
        person = entity['person']
        gender = entity['gender'].lower()
        gender_dict[gender]['total'] += 1
        
        # Get the occurrences of each PCH
        pch_occurrences = entity.get('pch_occurrences', {})
        if pch_occurrences:
            for pch in pch_occurrences:
                occurrences = pch_occurrences[pch]
                # initialize the key if it does not exist
                if pch not in gender_dict[gender]['pch_occurrences']:
                    gender_dict[gender]['pch_occurrences'].update({pch: 0})
                gender_dict[gender]['pch_occurrences'][pch] += occurrences['occurrences_n']
        
        # Get the dependencies of the entities
        dependencies = entity.get('dependencies', [])
        if dependencies:
            for dependency in dependencies:
                noun = dependency['noun']
                dep = dependency['dependencies']
                for d in dep:
                    gender_dict[gender]['lemmas'].append(d['lemma'].lower())
                    if d['pos'] == 'ADJ' and noun == person and d['lemma'].lower() in adjectives:
                        gender_dict[gender]['adjectives'].append(d['lemma'].lower())
                    if 'category' in d:
                        gender_dict[gender]['categories'].append(d['category'])
    return gender_dict

def initiate_dict(attributes=ATTRIBUTES):
    res_dict = {
        'male': {
            'total': 0,
            'lemmas': []
        }, 
        'female': {
            'total': 0,
            'lemmas': []
        }, 
    }   
     
    for attribute in attributes:
        
        if attribute == 'pch_occurrences':
            res_dict['male']['pch_occurrences'] = {}
            res_dict['female']['pch_occurrences'] = {}
        else:
            res_dict['male'][attribute] = []
            res_dict['female'][attribute] = []
    
    return res_dict

def preprocessing(word):
    # remove words with less than 4 characters
    if len(word) < 4:
        return None    
    # remove quotes
    word = word.replace('"', '')
    # remove numbers
    word = re.sub(r'\d+', '', word)
    # remove punctuation
    word = re.sub(r'[^\w\s]', '', word)    
    return word

def save_csv(data, filename, index_name='word'):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = index_name
    df.to_csv(filename, encoding='utf-8', sep='\t')
    
    