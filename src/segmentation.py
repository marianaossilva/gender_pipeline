from itertools import islice

def segment_excerpts(sentences, entities):
    
    # Calculate the range of each sentence
    ranges = get_sentence_ranges(sentences)
    
    # Get the excerpts for each entity
    excerpts = get_entity_excerpts(entities, ranges, sentences)
    
    return excerpts

def get_sentence_ranges(sentences):
    ranges = []
    text = ' '.join(sentences)    
    for sentence in window(sentences, n=3):
        start = text.find(sentence[0])
        end = text.find(sentence[-1]) + len(sentence[-1])
        if end - start > 10000:
            end = text.find(sentence[1]) + len(sentence[1])        
        if end - start > 10000:
            end = text.find(sentence[0]) + len(sentence[0])
        ranges.append((start, end))
    return ranges

def get_entity_excerpts(entities, ranges, sentences):
    excerpts = []
    text = ' '.join(sentences)
    for entity in entities:
        start = entity['start_char']
        end = entity['end_char']
        for s, e in ranges:
            if start >= s and end <= e:
                excerpt = text[s:e]
                excerpts.append(excerpt)
                break
    return excerpts

def window(seq, n=2):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result