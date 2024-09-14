import os
import random
import time
import traceback

import htmlParser
import webScraping
from SRProject import *
from os_path import *


def extract_without_link(row, already_extracted_files, web_scraper):
    metadata = None
    source, year, authors = None, None, None
    print(row[['title', 'source']])
    if not pd.isna(row['source']): source = row['source']
    if not pd.isna(row['year']): year = row['year']
    if not pd.isna(row['authors']): authors = row['authors']

    print(source, authors, year)

    # check if already extracted without link
    for column in ['title']:
        # for column in ['title', 'authors', 'abstract']:
        formated_name = str(row[column])
        for k in special_char_conversion.keys():
            formated_name = formated_name.replace(k, "%" + special_char_conversion[k])
        print("formated_name", formated_name)
        for file in already_extracted_files:
            new_metadata = None
            try:
                tmp_source = code_source[file[-7:-5]]
            except:
                try:
                    tmp_source = code_source[file[-6:-4]]
                except:
                    tmp_source = None
            if tmp_source == IEEE:
                if file[11:-8] == formated_name + "%2Freferences#references":
                    print(file)
                    new_metadata = htmlParser.get_metadata_from_already_extract(file, IEEE)
                elif file[11:-8] == formated_name + "%2Fkeywords#keywords":
                    print(file)
                    new_metadata = htmlParser.get_metadata_from_already_extract(file, IEEE)
            elif tmp_source is not None and (file[11:-8] == formated_name or file[11:-7] == formated_name):
                print(file)
                new_metadata = htmlParser.get_metadata_from_already_extract(file, tmp_source)
            if new_metadata:
                if metadata: update_metadata(metadata, new_metadata)
                else: metadata = new_metadata

    # TODO: check if link already get through search
    if metadata:
        print("already extracted without link")
        print("metadata", metadata['DOI'])
        # if metadata['DOI'] is None or metadata['DOI'] == "":
        source = metadata['Source']
        authors = metadata['Authors']
        links_already_searched = pd.read_csv(f'{MAIN_PATH}/Scripts/articles_source_links.tsv', sep='\t', encoding='windows-1252')
        if metadata['Title'] in links_already_searched['Title'].values:
            print("link already searched, adding it instead of DOI")
            metadata['Link'] = links_already_searched.loc[links_already_searched['Title'] == metadata['Title']]['Link'].values[0]
            if metadata['DOI'] is None or metadata['DOI'] == "":
                print("missing DOI")
                metadata['DOI'] = metadata['Link']
                

    # need to extract without link
    if not metadata or metadata['DOI'] is None or metadata['DOI'] == "":

        print("no metadata")
        print("title", row['title'])
        print("source", source)
        print("author", authors)
        print("year", year)
        if web_scraper:
            metadata = web_scraper.get_metadata_from_title(row['title'], authors, ScienceDirect, year)
        print("extracted without link")

    return metadata


def extract_with_link(row, already_extracted_files, web_scraper):
    metadata = None
    # check if already extracted
    url = row['doi']
    formated_url = str(url)
    for k in special_char_conversion.keys():
        formated_url = formated_url.replace(k, "%" + special_char_conversion[k])
    print(formated_url)
    source = htmlParser.get_source(formated_url)
    for file in already_extracted_files:
        if not source:  # is a doi
            if file[11:-5] == formated_url:
                print(file)
                print(file[file.find("doi.org%2F") + 10:-5])
                for f in already_extracted_files:
                    if f[11:-5] == "http%3A%2F%2Fapi.crossref.org%2Fworks%2F" + file[file.find(
                            "doi.org%2F") + 10:-5]:
                        print(file)
                        print(f)
                        metadata = htmlParser.get_metadata_from_already_extract(file)
                        break
        elif source == "ieee":
            if file[11:-5] == formated_url + "%2Freferences#references":
                print(file)
                metadata = htmlParser.get_metadata_from_already_extract(file)
            elif file[11:-5] == formated_url + "%2Fkeywords#keywords":
                print(file)
                metadata = htmlParser.get_metadata_from_already_extract(file)
        else:
            if file[11:-5] == formated_url:
                print(file)
                metadata = htmlParser.get_metadata_from_already_extract(file)
        if metadata:
            metadata['Link'] = url
            print("already extracted from link")
            break

    # if not already extracted
    if not metadata:
        if web_scraper:
            metadata = web_scraper.get_metadata_from_link(url, source)
        metadata['Link'] = url
        print("extracted from link")
        time.sleep(random.randint(1, 5))
        
    return metadata


def update_dataset(row, metadata):
    if metadata['Title']:
        row['meta_title'] = row['title']
        row['title'] = metadata['Title']
    if metadata['Venue']:
        row['venue'] = metadata['Venue']
    if metadata['Authors']:
        row['authors'] = metadata['Authors']
    if metadata['Abstract']:
        row['abstract'] = metadata['Abstract']
    if metadata['Keywords']:
        row['keywords'] = metadata['Keywords']
    if metadata['Pages']:
        row['pages'] = metadata['Pages']
    if metadata['Bibtex']:
        row['bibtex'] = metadata['Bibtex']
    if metadata['Source']:
        row['source'] = metadata['Source']
    if metadata['References']:
        row['references'] = metadata['References']
    if metadata['Publisher']:
        row['publisher'] = metadata['Publisher']
    print(metadata['DOI'])
    if (pd.isna(row['doi']) or row['doi'][:15] != "https://doi.org") and metadata['DOI'] is not None and metadata[
        'DOI'] not in ["", "None"]:
        row['doi'] = "https://doi.org/" + str(metadata['DOI']) if "http" not in metadata['DOI'] else metadata['Link']
    if metadata['Link']:
        row['link'] = metadata['Link']
    for key in metadata.keys():
        if metadata[key] is None or metadata[key] == "":
            row['metadata_missing'] = str(row['metadata_missing']) + '; ' + str(key)
    return row
    

def main(sr_df, do_web_scraping=False, run=999):
    completed_sr_project = sr_df.copy()
    web_scraper = webScraping.WebScraper() if do_web_scraping else None
    metadata_cols = ['title', 'venue', 'authors', 'abstract', 'keywords', 'references', 'doi', 'meta_title']

    # run = 111  # <------- partition [0,1,2,3], only without link [111] or complete [999]
    parts = 6
    n = len(list(sr_df.iterrows()))//parts
    i = 0
    erreurs = []
    already_extracted_files = []
    already_extracted_html = os.listdir(f"{EXTRACTED_PATH}/HTML extracted")
    already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
    already_extracted_files.extend(already_extracted_html)
    already_extracted_files.extend(already_extracted_bibtex)
    for idx, row in sr_df.iterrows():
        try:
            i += 1
            print(i)
            if run < parts and not (n * run <= i <= n * (run+1)):
                continue  # seulement partition
            if run == 111 and not (2651 <= i <= 2970):
                continue  # on veut extraire sans link
            # if row['source'] in ["IEEE", "ACM", "Web of Science", "Scopus"]:
            #     continue

            # check if it is missing at least one metadata
            url = row['doi']
            need_web_scraping = False
            for col in metadata_cols:
                if pd.isna(row[col]):
                    need_web_scraping = True
            
            # there is missing at least one metadata
            if need_web_scraping:
                metadata = None

                # link exists in source data
                if not metadata and not pd.isna(url) and url[:4] == 'http':
                    metadata = extract_with_link(row, already_extracted_files, web_scraper)
                    
                # no link
                if not metadata:
                    print(row[['title', 'source']])
                    metadata = extract_without_link(row, already_extracted_files, web_scraper)
                print(metadata)
                
                # found metadata
                if metadata:
                    row = update_dataset(row, metadata)
                    for k in metadata.keys():
                        if metadata[k] is None:
                            erreurs.append((idx, k, 'passed'))
                else:
                    erreurs.append((idx, "all", 'passed'))
        except Exception as e:
            print(e)
            erreurs.append((idx, e, traceback.format_exc()))
        print(completed_sr_project.iloc[idx])
        completed_sr_project.iloc[idx] = row

    # for er in erreurs: print(er)
    pd.DataFrame(erreurs, columns=['index', 'key', 'error']).to_excel(f"{MAIN_PATH}/Datasets/erreurs_"+str(run)+".xlsx")
    if web_scraper: web_scraper.close()
    return completed_sr_project
