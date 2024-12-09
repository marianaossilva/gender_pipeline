import logging

def set_logging_config(log_file):
    
    if log_file is None:
        logging.basicConfig(
            format='%(asctime)s %(levelname)-5s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S'
        )   
    
    logging.basicConfig(
        format='%(asctime)s %(levelname)-5s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file,
        encoding='utf-8',
        filemode='a'
    )