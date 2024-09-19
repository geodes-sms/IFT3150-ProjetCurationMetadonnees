# -*- coding: utf-8 -*-
import chardet
import sys

from SRProject import *
from Scripts.DatasetsScripts.ESM_2 import ESM_2
from Scripts.DatasetsScripts.CodeClone import CodeClone
from Scripts.DatasetsScripts.GameSE import GameSE

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


# Temporary function to test and compare the results of the script with the reference datasets
def tmp_ExportToCSV(sr_project):
    final_data_frame = pd.DataFrame(columns=["project", "key", "title", "abstract", "doi", "decision", "mode",
                                             "exclusion_criteria", "reviewer_count"], dtype=str)
    final_data_frame["project"] = sr_project.project
    final_data_frame["key"] = sr_project.key
    final_data_frame["title"] = sr_project.title
    final_data_frame["abstract"] = sr_project.abstract
    final_data_frame["doi"] = sr_project.references
    final_data_frame["decision"] = sr_project.screened_decision
    final_data_frame["mode"] = sr_project.mode
    final_data_frame["exclusion_criteria"] = sr_project.exclusion_criteria
    final_data_frame["reviewer_count"] = sr_project.reviewer_count
    final_data_frame.to_csv(sr_project.export_path, sep="\t", index=False)


class LC(SRProject):
    """Reference dataset to test the code"""
    def __init__(self):
        super().__init__()
        self.path = "Reference datasets/lc.csv"
        sheet_abstract = pd.read_csv(self.path, sep="\t", encoding='utf-8')

        self.key = sheet_abstract["key"]
        self.project = sheet_abstract["project"]
        self.title = sheet_abstract["title"]
        self.abstract = sheet_abstract["abstract"]
        self.references = sheet_abstract["doi"]
        self.screened_decision = sheet_abstract["decision"]
        self.mode = sheet_abstract["mode"]
        self.exclusion_criteria = sheet_abstract["exclusion_criteria"]
        self.reviewer_count = sheet_abstract["reviewer_count"]

        self.export_path = "Reference datasets/lc_replicated.tsv"


def main(args=None):
    if args is None or not len(args) > 0:
        args = ["lc"]
    sr_project = None

    for arg in args:
        if arg == "CodeClone":
            sr_project = CodeClone()
        elif arg == "AUI" or arg == "ESM_2":
            sr_project = ESM_2()
        elif arg == "lc":
            sr_project = LC()
        elif arg == "GameSE":
            sr_project = GameSE()

        printEncoding(sr_project.path)  # to make sure we use the right encoding if necessary
        tmp_ExportToCSV(sr_project)  # only for the reference
        postProcessing(sr_project)


if __name__ == "__main__":
    main(sys.argv[1:])
