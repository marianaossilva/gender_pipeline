import torch

from TorchCRF import CRF
from src.utils.tag_encoder import NERTagsEncoder
from transformers import BertTokenizer, BertForTokenClassification

# Load the BERT tokenizer and model
MODEL_NAME = 'marianaossilva/LitBERT-CRF'
CLASSES_PATH = './data/models/litbert-crf/classes-selective.txt'
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME, do_lower_case=False)
tag_encoder = NERTagsEncoder.from_labels_file(CLASSES_PATH, scheme='BIO')

model = BertForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=tag_encoder.num_labels,
    output_hidden_states=True)
crf = CRF(model.config.num_labels, batch_first=True)

def extract_person_entities(sentences):
    """
    Extract PERSON entities from preprocessed sentences, using the NER model.

    Args:
        sentences (List[str]): The preprocessed sentences.

    Returns:
        List[str]: A list of PERSON entities.
    """
    person_entities = []

    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        input_tensor = torch.tensor([input_ids])

        with torch.no_grad():
            emissions = model(input_tensor).logits
            tags = crf.decode(emissions)
        
        entities = decode_entities(tokens, tags[0])
        person_entities.extend([entity for entity in entities if entity['entity'] == 'PESSOA'])

    return person_entities

def decode_entities(tokens, tags):
    """
    Decode the entities from the tokens and tags.

    Args:
        tokens (List[str]): The tokenized text.
        tags (List[int]): The predicted tags from the NER model.

    Returns:
        List[Dict]: A list of entities with their type and text.
    """
    entities = []
    entity = {}

    for token, tag in zip(tokens, tags):
        tag_name = tag_encoder.convert_ids_to_tags([tag])[0]
        
        if tag_name.startswith('B-'):
            if entity:
                entities.append(entity)
                entity = {}
            entity['entity'] = tag_name[2:]
            entity['person'] = token
        elif tag_name.startswith('I-') and entity:
           if entity['entity'] == tag_name[2:]:
               entity['person'] += ' ' + token
        else:
            if entity:
                entities.append(entity)
                entity = {}
        
    if entity:        
        entities.append(entity)

    return entities