import os
import logging

if 'LOG_FILE' not in os.environ:
    LOG_FILE = None # O log é realizado no terminal
else:
    LOG_FILE = os.environ['LOG_FILE'] 

def set_logging_config():
    logging.basicConfig(
         format='%(asctime)s %(levelname)-5s %(message)s',
         level=logging.INFO,
         datefmt='%Y-%m-%d %H:%M:%S',
         filename=LOG_FILE)