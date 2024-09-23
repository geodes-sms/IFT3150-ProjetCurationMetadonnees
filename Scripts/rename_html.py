import os, pandas

import pandas as pd

from SRProject import *
from os_path import EXTRACTED_PATH
from bs4 import BeautifulSoup


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
        # os.rename(path + "/" + file, path + "/" + rightly_formatted_file)


# rename_files()

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
    df.to_excel(f"{MAIN_PATH}/Datasets/GameSE/GameSE_final_2-bibtex.xlsx")

# generate_bibtex()

def get_url_from_html():
    extract = pd.read_excel(f"{MAIN_PATH}/Datasets/GameSE/GameSE.xlsx")
    for idx, row in extract.iterrows():
        if not pd.isna(row['link']) or not pd.isna(row['doi']):
            continue
        file_to_search = None
        for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
            if file[11:-8] == format_link(str(row['meta_title'])):
                file_to_search = file
                break
        if not file_to_search:
            continue
        with open(f"{EXTRACTED_PATH}/HTML extracted/{file_to_search}") as f:
            soup = BeautifulSoup(f)
        if file_to_search[-7:-5] == '05':
            suffix = soup.find('span', {'id': 'HiddenSecTa-accessionNo'})
            url = "https://www.webofscience.com/wos/woscc/full-record/" + suffix
            save_link(row['meta_title'], url)
get_url_from_html()
