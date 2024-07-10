import torch
from transformers import BertTokenizer, BertForTokenClassification
from torchcrf import CRF

# Load the BERT tokenizer and model
MODEL_PATH = '../data/models/litbert-crf'
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForTokenClassification.from_pretrained(MODEL_PATH)
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
        person_entities.extend([entity for entity in entities if entity['entity'] == 'PERSON'])

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
    current_tag = None

    for token, tag in zip(tokens, tags):
        tag_name = model.config.id2label[tag]
        if tag_name.startswith('B-'):
            if entity:
                entities.append(entity)
                entity = {}
            entity['entity'] = tag_name[2:]
            entity['text'] = token
        elif tag_name.startswith('I-') and entity:
            if entity['entity'] == tag_name[2:]:
                entity['text'] += ' ' + token
        else:
            if entity:
                entities.append(entity)
                entity = {}

    if entity:
        entities.append(entity)

    return entities