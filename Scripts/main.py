# -*- coding: utf-8 -*-
import os
# import cudf.pandas
# cudf.pandas.install()
import sys

from Scripts.DatasetsScripts.Demo import Demo
from Scripts.DatasetsScripts.IFT3710 import IFT3710
from Scripts.os_path import MAIN_PATH

# sys.stdout = open(os.devnull, 'w')
sys.path.extend([MAIN_PATH])

import chardet
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
import findMissingMetadata
from Scripts.DatasetsScripts.ArchiML import ArchiML
from Scripts.DatasetsScripts.Behave import Behave
from Scripts.DatasetsScripts.CodeClone import CodeClone
from Scripts.DatasetsScripts.CodeCompr import CodeCompr
from Scripts.DatasetsScripts.DTCPS import DTCPS
from Scripts.DatasetsScripts.ESM_2 import ESM_2
from Scripts.DatasetsScripts.ESPLE import ESPLE
from Scripts.DatasetsScripts.GameSE import GameSE
from Scripts.DatasetsScripts.GameSE_abstract import GameSE_abstract
from Scripts.DatasetsScripts.GameSE_title import GameSE_title
from Scripts.DatasetsScripts.ModelGuidance import ModelGuidance
from Scripts.DatasetsScripts.ModelingAssist import ModelingAssist
from Scripts.DatasetsScripts.OODP import OODP
from Scripts.DatasetsScripts.SecSelfAdapt import SecSelfAdapt
from Scripts.DatasetsScripts.SmellReprod import SmellReprod
from Scripts.DatasetsScripts.TestNN import TestNN
from Scripts.DatasetsScripts.TrustSE import TrustSE
from SRProject import *

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
    print(sr_project.df['project'].values[0])
    print("Number of blanks/NaN:", empty_counts)
    print("Number of articles:", len(file))
    print("Number of missing articles:", file['meta_title'].isna().sum())

    # TODO: check good number of lines exported
    # TODO: check for any unknown characters
    # TODO: check for right encoding
    # TODO: check for NaN or missing values


def cleanDataFrame(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.replace("–", "-")
    new_df = new_df.replace("©", '')
    new_df = new_df.replace(";;", ';')
    # new_df = new_df['keywords'].replace(",", ';')
    new_df = new_df.map(lambda x: x.strip() if isinstance(x, str) else x)
    new_df = new_df.replace("nan", '')
    new_df = new_df.fillna('')
    new_df = new_df.map(lambda x: ILLEGAL_CHARACTERS_RE.sub(r'',x) if isinstance(x, str) else x)
    return new_df


# Function to export to CSV the SRProject object
def ExportToCSV(sr_project):

    final_data_frame = sr_project.df

    final_data_frame = final_data_frame.drop(columns=["index",'key'])
    final_data_frame.to_csv(sr_project.export_path, sep="\t", index_label="key", encoding='utf-8')


def pre_process_sr_project(sr_project):
    title_counts = {}

    def make_unique(title):
        if title in title_counts:
            title_counts[title] += 1
            print(title)
            return f"{title} {title_counts[title]}"
        else:
            title_counts[title] = 1
            return title

    sr_project.df["title"] = sr_project.df["title"].apply(make_unique)


def read_sr_project(arg):
    return pd.read_csv(f"{MAIN_PATH}/Datasets/{arg}/{arg}.tsv", delimiter="\t")


def main(args=None):
    if args is None or not len(args) > 0:
        args = ['CodeCompr', "ArchiML", 'ModelingAssist', 'CodeClone']
        # args = ['CodeCompr']
    sr_project = None

    for arg in args:
        if arg == "ArchiML":  # missing
            sr_project = ArchiML()
        elif arg == "Behave":  # complete
            sr_project = Behave()
        elif arg == "CodeClone":  # missing
            sr_project = CodeClone()
        elif arg == "CodeCompr":  # missing
            sr_project = CodeCompr()
        elif arg == "DTCPS":  # complete
            sr_project = DTCPS()
        elif arg == "ESM_2":  # complete
            sr_project = ESM_2()
        elif arg == "ESPLE":  # complete
            sr_project = ESPLE()
        elif arg == "GameSE":  # complete
            sr_project = GameSE()
        elif arg == "GameSE_title":  # complete
            sr_project = GameSE_title()
        elif arg == "GameSE_abstract":  # complete
            sr_project = GameSE_abstract()
        elif arg == "ModelGuidance":  # 914 missing
            sr_project = ModelGuidance()
        elif arg == "ModelingAssist":  # 749 missing
            sr_project = ModelingAssist()
        elif arg == "OODP":  # 91 missing
            sr_project = OODP()
        elif arg == "SecSelfAdapt":  # complete
            sr_project = SecSelfAdapt()
        elif arg == "SmellReprod":  # complete
            sr_project = SmellReprod()
        elif arg == "TestNN":  # complete
            sr_project = TestNN()
        elif arg == "TrustSE":  # complete
            sr_project = TrustSE()
        elif arg == "Demo":
            sr_project = Demo()
        elif arg == "IFT3710":
            sr_project = IFT3710()
        else:
            print("Not a valid argument")
            continue

        pre_process_sr_project(sr_project)
        sr_project.df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}_pre-extract.xlsx")

        do_extraction = False
        if do_extraction:
            sr_compiled_project = read_sr_project(arg)
            # Keep only the rows that still need processing (meta_title is null/empty)
            unprocessed = sr_compiled_project[sr_compiled_project['meta_title'].isnull()]
            # Filter the original dataframe to only keep those rows
            titles_to_process = unprocessed['title']
            sr_project.df = sr_project.df[sr_project.df['title'].isin(titles_to_process)]
            sr_project.export_path = f"{MAIN_PATH}/Datasets/{arg}/{arg}_unprocessed.xlsx"

        # printEncoding(sr_project.path)  # to make sure we use the right encoding if necessary
        completed_df = findMissingMetadata.main(sr_project.df, do_extraction, 999)
        cleaned_df = cleanDataFrame(completed_df)
        sr_project.df = cleaned_df

        ExportToCSV(sr_project)
        # sys.stdout = sys.__stdout__127
        postProcessing(sr_project)

        # cleaned_df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}.xlsx")
        # sr_project.df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}_tmp.xlsx")


if __name__ == "__main__":
    main(sys.argv[1:])
