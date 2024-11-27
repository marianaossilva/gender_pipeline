import os
import glob

from bs4 import BeautifulSoup

output_path = '../data/Colonia Corpus/txts/'
colonia_path = '../data/Colonia Corpus/texts/*.txt'
files = glob.glob(colonia_path)

for file in files:
    try:
        with open(file, 'r', encoding='latin-1') as f:
            raw_html = f.read()
            raw_html = BeautifulSoup(raw_html, "html.parser")
            # get only the body of the text
            raw_html = raw_html.find_all('s')
            cleantext = '\n'.join([s.text for s in raw_html])
            
            # break each line by \t and save the first element
            cleantext = ' '.join([line.split('\t')[0] for line in cleantext.split('\n')])
            with open(output_path + os.path.basename(file), 'w', encoding='latin-1') as out:
                out.write(cleantext)
    except Exception as e:
        print(e)
        print(file)
        continue