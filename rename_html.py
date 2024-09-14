import os, pandas
from SRProject import *
from os_path import EXTRACTED_PATH

path = f"{EXTRACTED_PATH}/Bibtex"
def rename_files():
    for file in os.listdir(path):
        # print(file)
        rightly_formatted_file = file
        # for char in special_char_conversion.keys():
        #     rightly_formatted_file = rightly_formatted_file.replace(special_char_conversion[char], "%" + special_char_conversion[char])
        # rightly_formatted_file = rightly_formatted_file.replace("3f", "?")
        # # rightly_formatted_file = rightly_formatted_file.replace("24", "$")
        # rightly_formatted_file = rightly_formatted_file.replace("26", "&")
        # rightly_formatted_file = rightly_formatted_file.replace("2b", "+")
        # rightly_formatted_file = rightly_formatted_file.replace("2c", ",")
        # rightly_formatted_file = rightly_formatted_file.replace("3b", ";")
        # rightly_formatted_file = rightly_formatted_file.replace("40", "@")
        # print(file[8:10])
        # if not (file[8:10] == "22" or file[8:10] == "25"):
        #     continue
        # rightly_formatted_file = "2024-08-20_" + rightly_formatted_file
        rightly_formatted_file = rightly_formatted_file[:-7] + "_07" + rightly_formatted_file[-4:]
        print(rightly_formatted_file)
        os.rename(path + "/" + file, path + "/" + rightly_formatted_file)


rename_files()

def test_keys():
    name= "2024-06-25_Adaptive Behavior Control Model Of Non Player Character_05.html"
    print(name[-7:-5])
    print(list(code_source.keys()))
    print(code_source[name[-7:-5]])
    try:
        venue = code_source[name[-7:-5]]
    except:
        venue = None
    print(venue)
    # print(code_source[name[-7:-5]] if str(name[-7:5]) in ['00', '01', '02', '03', '04', '05'] else None)
    print(name[11:-8])


# test_keys()

def generate_bibtex():
    df = pandas.read_excel(f"{MAIN_PATH}\\Datasets\\GameSE\\GameSE_final_2.xlsx")
    for idx, row in df.iterrows():
        bibtex = f"""@article{{{''},
title = {{{row['title']}}},
journal = {{{row['venue']}}},
pages = {{{row['pages']}}},
year = {{{row['year']}}},
issn = {{{''}}},
doi = {{{row['doi']}}},
url = {{{''}}},
author = {{{row['authors']}}},
keywords = {{{row['keywords']}}},
abstract = {{{row['abstract']}}}
}}
"""
        row['bibtex'] = bibtex
        df.iloc[idx] = row
    df.to_excel(f"{MAIN_PATH}\\Datasets\\GameSE\\GameSE_final_2-bibtex.xlsx")

# generate_bibtex()