"""
TrustSE Systematic Literature Review Dataset Processing Script

Processes the TrustSE systematic review dataset on "A systematic literature review 
on trust in the software ecosystem" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: TrustSE (Trust in Software Ecosystem)
Paper: https://doi.org/10.1007/s10664-022-10238-y
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional


# Exclusion criteria descriptions for the TrustSE systematic review
EXCLUSION_CRITERIA_DESCRIPTIONS = {
'book': 'Studies that were books or gray literature',
'Book': 'Studies that were books or gray literature',
'Book cannot access': 'Studies that were books or gray literature',
'Cannot access': 'Studies that were not accessible in full-text',
'cannot access': 'Studies that were not accessible in full-text',
'incomplete paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Not a paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Not peer-reviewed': 'Studies that were not peer-reviewed',
'Short paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Tech Report': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'thesis': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Working paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
}


def convert_text_encoding(x):
    """
    Converts text encoding to ensure proper UTF-8 handling.
    
    Args:
        x (str): Input text to convert
        
    Returns:
        str: UTF-8 encoded text
    """
    # return x
    # x = x.replace("0xE20x800x99", "'")
    return x.encode('utf-8').decode('utf-8')


convert_dict = {"Title": convert_text_encoding}  # TODO: add other columns


class TrustSE(SRProject):
    """
    TrustSE Systematic Literature Review Dataset Handler.
    
    Processes the systematic review dataset on trust in the software ecosystem. 
    This dataset contains 556 articles with 112 included and 444 excluded 
    (20% inclusion rate).
    
    Dataset characteristics:
    - Size: 556 articles
    - Included: 112 articles
    - Excluded: 444 articles
    - Inclusion rate: 20%
    - Has conflict data: No
    - Criteria labeled: Yes
    - Has abstract text: No
    
    Processing notes: Exclusion criteria are not about content but format
    """

    def __init__(self):
        """
        Initialize the TrustSE dataset processor.
        
        Loads data from Excel sheet with selected manuscripts and SLR decisions.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/TrustSE/TrustSE-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="Selected manuscripts", header=1)  # 556 rows
            print(sheet_all)
            sheet_final = sheet_all.loc[sheet_all['SLR paper?'] == 'Yes']  # 112 rows
            print(sheet_final)


        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title"]
        # self.df['abstract'] = sheet_without_duplicates["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        # self.df["authors"] = sheet_without_duplicates["Author"]
        # self.df['venue'] = sheet_without_duplicates["Journal"]
        # self.df["doi"] = sheet_without_duplicates["URL"]
        # self.df["year"] = sheet_without_duplicates["Year"]
        # # self.df["year"].astype(int)
        # # self.df["references"]
        # # self.df["bibtex"]
        # self.df['mode'] = "new_screen"

        # Find all screened decisions
        self.find_decision_on_articles(sheet_final, sheet_all)
        self.df['final_decision'] = self.df['screened_decision']
        # self.find_decision_on_articles(sheet_abstract_included, sheet_title_keywords_included)
        #
        # # Add snowballing articles
        # self.add_snowballing_articles(sheet_snowballing)
        #
        # # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_final_selection, sheet_abstract_included, True)
        # self.find_decision_on_articles(sheet_final_selection, sheet_text_included, True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)

        self.df['project'] = "TrustSE"
        self.export_path = f"{MAIN_PATH}/Datasets/TrustSE/TrustSE.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Determine inclusion/exclusion decisions based on SLR paper status.
        
        Args:
            sheet_included (pd.DataFrame): DataFrame containing included articles
            sheet_criteria (pd.DataFrame): DataFrame containing all articles with decisions
            is_final (bool): Whether this is for final decision (True) or screened decision (False)
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        # criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        criteria = 'exclusion_criteria' if not is_final else 'exclusion_criteria'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, ["SLR paper?"]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        self.df.loc[self.df['title'] == article_title, criteria] = EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]


if __name__ == '__main__':
    try:
        sr_project = TrustSE()
        print('Dataset Summary:')
        print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
        print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['final_decision'] == 'Included'), 'Included')
    except Exception as e:
        print(f"Error processing TrustSE dataset: {e}")
