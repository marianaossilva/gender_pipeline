import os
from src.preprocessing import preprocess_text
from src.ner import extract_person_entities
from src.segmentation import segment_excerpts
from src.gender_classification import classify_gender
from src.dependency_analysis import analyze_dependencies
from src.gender_skewness import calculate_gender_skewness
from src.plot_results import plot_results

def main(input_folder, output_folder):
    # Step 1: Preprocessing and Sentencer
    preprocessed_texts = []
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
            preprocessed_sentences = preprocess_text(text)
            preprocessed_texts.append(preprocessed_sentences)
    
    # Step 2: Entity Recognition
    all_entities = []
    for sentences in preprocessed_texts:
        entities = extract_person_entities(sentences)
        all_entities.append(entities)
    
    # Step 3: Excerpt Segmentation
    all_excerpts = []
    for sentences, entities in zip(preprocessed_texts, all_entities):
        excerpts = segment_excerpts(sentences, entities)
        all_excerpts.append(excerpts)
    
    # Step 4: Gender Classification
    gendered_entities = classify_gender(excerpts, all_entities)
    
    # Step 5: Dependency Analysis
    dependency_results = analyze_dependencies(preprocessed_texts, gendered_entities)
    
    # Step 6: Gender Skewness
    skewness_results = calculate_gender_skewness(gendered_entities)
    
    # Step 7: Plot Results
    plot_results(dependency_results, skewness_results, output_folder)

    # Save results to CSV
    for idx, text in enumerate(preprocessed_texts):
        output_filepath = os.path.join(output_folder, f'processed_{idx}.csv')
        with open(output_filepath, 'w', encoding='utf-8') as file:
            # Save relevant data for each step as needed
            pass

if __name__ == "__main__":
    input_folder = 'data/raw'
    output_folder = 'data/results'
    os.makedirs(output_folder, exist_ok=True)
    main(input_folder, output_folder)