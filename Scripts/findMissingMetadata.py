import os
import random
import time
import traceback

import pandas as pd
from selenium.common import NoSuchElementException

import htmlParser
import webScraping
from SRProject import *
from Scripts.webScraping import WebScraper
from os_path import *
from unidecode import unidecode


def get_link_from_articles_source_links(title):
    # check if title is in articles_source_links.tsv
    links_already_searched = pd.read_csv(f'{MAIN_PATH}/Scripts/articles_source_links.tsv', sep='\t',
                                         encoding='windows-1252', encoding_errors='ignore')
    links_already_searched['Title'] = links_already_searched['Title'].astype(str)
    # links_already_searched['Title'] = links_already_searched['Title'].apply(unidecode)
    # links_already_searched = pd.read_csv(f'{MAIN_PATH}/Scripts/articles_source_links.tsv', sep='\t')
    if title in links_already_searched['Title'].values:
        print("link already searched, adding it instead of DOI")
        return links_already_searched.loc[links_already_searched['Title'] == title]['Link'].values[-1]


def get_from_already_extract(formated_name, already_extracted_files, source=None):
    metadata = None
    print("formated_name", formated_name)
    for formated_name in [formated_name, formated_name.strip()]:
        for file in already_extracted_files:
            # file = file.lower()
            # formated_name = formated_name.lower()

            try:
                new_metadata = None
                try:
                    tmp_source = code_source[file[-7:-5]]
                except:
                    try:
                        tmp_source = code_source[file[-6:-4]]
                    except:
                        tmp_source = source
                if tmp_source == IEEE:
                    if file[11:-8] == formated_name + "%2Freferences#references":
                        print(file)
                        new_metadata = htmlParser.get_metadata_from_already_extract(file, IEEE)
                    elif file[11:-8] == formated_name + "%2Fkeywords#keywords":
                        print(file)
                        new_metadata = htmlParser.get_metadata_from_already_extract(file, IEEE)
                    elif file[-3:] == 'bib' and file[11:-7] == formated_name:
                        new_metadata = htmlParser.get_metadata_from_already_extract(file, IEEE)
                elif tmp_source is not None and (file[11:-8] == formated_name or file[11:-7] == formated_name):
                    print(file)
                    new_metadata = htmlParser.get_metadata_from_already_extract(file, tmp_source)
                if new_metadata:
                    if metadata:
                        update_metadata(metadata, new_metadata)
                    else:
                        metadata = new_metadata
                    print(metadata)
            except Exception as e:
                print("Error", e)
                raise Exception(e)
    return metadata


def extract_without_link(row, already_extracted_files, web_scraper):
    metadata = None
    source, year, authors = None, None, None
    print(row[['title', 'source']])
    if not pd.isna(row['source']): source = row['source']
    if not pd.isna(row['year']): year = row['year']
    if not pd.isna(row['authors']): authors = row['authors']

    print(source, authors, year)

    # check if title is in articles_extract_manually.tsv
    articles_extract_manually = pd.read_csv(f'{MAIN_PATH}/Scripts/articles_extract_manually.tsv', sep='\t')
                                            # encoding='windows-1252', encoding_errors='ignore')
    if row['title'] in articles_extract_manually['meta_title'].values:
        print("link already extracted manually, adding it")
        extract_row = articles_extract_manually.loc[articles_extract_manually['meta_title'] == row['title']].iloc[0]
        extract_row = extract_row.apply(str)
        metadata = metadata_base.copy()
        metadata['Title'] = unidecode(extract_row['title'])
        metadata['Abstract'] = unidecode(extract_row['abstract'])
        metadata['Keywords'] = unidecode(extract_row['keywords'])
        metadata['Authors'] = unidecode(extract_row['authors'])
        metadata['Venue'] = unidecode(extract_row['venue'])
        metadata['DOI'] = extract_row['doi']
        metadata['References'] = unidecode(extract_row['references'])
        metadata['Pages'] = unidecode(extract_row['pages'])
        metadata['Bibtex'] = unidecode(extract_row['bibtex'])
        metadata['Source'] = unidecode(extract_row['source'])
        metadata['Year'] = extract_row['year']
        metadata['Link'] = extract_row['link']
        metadata['Publisher'] = unidecode(extract_row['publisher'])
        return metadata

    # check if already extracted without link
    for column in ['title']:
        # for column in ['title', 'authors', 'abstract']:
        formated_name = format_link(str(row[column]))
        metadata = get_from_already_extract(formated_name, already_extracted_files)

    if metadata:
        print("already extracted without link")
        print("metadata", metadata['DOI'])
        # if metadata['DOI'] is None or metadata['DOI'] == "":
        source = metadata['Source']
        authors = metadata['Authors']

        metadata['Link'] = get_link_from_articles_source_links(row['title'])
        if metadata['DOI'] is None or metadata['DOI'] == "":
            print("missing DOI")
            metadata['DOI'] = metadata['Link']

    # need to extract without link
    if not metadata or metadata['DOI'] is None or metadata['DOI'] == "" or metadata['Bibtex'] is None or metadata['Bibtex'] == "":

        print("no metadata")
        print("title", row['title'])
        print("source", source)
        print("author", authors)
        print("year", year)
        if web_scraper:
            metadata = web_scraper.get_metadata_from_title(row['title'], authors, ScopusSignedIn)  #### source here if want to specify
            if metadata: print("extracted without link")
            else: print("no article found without link")
            # time.sleep(60)
            # extract doi obtained
            if metadata and metadata['DOI']:
                print("trying to extract from new DOI")
                new_metadata = web_scraper.get_metadata_from_link(row['title'], "https://doi.org/" + str(metadata['DOI']), metadata['Publisher'])
                if new_metadata and new_metadata['Title']:
                    update_metadata(metadata, new_metadata)
                    print("extracted from new doi obtained")

    print(metadata)
    return metadata


def extract_with_link(row, already_extracted_files, web_scraper: WebScraper):
    metadata = None
    # check if already extracted
    url = row['doi']
    formated_url = format_link(str(url))
    source = htmlParser.get_source(formated_url) if not row['source'] or pd.isna(row['source']) else str(row['source'])
    metadata = get_from_already_extract(formated_url, already_extracted_files, source)

    formated_name = format_link(str(row['title']))

    if not metadata:
        metadata = get_from_already_extract(formated_name, already_extracted_files)

    # check if different link saved than the one given
    if metadata:
        source_link = get_link_from_articles_source_links(row['title'])
        metadata['Link'] = source_link if source_link else url
        print("already extracted from link")

    # if not already extracted
    if not metadata or metadata['Bibtex'] is None or metadata['Bibtex'] == "":
        if web_scraper:
            for i in range(5):
                try:
                    metadata = web_scraper.get_metadata_from_link(row['title'], url, source)
                    break
                except NoSuchElementException as e:
                    break
                    metadata = None
                    web_scraper.close()
                    web_scraper = webScraping.WebScraper()
                    continue
            if metadata:
                print("extracted from link")
                metadata['Link'] = url
            else: print("no article found from link")
            # time.sleep(60*5)

    if not metadata or not metadata['Title'] or metadata['Bibtex'] is None or metadata['Bibtex'] == "":
        metadata = extract_without_link(row, already_extracted_files, web_scraper)

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
        row['bibtex'] = '"' + metadata['Bibtex'] + '"'
    if metadata['Source']:
        row['source'] = metadata['Source']
    if metadata['References']:
        row['references'] = metadata['References']
    if metadata['Publisher']:
        row['publisher'] = metadata['Publisher']
    print(metadata['DOI'])
    # if (pd.isna(row['doi']) or row['doi'][:15] != "https://doi.org") and metadata['DOI'] is not None and metadata[
    #     'DOI'] not in ["", "None"]:
    if metadata['DOI']:
        row['doi'] = "https://doi.org/" + str(metadata['DOI']) if "http" not in metadata['DOI'] else metadata['Link']
    if metadata['Link']:
        row['link'] = metadata['Link']
    if (metadata['DOI'] is None or metadata['DOI'] == "") and metadata['Link']:
        row['doi'] = row['link']
    elif (metadata['Link'] is None or metadata['Link'] == "") and metadata['DOI']:
        row['link'] = row['doi']
    for key in metadata.keys():
        if metadata[key] is None or metadata[key] == "":
            row['metadata_missing'] = str(row['metadata_missing']) + '; ' + str(key)
    return row
    

def main(sr_df, do_web_scraping=False, run=999):
    completed_sr_project = sr_df.copy().reset_index()
    print(len(pd.isna(completed_sr_project['meta_title'])), "articles to be extracted")
    metadata_cols = ['title', 'venue', 'authors', 'abstract', 'keywords', 'references', 'doi', 'meta_title']

    web_scraper = webScraping.WebScraper() if do_web_scraping else None

    # run = 111  # <------- partition [0,1,2,3], only without link [111] or complete [999]
    parts = 6
    n = len(list(sr_df.iterrows()))//parts
    erreurs = []

    # Get already extracted files from HTML and Bibtex
    already_extracted_files = []
    already_extracted_html = os.listdir(f"{EXTRACTED_PATH}/HTML extracted")
    already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
    already_extracted_files.extend(already_extracted_html)
    already_extracted_files.extend(already_extracted_bibtex)

    # Extract files
    for idx, row in completed_sr_project.iterrows():
        try:
            print(idx)
            if run < parts and not (n * run <= idx <= n * (run+1)):
                continue  # seulement partition
            if run == 111 and not (idx == 152):
                continue  # on veut extraire sans link
            # if row['source'] in ["IEEE", "ACM", "Web of Science", "Scopus"]:
            #     continue

            # check if it is missing at least one metadata
            url = str(row['doi'])
            # if url[:4] != 'http':continue
            need_web_scraping = True
            # for col in metadata_cols:
            #     if pd.isna(row[col]):
            #         need_web_scraping = True
            #         break

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
            print(traceback.format_exc())
            erreurs.append((idx, e, traceback.format_exc()))
            # breakpoint()
        print(completed_sr_project.loc[idx])
        completed_sr_project.loc[idx] = row
        print(row)

    # for er in erreurs: print(er)
    pd.DataFrame(erreurs, columns=['index', 'key', 'error']).to_excel(f"{MAIN_PATH}/Datasets/erreurs_"+str(run)+".xlsx")
    if web_scraper: web_scraper.close()
    return completed_sr_project
