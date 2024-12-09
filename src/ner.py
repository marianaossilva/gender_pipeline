import torch
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from torchcrf import CRF
from utils.tag_encoder import NERTagsEncoder
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertTokenizer, BertForTokenClassification

CLASSES_PATH = '../data/dictionaries/classes-selective.txt'
tag_encoder = NERTagsEncoder.from_labels_file(CLASSES_PATH, scheme='BIO')

class NERModelCache:
    _model = None
    _tokenizer = None
    _crf = None
    _device = None

    @classmethod
    def get_model_and_tokenizer(cls):
        if cls._model is None:
            cls._load_model_and_tokenizer()
        return cls._model, cls._tokenizer, cls._crf, cls._device

    @classmethod
    def _load_model_and_tokenizer(cls):

        cls._tokenizer = BertTokenizer.from_pretrained('../data/models/ft_bert_crf', do_lower_case=False)
        cls._model = BertForTokenClassification.from_pretrained('../data/models/ft_bert_crf')
        # cls._model = BertForTokenClassification.from_pretrained('marianaossilva/LitBERT-CRF')
        cls._crf = CRF(cls._model.config.num_labels, batch_first=True)
        cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        cls._model.to(cls._device)
        cls._crf.to(cls._device)

def extract_person_entities(texts):
    """
    Extract PERSON entities from preprocessed sentences, using the NER model.

    Args:
        texts (Dict): Dictionary containing the sentences.
        batch_size (int): Number of sentences to process in one batch.

    Returns:
        Dict: Updated dictionary with PERSON entities.
    """
    
    model, tokenizer, crf, device = NERModelCache.get_model_and_tokenizer()
    person_entities = []
    sentences = texts.get("sentences", [])
    # get sample of sentences
    # sentences = sentences[:50]
    
    if not sentences:
        texts["entities"] = person_entities
        return texts  # Return if no sentences are provided
    
    for sentence in sentences:
    
        # Tokenize the sentence
        encoding = tokenizer(sentence, truncation=True, padding=True, return_tensors="pt", max_length=512)
        input_ids = encoding["input_ids"]
        input_tensor = input_ids.to(device)
        attention_mask = encoding["attention_mask"].to(device)
        
        # Run the model to get the NER tag predictions
        with torch.no_grad():
            emissions = model(input_tensor, attention_mask=attention_mask).logits
            tags = crf.decode(emissions)
            tags = tags[0][1:-1]  # Remove [CLS] and [SEP] tokens

        # Decode the entities
        tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze(), skip_special_tokens=True)
        entities = decode_entities(tokens, tags)
            
        for entity in entities:
            if entity['class'] == 'PESSOA' and (len(entity['entity']) > 2 and entity['entity'].lower() not in ['eu', 'ele', 'ela', 'eles', 'elas']):
                entity['sentence'] = sentence
                person_entities.append(entity)
    
    texts["entities"] = person_entities
    return texts

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

        if tag_name.startswith('B-'):  # Beginning of a new entity
            if entity:  # Append the previous entity
                entities.append(entity)
            entity = {'class': tag_name[2:], 'entity': token[2:] if token.startswith("##") else token}  # Initialize a new entity

        elif tag_name.startswith('I-') and entity and entity['class'] == tag_name[2:]:
            
            if token.startswith("##"):
                entity['entity'] += token[2:]
            else:
                entity['entity'] += f" {token}"

        else:  # Outside an entity or mismatched continuation
            if entity:  # Append the completed entity
                entities.append(entity)
                entity = None

    if entity:  # Add the last entity
        entities.append(entity)

    return entities