"""
ModelGuidance Systematic Literature Review Dataset Processing Script

Processes the ModelGuidance systematic review dataset on "Modelling guidance in 
software engineering" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: ModelGuidance (Modelling Guidance in Software Engineering)
Paper: https://doi.org/10.1007/s10270-023-01117-1
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional


# Exclusion criteria descriptions for the ModelGuidance systematic review
EXCLUSION_CRITERIA_DESCRIPTIONS = {
    "Duplicated": "Studies that were duplicates of other studies.",
    "Written in other languages": "Studies that were not written in English.",
    "Before 2009": "Studies that were not published online between 2009 to 2021.",
    "Non-peer reviewed": "Studies presenting non-peer-reviewed material.",
    "Proceedings": "Studies presenting peer-reviewed but not published in journals, conferences, or workshops.",
    "Proceedings and posters": "Studies presenting peer-reviewed but not published in journals, conferences, or workshops.",
    "Summaries of conferences/editorials": "Studies that were summaries of conferences/editorials.",
    "Not primary study": "Non-primary studies.",
    "Serious games or gamification": "Studies that were focused on the social and educational impact of video games, such as serious games.",
    "AI": "Studies that were focused on Artificial Intelligence (AI).",
    "Content Creation": "Studies that were focused on Content Creation.",
    "Not related to Software Engineering": "Studies that were not in the field of Software Engineering.",
    "Not related to Video Games": "Studies that were not focused on software engineering applied to industry-scale computer games development.",
    "Not sure": ""
}


class ModelGuidance(SRProject):
    """
    ModelGuidance Systematic Literature Review Dataset Handler.
    
    Processes the systematic review dataset on modelling guidance in software 
    engineering. This dataset contains 1776 articles with 221 included and 1555 
    excluded (12% inclusion rate).
    
    Dataset characteristics:
    - Size: 1776 articles
    - Included: 221 articles
    - Excluded: 1555 articles
    - Inclusion rate: 12%
    - Has conflict data: Yes
    - Criteria labeled: No
    - Has abstract text: Yes
    
    Processing notes: 2 phases - Title screening then abstract screening
    """

    def __init__(self):
        """
        Initialize the ModelGuidance dataset processor.
        
        Loads data from multiple Excel sheets representing different screening phases.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/ModelGuidance/ModelGuidance-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all_1 = pd.read_excel(f, sheet_name="step1title_venue_search1")  # 8604 rows
            sheet_all_2 = pd.read_excel(f, sheet_name="step1title_venue_search2")  # 3573 rows
            sheet_all = pd.concat([sheet_all_1, sheet_all_2])  # 12 177
            print(sheet_all)
            sheet_abstract_1 = pd.read_excel(f, sheet_name="step2abstract_search1")  # 1008 rows
            sheet_abstract_2 = pd.read_excel(f, sheet_name="step2abstract_search2")  # 768 rows
            sheet_abstract = pd.concat([sheet_abstract_1, sheet_abstract_2])  # 1776
            print(sheet_abstract)
            sheet_text_1 = pd.read_excel(f, sheet_name="step3fulltext_search1")  # 111 rows
            sheet_text_2 = pd.read_excel(f, sheet_name="step3fulltext_search3")  # 110 rows
            sheet_text = pd.concat([sheet_text_1, sheet_text_2])  # 221
            print(sheet_text)
            sheet_final = pd.read_excel(f, sheet_name="step4analysis")  # 22 rows
            print(sheet_final)

        # TODO: to be changed to normal
        sheet_all = sheet_abstract

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title"]
        # self.df['abstract'] = sheet_all["Abstract"]
        # self.df["keywords"] = sheet_abstract["Keywords"]
        self.df["authors"] = sheet_all["Author"]
        self.df['venue'] = sheet_all["Venue"]
        # self.df["doi"] = sheet_abstract["doi"]
        self.df["year"] = sheet_all["Year"]
        # self.df["link"] = sheet_abstract["url"]
        # self.df["pages"] = sheet_abstract["pages"]
        # self.df["publisher"] = sheet_abstract["publisher"]
        # self.df["source"] = self.find_source(sheet_abstract["publisher"])
        # self.df["references"]
        # self.df["bibtex"]
        # self.df['mode'] = ['snowballing' if s != 'None' else 'new_screen' for s in sheet_abstract['Snowballing']]
        self.df['mode'] = 'new_screen'

        # Find all screened decisions
        # self.find_decision_on_articles(sheet_abstract, sheet_all)
        self.find_decision_on_articles(sheet_text, sheet_abstract)

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_final, None, True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "ModelGuidance"
        self.export_path = f"{MAIN_PATH}/Datasets/ModelGuidance/ModelGuidance.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Determine inclusion/exclusion decisions and detect conflicts between reviewers.
        
        Args:
            sheet_included (pd.DataFrame): DataFrame containing included articles
            sheet_criteria (pd.DataFrame): DataFrame containing screening decisions with reviewer info
            is_final (bool): Whether this is for final decision (True) or screened decision (False)
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        # criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        criteria = 'exclusion_criteria' if not is_final else 'exclusion_criteria'

        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                conflicted_decision = "Included"
                if not is_final and article_title in sheet_criteria['Title'].values:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if ((row['YES/NO (SC)'].values[0] != row['YES/NO (GL)'].values[0] and not pd.isna(
                            row['YES/NO (SC)'].values[0]) and not pd.isna(row['YES/NO (GL)'].values[0])) or
                            (row['YES/NO (SC) 2nd time'].values[0] != row['YES/NO (GL) 2nd time'].values[
                                0] and not pd.isna(row['YES/NO (SC) 2nd time'].values[0]) and not pd.isna(
                                row['YES/NO (SC) 2nd time'].values[0]))):
                        conflicted_decision = "ConflictIncluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision
            else:
                conflicted_decision = "Excluded"
                if not is_final and article_title in sheet_criteria['Title'].values:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if ((row['YES/NO (SC)'].values[0] != row['YES/NO (GL)'].values[0] and not pd.isna(row['YES/NO (SC)'].values[0]) and not pd.isna(row['YES/NO (GL)'].values[0])) or
                            (row['YES/NO (SC) 2nd time'].values[0] != row['YES/NO (GL) 2nd time'].values[0] and not pd.isna(row['YES/NO (SC) 2nd time'].values[0]) and not pd.isna(row['YES/NO (SC) 2nd time'].values[0]))):
                        conflicted_decision = "ConflictExcluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision

    def find_source(self, publishers):
        """
        Map publisher names to standardized source identifiers.
        
        Args:
            publishers (list): List of publisher names
            
        Returns:
            list: List of standardized source names
        """
        results = []
        for pub in publishers:
            if pd.isna(pub):
                results.append(pub)
            elif 'ACM' in pub or 'Association for Computing Machinery' in pub or 'ICST' in pub:
                results.append('ACM')
            elif 'Elsevier' in pub or 'Academic Press' in pub:
                results.append('ScienceDirect')
            elif 'IEEE' in pub or 'Institute of Electrical and Electronics Engineers' in pub:
                results.append('IEEE')
            elif 'Springer' in pub:
                results.append('Springer')
            else:
                results.append(pub)
        return results


if __name__ == '__main__':
    try:
        sr_project = ModelGuidance()
        print('Dataset Summary:')
        print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['screened_decision'] == 'Included'), 'Included,',
              sum(sr_project.df['screened_decision'] == 'ConflictExcluded'), 'ConflictExcluded,',
              sum(sr_project.df['screened_decision'] == 'ConflictIncluded'), 'ConflictIncluded')
        print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['final_decision'] == 'Included'), 'Included,',
              sum(sr_project.df['final_decision'] == 'ConflictExcluded'), 'ConflictExcluded,',
              sum(sr_project.df['final_decision'] == 'ConflictIncluded'), 'ConflictIncluded')
    except Exception as e:
        print(f"Error processing ModelGuidance dataset: {e}")
