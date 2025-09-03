"""
ESM_2 Systematic Literature Review Dataset Processing Script

Processes the ESM_2 systematic review dataset on "Adaptive user interfaces in 
systems targeting chronic disease" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: ESM_2 (Adaptive User Interfaces for Chronic Disease Systems)
Paper: https://doi.org/10.48550/arXiv.2211.09340
"""

from Scripts.core.SRProject import SRProject
import pandas as pd
from typing import Dict, Optional

from Scripts.core.os_path import MAIN_PATH

# Publisher code mappings for source identification
code_publisher = {
    'ACM': 'ACM',
    'IEE': 'IEEE',
    'SCO': 'Scopus',
    'MED': 'Medline',
    'SCI': 'ScienceDirect',
    'SPR': 'Springer Link'
}

# No exclusion criteria descriptions available - articles processed differently
EXCLUSION_CRITERIA_DESCRIPTIONS = {}


class ESM_2(SRProject):
    """
    ESM_2 Systematic Literature Review Dataset Handler.
    
    Processes the systematic review dataset on adaptive user interfaces in systems
    targeting chronic disease. This dataset contains 114 articles with 61 included
    and 53 excluded (54% inclusion rate).
    
    Dataset characteristics:
    - Size: 114 articles
    - Included: 61 articles
    - Excluded: 53 articles
    - Inclusion rate: 54%
    - Has conflict data: No
    - Criteria labeled: Yes
    - Has abstract text: Yes
    
    Note: Numbers don't match paper exactly, initial papers not available. 
    Criteria labeled do not match exclusion criteria in paper.
    """

    def __init__(self):
        """
        Initialize the ESM_2 dataset processor.
        
        Loads data from the ESM_2 source Excel file and processes both abstract
        and full-text screening phases.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/ESM_2/ESM_2-source.xlsx"
        sheet_abstract = pd.read_excel(self.path, sheet_name="Abstract")  # 114
        sheet_final = pd.read_excel(self.path, sheet_name="Intro+method+conclusion")  # 61

        # self.project = "ESM_2"
        # self.key = sheet_abstract["Number"]
        # self.authors = sheet_abstract["Author"]
        # self.title = sheet_abstract["Titile"]
        # self.abstract = sheet_abstract["Abstract"]
        # self.screened_decision = sheet_abstract["Decision"]
        # self.mode = "new_screen"

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_abstract["Titile"]
        self.df['abstract'] = sheet_abstract["Abstract"]
        # self.df["keywords"] = sheet_abstract["Keywords"]
        self.df["authors"] = sheet_abstract["Author"]
        # self.df['venue'] = sheet_abstract["Journal"]
        # self.df["doi"] = sheet_abstract["URL"]
        # self.df["year"] = sheet_abstract["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "snowballing"  # we don't have the original screening
        # self.df['publisher'] = [code_publisher[e[:3]] for e in sheet_abstract['Number']]
        # self.df['source'] = self.df['publisher']

        # Find all screened decisions
        self.find_decision_on_articles(sheet_final, sheet_abstract)

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_final, sheet_final, True)
        self.df.loc[self.df['screened_decision'] == 'Excluded', 'final_decision'] = 'Excluded'

        self.df["reviewer_count"] = 2  # TODO: to be verified

        self.df['title'] = self.df['title'].str[:-1]

        self.df['project'] = "ESM_2"
        self.export_path = f"{MAIN_PATH}/Datasets/ESM_2/ESM_2.tsv"
        print(self.df[['screened_decision', 'final_decision', 'exclusion_criteria']])

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Determine inclusion/exclusion decisions for articles based on different screening phases.
        
        Args:
            sheet_included (pd.DataFrame): DataFrame containing included articles
            sheet_criteria (pd.DataFrame): DataFrame containing all articles with decisions
            is_final (bool): Whether this is for final decision (True) or screened decision (False)
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        for idx, row in sheet_criteria.iterrows():
            article_title = row["Titile"]

            if row['Decision'] == 'In':
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
                print(self.df.loc[self.df['title'] == article_title])
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                criteria = 'exclusion_criteria'
                exclusion_criteria = sheet_criteria.loc[sheet_criteria["Titile"] == article_title, ["Note"]].values[0][0]
                if not pd.isna(exclusion_criteria):
                    self.df.loc[self.df['title'] == article_title, criteria] = self.clean_exclusion_criteria(exclusion_criteria)

    def clean_exclusion_criteria(self, exclusion_criteria):
        """
        Clean and format exclusion criteria text.
        
        Args:
            exclusion_criteria (str): Raw exclusion criteria text
            
        Returns:
            str: Cleaned exclusion criteria text
        """
        return exclusion_criteria


if __name__ == '__main__':
    try:
        sr_project = ESM_2()
        print('Dataset Summary:')
        print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
        print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['final_decision'] == 'Included'), 'Included')
    except Exception as e:
        print(f"Error processing ESM_2 dataset: {e}")
