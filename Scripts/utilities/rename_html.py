import csv
import os, pandas
import shutil
import time

import pandas as pd
from pybtex.database import parse_file

from SRProject import *
from os_path import EXTRACTED_PATH
from bs4 import BeautifulSoup
import htmlParser


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
# get_url_from_html()

def extract_from_manual():
    metadata = metadata_base.copy()
    metadata['Title'] = "Role-Playing Computer Game To Improve Speech Ability Of Down Syndrome Children"
    articles_extract_manually = pd.read_csv(f'{MAIN_PATH}/Scripts/data/articles_extract_manually.tsv', sep='\t',
                                            encoding='windows-1252', encoding_errors='ignore')
    if metadata['Title'] in articles_extract_manually['meta_title'].values:
        print("link already extracted manually, adding it")
        row = articles_extract_manually.loc[articles_extract_manually['meta_title'] == metadata['Title']].iloc[0]
        print(row)
        metadata['Title'] = row['title']
        metadata['Abstract'] = row['abstract']
        metadata['Keywords'] = row['keywords']
        metadata['Authors'] = row['authors']
        metadata['Venue'] = row['venue']
        metadata['DOI'] = row['doi']
        metadata['References'] = row['references']
        metadata['Pages'] = row['pages']
        metadata['Bibtex'] = row['bibtex']
        metadata['Source'] = row['source']
        metadata['Year'] = row['year']
        metadata['Link'] = row['link']
        metadata['Publisher'] = row['publisher']
    print(metadata)
# extract_from_manual()

def compare_titles_and_metatitles(project):
    errors = []
    df = pd.read_csv(f"{MAIN_PATH}/Datasets/{project}/{project}.tsv", sep='\t')
    links_already_searched = pd.read_csv(f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv', sep='\t',
                                         encoding='windows-1252', encoding_errors='ignore')
    for idx, row in df.iterrows():
        title = standardize_title(str(row['title']))
        meta_title = standardize_title(str(row['meta_title']))
        if abs(len(title.split()) - len(meta_title.split())) > 4 or abs(len(title) - len(meta_title)) > 10 or edit_distance(title, meta_title) > 3:
            print("erreur")
            errors.append((idx, title, meta_title))
            print(('idx', 'extracted title', 'original title'))
            print((idx, title, meta_title))
            # errors.append((idx, row['title'], row['meta_title']))
            if title not in meta_title and meta_title not in title: decision = 'y'
            else: decision = input("delete?")
            if decision == "y":
                n = 0
                for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
                    if file[11:-8] == format_link(str(row['meta_title'])):
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}", f"{EXTRACTED_PATH}/Error/{file}")
                        print(file)
                        n += 1
                for file in os.listdir(f"{EXTRACTED_PATH}/Bibtex"):
                    if file[11:-7] == format_link(str(row['meta_title'])):
                        os.rename(f"{EXTRACTED_PATH}/Bibtex/{file}", f"{EXTRACTED_PATH}/Error/{file}")
                        print(file)
                        n += 1
                print('nb deplace:', n)
                links_already_searched = links_already_searched.loc[links_already_searched['Title'] != meta_title] # enlever le lien vers l'article
                links_already_searched.to_csv(f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv', sep='\t')
                print("liens supprimés")
                time.sleep(1)
        else:
            print("correct")
    print("====================================")
    for er in errors: print(er)
    print(len(errors))
#compare_titles_and_metatitles('SecSelfAdapt')

def clean_bad_html():
    n = 0
    for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
        if 'http' in file:
            continue
        if file[-7:-5] == '00':
            with open(f"{EXTRACTED_PATH}/HTML extracted/{file}", 'rb') as f:
                doc = f.read().decode('utf-8')
                metadata = htmlParser.get_metadata_from_html_ieee(doc)
                if not metadata or not metadata['Title']:
                    print(file)
                    print(metadata)
                    if "IEEE Xplore is temporarily unavailable" in doc:
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}",f"{EXTRACTED_PATH}/Error/{file}")
                        print('deplace...')
                        n += 1
        if file[-7:-5] == '01':
            with open(f"{EXTRACTED_PATH}/HTML extracted/{file}", 'rb') as f:
                doc = f.read().decode('utf-8')
                metadata = htmlParser.get_metadata_from_html_ACM(doc)
                if not metadata or not metadata['Title']:
                    print(file)
                    print(metadata)
                    if "DOI Not Found" in doc:
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}",f"{EXTRACTED_PATH}/Error/{file}")
                        print('deplace...')
                        n += 1
        if file[-7:-5] == '02':
            with open(f"{EXTRACTED_PATH}/HTML extracted/{file}", 'rb') as f:
                doc = f.read().decode('utf-8')
                metadata = htmlParser.get_metadata_from_html_sciencedirect(doc)
                if not metadata or not metadata['Title']:
                    print(file)
                    print(metadata)
                    if "There was a problem providing the content you requested" in doc:
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}",f"{EXTRACTED_PATH}/Error/{file}")
                        print('deplace...')
                        n += 1
    print('nb deplace:', n)
# clean_bad_html()

def clean_and_duplicate_good_scopus_html():
    n = 0
    for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
        if not 'scopus' in file:
            continue
        # if file[-8:-5] == '_04':
        #     os.remove(f"{EXTRACTED_PATH}/HTML extracted/{file}")
        shutil.copy(f"{EXTRACTED_PATH}/HTML extracted/{file}", f"{EXTRACTED_PATH}/HTML extracted/{file[:-5] + '_04' + file[-5:]}")
# clean_and_duplicate_good_scopus_html()

def clean_publisher(publisher: str):
    if not publisher:
        return publisher
    publisher = publisher.replace('All rights reserved.', '')
    publisher = re.sub('^\d+[-,\d\s]*?(?=[A-Za-z])', '', publisher.strip())  # chiffre avant texte
    publisher = re.sub('\d+\s*.*$', '', publisher.strip())  # chiffre apres texte
    if publisher[-1] == '.': publisher = publisher[:-1]
    return publisher
# print(clean_publisher('ACTA PRESS2509 DIEPPE AVE SW, BLDG B6, STE 101, CALGARY, AB T3E 7J9, CANADA'))

def clean_abstract(abstract):
    if not abstract:
        return abstract
    abstract = re.sub('(?:\(c\)|Copyright)\s*(.*)', '', abstract)
    return abstract
# print(clean_abstract("""There is untapped potential in having a computer work as a colleague with the video game level designer as a source of creative stimuli, instead of simply working as his slave. This paper presents 3Buddy, a co-creative level design tool exploring this digital peer paradigm, aimed at fostering creativity by allowing human and computer to work together in the context of level design, and describes a case study of the approach to produce content using the Legend of Grimrock 2 level editor. Suggestions are generated and iteratively evolved by multiple inter-communicating genetic algorithms guiding three different domains: innovation (exploring new directions), guidelines (respecting specific design goals) and convergence (focusing on current co-proposal). The interface allows the designer to orient the tool behaviour in the space defined by these dimensions. This paper details the inner workings of the system and presents an exploratory study showing, on the one hand, how the tool was used differently by professional and amateur level designers, and on the other hand, how the nuances of the co-creative interaction through an intention-oriented interface may be a source of positive influence for the creative level design process. (c) ICCC 2017.
# """))

def remove_whitespaces_from_bibtex_id(bibtex_string):
    match = re.search(r"(?<=\{)(.*?)(?=\,)", bibtex_string)

    if match:
        cleaned_id = match.group().replace(' ', '')
        bibtex_string = bibtex_string.replace(match.group(), cleaned_id)
    return bibtex_string

def wrap_entry_in_bibtex(bibtex_string):
    def clean_field(field_content):
        # Split by "and" to process each editor/institution separately
        entries = field_content.split(" and ")
        cleaned_entries = []
        for entry in entries:
            # Escape commas in each entry that are not already wrapped in {}
            if ',' in entry and not entry.startswith("{") and not entry.endswith("}"):
                cleaned_entries.append(f"{{{entry.strip()}}}")
            else:
                cleaned_entries.append(entry.strip())
        return " and ".join(cleaned_entries)

    # Search for the editor field and apply cleaning
    bibtex_string = re.sub(
        r'editor\s*=\s*{([^{}]*)}',
        lambda match: 'editor = {' + clean_field(match.group(1)) + '}',
        bibtex_string
    )
    return bibtex_string

# Example usage
bibtex_string = """
@ARTICLE{Caron2003164,
	author = {Caron, O. and Carré, B. and Muller, A. and Vanwormhoudt, G.},
	title = {A framework for supporting views in component oriented information systems},
	year = {2003},
	journal = {Lecture Notes in Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics)},
	volume = {2817},
	pages = {164 – 178},
	doi = {10.1007/978-3-540-45242-3_16},
	url = {https://www.scopus.com/inward/record.uri?eid=2-s2.0-35248841430&doi=10.1007%2f978-3-540-45242-3_16&partnerID=40&md5=4b710662ae6114ad707ca98c732cf67f},
	affiliations = {Laboratoire d'Informatique Fondamentale de Lille, UPRESA CNRS 8022, Université des Sciences et Technologies de Lille, 59655 Villeneuve d'Ascq Cedex, France},
	abstract = {The Component Oriented Design of Information Systems is spreading. After being used for gaining in reusability at the architectural level, components are nowadays applied at the business logic level. We focus here on the design of multiple functional views in such information systems, specially within the EJB framework. Traditionally, in the database context, this problem is solved by the notion of "view-schemas" applied to a database schema. We present a composition-oriented approach grounded on the splitting of entities according to views requirements. Two original design patterns are formulated and capture the main issues of the approach. The first one is concerned with the management of the split component and its conceptual identity. The second offers a solution for relationships among such components. Finally, we apply these patterns to the EJB framework. This framework improves evolution and traceability of views. © Springer-Verlag Berlin Heidelberg 2003.},
	keywords = {Reusability; Architectural levels; Business logic; Component-oriented; Component-oriented designs; Database schemas; Original design; Information systems},
	correspondence_address = {O. Caron; Laboratoire d'Informatique Fondamentale de Lille, UPRESA CNRS 8022, Université des Sciences et Technologies de Lille, 59655 Villeneuve d'Ascq Cedex, France; email: carono@lifl.fr},
	editor = {Konstantas D. and Leonard M. and Konstantas D. and University of Twente, Department of Computer Science, P.O.Box 217, Enschede, 7500 and Pigneur Y. and Patel S. and South Bank University, School of Computing, Information Systems and Mathematics, 103 Borough Road, London, SE1 0AA},
	publisher = {Springer Verlag},
	issn = {03029743},
	isbn = {3540408606},
	language = {English},
	abbrev_source_title = {Lect. Notes Comput. Sci.},
	type = {Article},
	publication_stage = {Final},
	source = {Scopus},
	note = {Cited by: 8}
}
"""

# cleaned_bibtex = remove_whitespaces_from_bibtex_id(bibtex_string)
# print(cleaned_bibtex)
# clean_bibtex = wrap_entry_in_bibtex(bibtex_string)
# print(clean_bibtex)


def test_opening_dataset(tsv):
    df = pandas.read_csv(tsv, sep='\t', encoding='utf-8')
    return df
# test_df = test_opening_dataset(f'{MAIN_PATH}/Datasets/_Datasets Sent/ESPLE.tsv')
# print(test_df.shape)
# print(test_df.columns)
# test_df = test_opening_dataset(f'{MAIN_PATH}/Datasets/_Datasets Sent/ESPLE.tsv')
# print(test_df.shape)
# print(test_df.columns)

def clean_all_bibtex():
    for file in os.listdir(f"{EXTRACTED_PATH}/Bibtex"):
        with open(f"{EXTRACTED_PATH}/Bibtex/{file}", 'rb') as f:
            bib = f.read().decode('utf-8')
        cleaned_bib = remove_whitespaces_from_bibtex_id(bib)
        with open(f"{EXTRACTED_PATH}/Bibtex/{file}", 'wb') as f:
            f.write(cleaned_bib.encode('utf-8'))
        print(file)
# clean_all_bibtex()

def convert_bib_to_tsv():
    # Path to your .bib file
    input_bib_file = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées/Datasets/ESPLE/ESPLE-screened.bib"
    # Path to save the output .tsv file
    output_tsv_file = "C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées/Datasets/ESPLE/ESPLE-screened.tsv"

    # List of desired columns in the output TSV
    columns = [
        "entrytype", "abstract", "address", "annote", "author", "booktitle",
        "chapter", "crossref", "edition", "editor", "howpublished",
        "institution", "journal", "key", "month", "note", "number",
        "organization", "pages", "paper", "publisher", "school", "series",
        "title", "type", "volume", "year"
    ]

    # Parse the .bib file
    bib_data = parse_file(input_bib_file)

    # Extract records into a list of dictionaries
    records = []

    for entry_key, entry in bib_data.entries.items():
        record = {field: entry.fields.get(field, "") for field in columns}
        record["entrytype"] = entry.type
        # Handle authors and editors as comma-separated strings
        if "author" in entry.persons:
            record["author"] = ", ".join(str(person) for person in entry.persons["author"])
        if "editor" in entry.persons:
            record["editor"] = ", ".join(str(person) for person in entry.persons["editor"])
        records.append(record)

    # Create a DataFrame and save it as TSV
    df = pd.DataFrame(records, columns=columns)
    df.to_csv(output_tsv_file, sep='\t', index=False)

    print(f"Conversion complete! TSV file saved as: {output_tsv_file}")
# convert_bib_to_tsv()

def rename_bib_from_doi_to_title():
    # Load data efficiently
    links_already_searched = pd.read_csv(f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv', sep='\t',
                                         encoding='windows-1252', encoding_errors='ignore')

    # Convert DataFrame to a dictionary for fast lookups
    link_to_title = {format_link(str(row['Link'])): format_link(str(row['Title'])) for idx, row in
                     links_already_searched.iterrows()}

    # Define the path using pathlib
    bibtex_path = f"{EXTRACTED_PATH}/Bibtex"

    # Iterate over files in reverse order
    for file in reversed(os.listdir(bibtex_path)):
        file_key = file[11:-7]
        if file_key in link_to_title:
            new_name = file[:11] + link_to_title[file_key] + file[-7:]
            old_path = bibtex_path + '/' + file
            new_path = bibtex_path + '/' + new_name
            os.rename(old_path, new_path)
            print(f"{file} renamed to {new_name}")


rename_bib_from_doi_to_title()