import re
import string

# Define a set of noisy headers
NOISY_HEADERS = [
    "<voluntario@futuro.usp.br>", 
    "<bibvirt@futuro.usp.br> e saiba como isso é possível.", 
    "<http://www.bibvirt.futuro.usp.br>", 
    "LITERATURA BRASILEIRA Textos literários em meio eletrônico"
]

def preprocess_text(text, nlp):
    """
    Preprocesses a text by removing extra spaces, noise, special characters, emails, websites and multiple dots.

    Args:
        text (str): The raw text to be preprocessed.
        nlp (spacy.Language): A preloaded spaCy language model.

    Returns:
        List[str]: A list of preprocessed and tokenized sentences.
    """
    text = clean_text(text)
    sentences = segment_sentences(text, nlp)
    return sentences

def clean_text(text):
    """
    Cleans a text by removing extra spaces, noise, special characters, emails, websites and multiple dots.

    Args:
        text (str): The raw text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    
    # Remove noisy headers
    text = remove_noisy_headers(text)

    # Standardize spaces, tabs, and line breaks
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters (except punctuation and hyphens)
    text = re.sub(r"[^\w\s\-{}]+".format(re.escape(string.punctuation)), '', text)

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove websites
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove multiple dots followed by specific patterns
    text = re.sub(r'\.{4,}', '', text)

    return text

def remove_noisy_headers(text):
    """
    Removes predefined noisy headers from the text.

    Args:
        text (str): The raw text.

    Returns:
        str: Text without noisy headers.
    """
    for header in NOISY_HEADERS:
        if header in text:
            # Remove everything up to the header
            text = text.split(header, maxsplit=1)[-1]
            break
    return text

def segment_sentences(text, nlp):
    """
    Segments text into sentences using spaCy.

    Args:
        text (str): The text to segment.
        nlp (spacy.Language): A preloaded spaCy language model.

    Returns:
        List[str]: A list of segmented sentences.
    """
    nlp.max_length = len(text)  # Set max length to avoid spaCy's limit issues
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]
