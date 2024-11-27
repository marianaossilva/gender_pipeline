import os
import glob

output_path = '../data/Obras Corpus/txts/'
obras_path = '../data/Obras Corpus/txts/*.txt'
files = glob.glob(obras_path)

for file in files:
    with open(file, 'r', encoding='latin-1') as f:
        lines = f.readlines()
        cleantext = ''
        for line in lines:
            if line == '\n':
                continue
            else:
                cleantext += line.split('\t')[0] + ' '          
        with open(output_path + os.path.basename(file), 'w', encoding='latin-1') as out:
            out.write(cleantext)
        