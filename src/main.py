import time
import yaml
import logging
import argparse
import datetime as dt

from pipeline import run_pipeline
from utils.log_utils import set_logging_config

# supress warnings
import warnings
warnings.filterwarnings("ignore")

def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
        
    if "parameters" not in config:
        config["parameters"] = {
            "input_dir": "../data/raw",
            "preprocessed_dir": "../data/preprocessed",
            "output_dir": "../data/results",
            "group": False,
            "steps": [1, 2, 3, 4, 5, 6, 7]
        }
    
    if "input_dir" not in config["parameters"]:
        config["parameters"]["input_dir"] = "../data/raw"
    if "preprocessed_dir" not in config["parameters"]:
        config["parameters"]["preprocessed_dir"] = "../data/preprocessed"
    if "output_dir" not in config["parameters"]:
        config["parameters"]["output_dir"] = "../data/results"
    if "group" not in config["parameters"]:
        config["parameters"]["group"] = False
    if "steps" not in config["parameters"]:
        config["parameters"]["steps"] = [1, 2, 3, 4, 5, 6, 7]
    
    if "group" in config["parameters"]:
        config["parameters"]["group"] = True        
    
    return config

def parse_args():    
    p = argparse.ArgumentParser()    
    p.add_argument('-i', '--input_dir', type=str, help='Pasta contendo os arquivos de texto brutos')
    p.add_argument('-p', '--preprocessed_dir', type=str, help='Pasta para salvar os arquivos de texto pré-processados')
    p.add_argument('-o', '--output_dir', type=str, help='Pasta para salvar os resultados')
    p.add_argument('-g', '--group', action='store_false', help='Agrupar os resultados por livro')
    p.add_argument('-s', '--steps', type=str, help='Etapas do pipeline a serem executadas')             
    return p.parse_args()

if __name__ == "__main__":
    
    centutries = ['19', '20']
    for century in centutries:
        print(f'Running pipeline for century {century}')
        
        # Load configuration
        config = load_config("../config.yaml")
        set_logging_config(config["parameters"].get("log_file", None))

        logging.info('Iniciando execução do pipeline')
        start_time = time.time()

        # Parse CLI arguments
        args = parse_args()
        for key, value in vars(args).items():
            if value is not None:
                if key == "steps":
                    config["parameters"]["steps"] = [int(step) for step in value.split(",")]
                else:
                    config["parameters"][key] = value
                    
        # Update the directories based on the century
        config["parameters"]["input_dir"] = config["parameters"]["input_dir"].replace("17", century)
        config["parameters"]["preprocessed_dir"] = config["parameters"]["preprocessed_dir"].replace("17", century)
        config["parameters"]["output_dir"] = config["parameters"]["output_dir"].replace("17", century)

        # Run the pipeline
        run_pipeline(
            input_folder=config["parameters"]["input_dir"],
            preprocessed_folder=config["parameters"]["preprocessed_dir"],
            output_folder=config["parameters"]["output_dir"],
            group_results=config["parameters"]["group"],
            steps=config["parameters"]["steps"]
        )

        end_time = time.time()
        elapsed_time = dt.timedelta(seconds=end_time - start_time)
        logging.info(f'Pipeline executado em {elapsed_time}')