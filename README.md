# NLP Pipeline for Gender Bias Detection in Portuguese Literature

This project implements an NLP pipeline to detect gender bias in Portuguese literature. The pipeline consists of six steps, from preprocessing the text to gender bias analysis. The main script processes multiple text files, extracting entities, classifying gender, analyzing dependencies, and calculating gender skewness, outputting the results into CSV files.

## Project Structure

```plaintext
gender_bias_detection/
│
├── data/
│   ├── raw/               # Folder for raw input text files
│   ├── preprocessed/      # Folder for preprocessed text files
│   ├── results/           # Folder for output files
│   │   ├── book_dicts/    # Folder for intermediate JSON files
│   │   └── gender_bias/   # Folder for gender bias calculation results
│
├── src/
│   ├── __init__.py        # Init file for the src module
│   ├── preprocessing.py   # Step 1: Preprocessing and Sentencer
│   ├── ner.py             # Step 2: Entity Recognition
│   ├── segmentation.py    # Step 3: Excerpt Segmentation
│   ├── gender_classification.py # Step 4: Gender Classification
│   ├── dependency_analysis.py   # Step 5: Dependency Analysis
│   ├── gender_skewness.py       # Step 6: Gender Skewness
│   ├── plot_results.py          # Step 7: Plot Results
│   ├── utils/               # Utility functions
│       ├── files.py         # File read/write functions
│       ├── log_utils.py     # Logging configuration
│
├── notebooks/             # Jupyter notebooks for exploration and analysis
│
├── tests/                 # Unit tests for the pipeline components
│
├── requirements.txt       # List of Python packages required
├── README.md              # Project overview and instructions
└── main.py                # Main script to run the entire pipeline
```

## Instalation

1. Clone the repository:
```
git clone https://github.com/marianaossilva/gender_pipeline.git
cd gender_pipeline
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Download the spaCy Portuguese model:
```
python -m spacy download pt_core_news_lg
```

## Usage
### Running the Pipeline

The main script `main.py` orchestrates the entire pipeline. To run the pipeline, ensure you have your input text files in the `data/raw` directory, then execute:
```
python main.py
```

### Steps in the Pipeline
1. Preprocessing and Sentencer:

- Cleans the text, tokenizes, and segments it into sentences.
- Output: Preprocessed text files in `data/preprocessed`.

2. Entity Recognition:

- Uses a BERT-CRF model to extract PERSON entities.
- Output: JSON files with recognized entities in `data/results/book_dicts`.

3. Excerpt Segmentation:

- Segments text into excerpts around PERSON entities.
- Output: Updated JSON files in `data/results/book_dicts`.

4. Gender Classification:

- Classifies the gender of each PERSON entity.
- Output: Updated JSON files in `data/results/book_dicts`.

5. Dependency Analysis:

- Analyzes grammatical dependencies to understand how gendered terms are used.
- Output: Updated JSON files in `data/results/book_dicts`.

6. Gender Skewness:

- Measures gender bias by calculating skewness in the text.
- Output: JSON files with gender bias results in `data/results/gender_bias`.

7. Plot Results (To be implemented):

- Visualizes the analysis results.

## How to Cite

If you use this pipeline in your research or work, please cite it as follows:
```
@inproceedings{semish/Silva24,
 author = {Mariana Silva and Mirella Moro},
 title = {{NLP} Pipeline for Gender Bias Detection in Portuguese Literature},
 booktitle = {Anais do LI Seminário Integrado de Software e Hardware, {SEMISH}},
 location = {Brasília/DF},
 year = {2024},
 issn = {2595-6205},
 pages = {169--180},
 publisher = {SBC},
 doi = {10.5753/semish.2024.2914},
 url = {https://sol.sbc.org.br/index.php/semish/article/view/29365}
}
```
