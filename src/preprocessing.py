import re
import spacy
import string

# Load the Portuguese language model
nlp = spacy.load('pt_core_news_lg')

noisy_headers = [
    "<voluntario@futuro.usp.br>", 
    "<bibvirt@futuro.usp.br> e saiba como isso é possível.", 
    "<http://www.bibvirt.futuro.usp.br>", 
    "LITERATURA BRASILEIRA Textos literários em meio eletrônico"
]

def preprocess_text(text):
    """
    Preprocesses a text by removing extra spaces, noise, special characters, emails, websites and multiple dots.

    Args:
        text (str): The raw text to be preprocessed.

    Returns:
        List[str]: A list of preprocessed and tokenized sentences.
    """
    
    # Clean the text
    text = clean_text(text)
    
    # Tokenize and segment into sentences
    sentences = sentencer(text)
    
    return sentences

def clean_text(text):
    """
    Cleans a text by removing extra spaces, noise, special characters, emails, websites and multiple dots.

    Args:
        text (str): The raw text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    
    # Remove extra spaces, tabs and breaklines
    text = re.sub(r'\s+|\t+|\n+', ' ', text)
    
    # Remove noisy headers
    for header in noisy_headers:
        if header in text:
            text = text.split(header)[1]
            break
       
    # Remove special characters (except hyphens, punctuation and breaklines)
    text = re.sub(r"[^\w\s\-\n'{}]+".format(re.escape(string.punctuation)), '', text)
    
    # Remove multiple dots followed by a space or a number or a capital letter
    text = re.sub(r'\.{4,}(?:.+)\n', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove websites
    text = re.sub(r'http\S+|www\S+', '', text)
    
    return text

def sentencer(text):
    """
    Segments a text into sentences using the Spacy sentencer.

    Args:
        text (str): The text to be segmented into sentences.

    Returns:
        List[str]: A list of segmented sentences.
    """
    
    # Create a Spacy document
    doc = nlp(text)
    
    # Extract the sentences
    sentences = [sent.text for sent in doc.sents]
    
    return sentences

def remove_noisy_headers(text):
    """
    Removes noisy headers from a text.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """    
    
    if "<voluntario@futuro.usp.br>" in text:
        return text.split("<voluntario@futuro.usp.br>")[1]
    if "<bibvirt@futuro.usp.br> e saiba como isso é possível." in text:
        return text.split("<bibvirt@futuro.usp.br> e saiba como isso é possível.")[1]
    if "<http://www.bibvirt.futuro.usp.br>" in text:
        return text.split("<http://www.bibvirt.futuro.usp.br>")[1]
    if "LITERATURA BRASILEIRA Textos literários em meio eletrônico" in text:
        return text.split("LITERATURA BRASILEIRA Textos literários em meio eletrônico")[1]
    return text