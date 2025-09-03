"""
ESPLE Systematic Literature Review Dataset Processing Script

Processes the ESPLE systematic review dataset on "Empirical software product line 
engineering" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: ESPLE (Empirical Software Product Line Engineering)
Paper: https://www.sciencedirect.com/science/article/pii/S0950584920301555
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
import openpyxl
from typing import Dict, Optional


# Exclusion criteria descriptions for the ESPLE systematic review
EXCLUSION_CRITERIA_DESCRIPTIONS = {
    'I1': "Is the paper exclusively dedicated to a particular proposal, rather than being a compilation of proposals, aimed at assisting users during modelling tasks in MDSE tools? Compilation of proposals like literature reviews, systematic mappings, or systematic literature reviews does not fulfil I1.",
    'I2': "Is the proposal designed to assist users during modelling tasks in MDSE tools? We focus on proposals that assist users during modelling tasks in MDSE tools, including—but not limited to—modelling, model tracing, model debugging, model re-pair, and model validation, among others.",
    'E1': "The proposal’s main contribution is not to assist users during modelling in MDSE tools. If assisting users during modelling tasks is not the main contribution, we exclude the proposal using E1.",
    'E2': "The proposal is not related to software engineering.",
    'E3': "The proposal is not written in English",
    'E4': "The proposal is not a peer-reviewed publication",
    'E5': "The proposal's full text is not available."
}


def clean_title_for_search(title):
    """
    Clean title by removing curly braces used in BibTeX formatting.
    
    Args:
        title (str): Original title with potential braces
        
    Returns:
        str: Cleaned title without braces
    """
    if not title or len(title) == 0:
        return title
    if title[-1] == '}':
        title = title[:-1]
    if title[0] == '{':
        title = title[1:]
    return title


class ESPLE(SRProject):
    """
    ESPLE Systematic Literature Review Dataset Handler.
    
    Processes the systematic review dataset on empirical software product line 
    engineering. This dataset contains 963 articles with 60 included and 903 
    excluded (6% inclusion rate).
    
    Dataset characteristics:
    - Size: 963 articles
    - Included: 60 articles
    - Excluded: 903 articles
    - Inclusion rate: 6%
    - Has conflict data: No
    - Criteria labeled: No
    - Has abstract text: No
    """

    def __init__(self):
        """
        Initialize the ESPLE dataset processor.
        
        Loads data from TSV files containing filtered and screened articles.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/ESPLE"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path + "/ESPLE-filtered-source.tsv", 'rb') as f:
            sheet_all = pd.read_csv(f, sep='\t')  # 963 rows
            sheet_all['title'] = sheet_all['title'].apply(lambda x: x.replace("{", "").replace("}", ""))
            print(sheet_all['title'])

        with open(self.path + "/ESPLE-screened-source.tsv", 'rb') as f:
            sheet_final = pd.read_csv(f, sep='\t')  # 60 rows
            sheet_final['title'] = sheet_final['title'].apply(lambda x: x.replace("{", "").replace("}", ""))
            print(sheet_final['title'])

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["title"]
        self.df['abstract'] = sheet_all["abstract"]
        # self.df["keywords"] = sheet_all["Keywords"]
        self.df["authors"] = sheet_all["author"]
        self.df['venue'] = sheet_all["journal"]
        self.df["doi"] = sheet_all["paper"]
        self.df["year"] = sheet_all["year"]
        self.df["link"] = sheet_all["paper"]
        self.df["pages"] = sheet_all["pages"]
        self.df["publisher"] = sheet_all["publisher"]
        # self.df["source"] = self.find_source(sheet_all["publisher"])
        # self.df["references"]
        # self.df["bibtex"]
        # self.df['mode'] = ['snowballing' if not pd.isna(s) else 'new_screen' for s in sheet_without_duplicates['Strategy']]

        # Find all screened decisions
        self.find_decision_on_articles(sheet_final)
        self.df['final_decision'] = self.df['screened_decision']
        # self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')

        # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_screen_final, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria', True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "ESPLE"
        self.export_path = f"{MAIN_PATH}/Datasets/ESPLE/ESPLE.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included):
        """
        Determine inclusion/exclusion decisions by comparing against included articles list.
        
        Args:
            sheet_included (pd.DataFrame): DataFrame containing included articles
        """
        decision = 'screened_decision'
        print(self.df["title"].values)
        print(sheet_included['title'].values)
        for article_title in self.df['title'].values:
            if standardize_title(article_title) in sheet_included["title"].apply(standardize_title).values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"


if __name__ == '__main__':
    try:
        sr_project = ESPLE()
        print('Dataset Summary:')
        print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
        print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['final_decision'] == 'Included'), 'Included')
        sr_project.df.to_excel('esple.xlsx')
    except Exception as e:
        print(f"Error processing ESPLE dataset: {e}")

