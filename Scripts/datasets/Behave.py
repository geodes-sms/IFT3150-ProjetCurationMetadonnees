"""
Behave Systematic Literature Review Dataset Processing Script

Processes the Behave systematic review dataset on "Behavioral Software Engineering" 
for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: Behave (Behavioral Software Engineering)
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional


# Exclusion criteria descriptions as defined in the original paper
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


def convert_text_encoding(text: str) -> str:
    """
    Converts text encoding to ensure proper UTF-8 handling.
    
    Args:
        text (str): Input text to convert
        
    Returns:
        str: UTF-8 encoded text
    """
    if isinstance(text, str):
        return text.encode('utf-8').decode('utf-8')
    return text


convert_dict = {"Title": convert_text_encoding}


class Behave(SRProject):
    """
    Behave Systematic Literature Review Dataset Processor
    
    Processes the systematic review on "Behavioral Software Engineering" 
    for LLM training dataset creation.
    
    Dataset Characteristics:
        - Dataset: Behave (Behavioral Software Engineering)
        - Total Articles: 1,043
        - Focus: Human factors and behavioral aspects in software engineering
        - Abstract Text: Available
        - Review Process: Multi-phase screening with exclusion criteria
        
    Processing Details:
        - Loads data from Behave-source.xlsx
        - Maps exclusion criteria to original paper descriptions
        - Handles UTF-8 encoding for international characters
        - Processes screening decisions with detailed criteria tracking
    """
    """
    Behaviour driven development: A systematic mapping study
    https://doi.org/10.1016/j.jss.2023.111749
    Size: 601
    Included: 148
    Excluded: 453
    Inclusion rate: 25%
    Has Conflict data: No
    Criteria labeled: No
    Has abstract text: Some
    Comment: For some articles, full-text needed
    Need to subtract the two lists to get excluded articles
    """

    def __init__(self):
        """
        Initialize Behave systematic review dataset processor.
        
        Loads and processes data from the Behave source Excel file.
        """
        super().__init__()
        # self.path = "../../Datasets/Behave/Behave-source.xlsx"
        self.path = f"{MAIN_PATH}/Datasets/Behave/Behave-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="all citations")  # 601 rows
            print(sheet_all)
            sheet_final = pd.read_excel(f, sheet_name="final_data_from_database_search")  # 148 rows
            print(sheet_final)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["title"]
        self.df['abstract'] = sheet_all["abstract"]
        self.df["keywords"] = sheet_all["keywords"]
        self.df["authors"] = sheet_all["authors"]
        self.df['venue'] = sheet_all["journal"]
        self.df["doi"] = sheet_all["abstract"]
        # self.df["year"] = sheet_all["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened and final decisions
        self.find_decision_on_articles(sheet_final, sheet_all)

        self.df["reviewer_count"] = 2  # TODO: verify

        self.df['project'] = "Behave"
        self.export_path = f"{MAIN_PATH}/Datasets/Behave/Behave.tsv"
        
        print(f"Behave dataset initialized with {len(self.df)} articles")

    def find_decision_on_articles(self, sheet_included, sheet_criteria):
        """
        Process article screening decisions by comparing titles across sheets.
        
        Args:
            sheet_included: DataFrame containing included articles
            sheet_criteria: DataFrame containing all articles with criteria
            
        Note:
            In Behave, screening and final decisions are equivalent.
        """
        for article_title in self.df['title'].values:
            if pd.isna(article_title) or article_title == "":
                continue
                
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Included"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Excluded"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Excluded"


if __name__ == '__main__':
    """
    Main execution block for testing Behave dataset processing.
    """
    try:
        sr_project = Behave()
        print(f"\nBehave Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with abstracts: {sr_project.df['abstract'].notna().sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts (preserving original format)
        if 'screened_decision' in sr_project.df.columns:
            print('\nscreened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
            
        if 'final_decision' in sr_project.df.columns:
            print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['final_decision'] == 'Included'), 'Included')
            
    except Exception as e:
        print(f"Error running Behave processing: {e}")