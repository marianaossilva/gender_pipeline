from itertools import islice

def segment_excerpts(texts):
    
    sentences = texts['sentences']    
    text = ' '.join(sentences)
    
    # Calculate the range of each sentence
    ranges = get_sentence_ranges(sentences, text)
    
    # Get the positions of each entity in the text
    entities = texts['entities']
    entities = get_entity_positions(entities, text)
    
    # Get the excerpts for each entity
    excerpts = get_entity_excerpts(entities, ranges, text)
    
    return excerpts

def get_sentence_ranges(sentences, text, max_range_length=10000):
    ranges = []
    for sentence in window(sentences, n=3):
        start = text.find(sentence[0])
        end = text.find(sentence[-1]) + len(sentence[-1])
        if end - start > max_range_length:
            end = text.find(sentence[1]) + len(sentence[1]) if len(sentence) > 1 else end
        if end - start > max_range_length:
            end = start + len(sentence[0])
        ranges.append((start, end))
    return ranges

def get_entity_positions(entities, text):
    for entity in entities:
        sentence = entity['sentence']
        start = sentence.find(entity['entity'])
        end = start + len(entity['entity'])
        
        #Update the start and end positions to the text
        start_sentence = text.find(sentence)
        start += start_sentence
        end += start_sentence
        
        entity['start_char'] = start
        entity['end_char'] = end
        entity['excerpt'] = ''
    return entities

def get_entity_excerpts(entities, ranges, text):
    for entity in entities:
        start = entity['start_char']
        end = entity['end_char']
        for s, e in ranges:
            if start >= s and end <= e:
                entity['excerpt'] = text[s:e]
                break
    return entities

def window(seq, n=2):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result