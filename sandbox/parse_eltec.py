import os
import glob

from bs4 import BeautifulSoup

output_path = '../data/Eltec Corpus/txts/'
eltec_path = '../data/Eltec Corpus/xmls/*.xml'
files = glob.glob(eltec_path)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        raw_html = f.read()
        raw_html = BeautifulSoup(raw_html, "xml")
        # get only the body of the text
        raw_html = raw_html.find_all('body')[0]
        cleantext = raw_html.text
        with open(output_path + os.path.basename(file).replace('.xml', '.txt'), 'w', encoding='utf-8') as out:
            out.write(cleantext)
        