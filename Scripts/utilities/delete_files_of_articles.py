# Loop through folders and files
import os
from pathlib import Path

import pandas

from Scripts.SRProject import code_source, IEEE
from Scripts.os_path import EXTRACTED_PATH, MAIN_PATH

# df = pandas.read_excel(Path(MAIN_PATH) / 'Datasets' / 'ModelingAssist' / 'ModelingAssist_wrong-titles.xlsx', header=0)
df = pandas.read_csv(Path(MAIN_PATH) / 'Datasets' / 'ModelingAssist' / 'tmp.tsv', sep='\t')
titles = df['meta_title'].values

# Paths to your folders
folders = [Path(EXTRACTED_PATH) / "Bibtex", Path(EXTRACTED_PATH) / "HTML extracted"]


for folder in folders:
    print(len(os.listdir(folder)))
    for filename in os.listdir(folder):
        for title in titles:
            try:
                file = filename.lower()
                formated_name = title.lower()
                do_delete = False
                try:
                    tmp_source = code_source[file[-7:-5]]
                except:
                    try:
                        tmp_source = code_source[file[-6:-4]]
                    except:
                        tmp_source = True
                if tmp_source == IEEE:
                    if file[11:-8] == formated_name + "%2freferences#references":
                        print(file)
                        do_delete = True
                    elif file[11:-8] == formated_name + "%2fkeywords#keywords":
                        print(file)
                        do_delete = True
                    elif file[-3:] == 'bib' and file[11:-7] == formated_name:
                        print(file)
                        do_delete = True
                elif tmp_source is not None and (file[11:-8] == formated_name or file[11:-7] == formated_name):
                    print(file)
                    do_delete = True
                if do_delete:
                    file_path = os.path.join(folder, filename)
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
            except:
                print("erreur")
                continue

