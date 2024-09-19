# -*- coding: utf-8 -*-
import sys


import chardet

import findMissingMetadata
from Scripts.DatasetsScripts.Behave import Behave
from Scripts.DatasetsScripts.CodeClone import CodeClone
from Scripts.DatasetsScripts.DTCPS import DTCPS
from Scripts.DatasetsScripts.ESM_2 import ESM_2
from Scripts.DatasetsScripts.GameSE import GameSE
from Scripts.DatasetsScripts.GameSE_abstract import GameSE_abstract
from Scripts.DatasetsScripts.GameSE_title import GameSE_title
from Scripts.DatasetsScripts.TestNN import TestNN
from Scripts.DatasetsScripts.TrustSE import TrustSE
from SRProject import *
from os_path import MAIN_PATH

# Author : Guillaume Genois, 20248507
# This script is for importing and uniformising data from multiple datasets of SR.

"""
  Key               String
  Title             String
  Abstract          String
  Keywords          String
  Authors           String
  Venue             String
  DOI               String
  References        String
  Bibtex            String
  ScreenedDecision  String {Included, Excluded, ConflictIncluded, ConflictExcluded}
  FinalDecision     String {Included, Excluded, ConflictIncluded, ConflictExcluded}
  Mode              String {new_screen, snowballing}
  InclusionCriteria String
  ExclusionCriteria String
  ReviewerCount     Int
"""


# Function to detect the encoding in a file
def printEncoding(file_path):
    with open(file_path, 'rb') as file:
        print(chardet.detect(file.read()))


# Function for postprocessing
def postProcessing(sr_project):
    empty_counts = {"key": 0, "project": 0, "title": 0, "abstract": 0, "keywords": 0, "authors": 0, "venue": 0, "doi": 0,
       "references": 0, "bibtex": 0, "screened_decision": 0, "final_decision": 0, "mode": 0,
       "inclusion_criteria": 0, "exclusion_criteria": 0, "reviewer_count": 0}
    undesirable_pattern = (
        r'[\u0000-\u001F\u007F\u0080-\u009F\u200B\u200C\u200D\u200E\u200F'
        r'\u202A\u202B\u202C\u202D\u202E\uFEFF\uFFFD\0xE2\0x80\0x99]'
    )

    file = pd.read_csv(sr_project.export_path, delimiter="\t")
    for line in file.iterrows():
        row = line[1]
        for key in empty_counts:
            if pd.isna(row[key]):
                empty_counts[key] += 1
            elif re.search(undesirable_pattern, str(row[key])):
                continue
                print("Error:", line[0], row[key])
    print("Number of blanks/NaN:", empty_counts)
    print("Number of articles:", len(file))

    # TODO: check good number of lines exported
    # TODO: check for any unknown characters
    # TODO: check for right encoding
    # TODO: check for NaN or missing values


def cleanDataFrame(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.replace("–", "-")
    new_df = new_df.replace("©", '')
    # new_df = new_df['keywords'].replace(",", ';')
    df_obj = new_df.select_dtypes('object')
    new_df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    return new_df


# Function to export to CSV the SRProject object
def ExportToCSV(sr_project):

    # final_data_frame = pd.DataFrame(columns=["key", "project", "title", "abstract", "keywords", "authors", "venue",
    #                                          "doi", "references", "bibtex", "screened_decision", "final_decision",
    #                                          "mode", "inclusion_criteria", "exclusion_criteria", "reviewer_count"],
    #                                 dtype=str)
    #
    # final_data_frame["project"] = sr_project.project
    # final_data_frame["title"] = sr_project.title
    # final_data_frame["abstract"] = sr_project.abstract
    # final_data_frame["keywords"] = sr_project.keywords
    # final_data_frame["authors"] = sr_project.authors
    # final_data_frame["venue"] = sr_project.venue
    # final_data_frame["doi"] = sr_project.doi
    # final_data_frame["references"] = sr_project.references
    # final_data_frame["bibtex"] = sr_project.bibtex
    # final_data_frame["screened_decision"] = sr_project.screened_decision
    # final_data_frame["final_decision"] = sr_project.final_decision
    # final_data_frame["mode"] = sr_project.mode
    # final_data_frame["inclusion_criteria"] = sr_project.inclusion_criteria
    # final_data_frame["exclusion_criteria"] = sr_project.exclusion_criteria

    # final_data_frame = sr_project.df.drop(columns="year")
    final_data_frame = sr_project.df

    # otherwise error when trying to change None to int
    if sr_project.reviewer_count is not None:
        final_data_frame["reviewer_count"] = sr_project.reviewer_count
        final_data_frame["reviewer_count"].astype(int)

    # if there are no keys, assign index as key
    if sr_project.key is None:
        final_data_frame = final_data_frame.drop(columns="key")
        final_data_frame.to_csv(sr_project.export_path, sep="\t", index_label="key", encoding='utf-8')
    else:
        final_data_frame["key"] = sr_project.key
        final_data_frame.to_csv(sr_project.export_path, sep="\t", index=False, encoding='utf-8')
    # TODO: why not just assign key as range directly in SRProject class?


# def add_missing_links(df):
#     for idx, row in df.iterrows():
#         if row[]

def main(args=None):
    if args is None or not len(args) > 0:
        args = ["GameSE", "GameSE_abstract", "GameSE_title"]
    sr_project = None

    for arg in args:
        if arg == "Behave":
            sr_project = Behave()
        elif arg == "CodeClone":
            sr_project = CodeClone()
        elif arg == "DTCPS":
            sr_project = DTCPS()
        elif arg == "ESM_2":
            sr_project = ESM_2()
        elif arg == "GameSE":
            sr_project = GameSE()
        elif arg == "GameSE_title":
            sr_project = GameSE_title()
        elif arg == "GameSE_abstract":
            sr_project = GameSE_abstract()
        elif arg == "TestNN":
            sr_project = TestNN()
        elif arg == "TrustSE":
            sr_project = TrustSE()

        sr_project.df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}_pre-extract.xlsx")
        # printEncoding(sr_project.path)  # to make sure we use the right encoding if necessary
        completed_df = findMissingMetadata.main(sr_project.df, False, 999)
        # df = pd.read_csv("C:/Users/guill/OneDrive - Universite de Montreal/Projet Curation des métadonnées/Datasets/{arg}/{arg}.tsv", delimiter="\t")
        # print(df)
        # completed_df = find_missing_metadata(df)
        cleaned_df = cleanDataFrame(completed_df)
        cleaned_df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}.xlsx")
        # return
        # postProcessing(sr_project)
        sr_project.df = cleaned_df

        ExportToCSV(sr_project)
        postProcessing(sr_project)


if __name__ == "__main__":
    main(sys.argv[1:])
