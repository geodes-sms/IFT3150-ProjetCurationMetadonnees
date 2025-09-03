"""
TestNN Systematic Literature Review Dataset Processing Script

Processes the TestNN systematic review dataset on "Testing and verification of 
neural-network-based safety-critical control software" for metadata curation 
and standardization.

Author: Guillaume Genois, 20248507
Dataset: TestNN (Testing Neural Networks in Safety-Critical Systems)
Paper: https://www.sciencedirect.com/science/article/pii/S0950584920300471
"""

from Scripts.core.SRProject import SRProject, empty_df
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional

# No exclusion criteria descriptions available - criteria are embedded in data
EXCLUSION_CRITERIA_DESCRIPTIONS = {}


class TestNN(SRProject):
    """
    TestNN Systematic Literature Review Dataset Handler.
    
    Processes the systematic review dataset on testing and verification of neural-network-based 
    safety-critical control software. This dataset contains 105 articles with 27 included 
    and 78 excluded (26% inclusion rate).
    
    Dataset characteristics:
    - Size: 105 articles (plus snowballing articles)
    - Included: 27 articles
    - Excluded: 78 articles
    - Inclusion rate: 26%
    - Has conflict data: No
    - Criteria labeled: No
    - Has abstract text: No
    
    Processing notes: Title screening not available, includes snowballing articles
    """

    def __init__(self):
        """
        Initialize the TestNN dataset processor.
        
        Loads data from multiple Excel sheets including main screening and snowballing results.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/TestNN/TestNN-source.xlsx"
        sheet_abstract = pd.read_excel(self.path, sheet_name="Stage3(105)")
        sheet_abstract_final = pd.read_excel(self.path, sheet_name="Stage4(27)")
        sheet_snowballing = pd.read_excel(self.path, sheet_name="Stage5_snowballing_inital(70)")
        sheet_snowballing_final = pd.read_excel(self.path, sheet_name="Stage5_snowballing_result (56)")

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_abstract["Title"]
        # self.df['abstract'] = sheet_abstract["Abstract"]
        # self.df["keywords"] = sheet_abstract["Keywords"]
        self.df["authors"] = sheet_abstract["Author"]
        self.df['venue'] = sheet_abstract["Journal/conference"]
        # self.df["doi"] = sheet_abstract["URL"]
        self.df["year"] = sheet_abstract["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened decisions
        self.find_decision_on_articles(sheet_abstract_final, sheet_abstract)
        tmp_df = self.df
        self.df = empty_df.copy()

        # Add snowballing articles
        self.add_snowballing_articles(sheet_snowballing)
        self.find_decision_on_articles(sheet_snowballing_final, sheet_snowballing)

        self.df = pd.concat([tmp_df, self.df], ignore_index=True)

        # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_final, sheet_abstract, True)
        # self.find_decision_on_articles(sheet_final, sheet_snowballing, True)

        self.df["reviewer_count"] = 1

        # self.df["doi"].astype(str)

        self.df['project'] = "TestNN"
        self.export_path = f"{MAIN_PATH}/Datasets/TestNN/TestNN.tsv"
        print(self.df)

    def add_snowballing_articles(self, sheet_snowballing):
        """
        Add articles found through snowballing to the dataset.
        
        Args:
            sheet_snowballing (pd.DataFrame): DataFrame containing snowballing articles
        """
        snowball_df = empty_df.copy()
        snowball_df[['title', 'authors', 'year']] = sheet_snowballing[["Title", "Author(s)", "Year"]]
        snowball_df['mode'] = "snowballing"
        decision = 'screened_decision'
        criteria = 'exclusion_criteria'
        for article_title in snowball_df['title'].values:
            if article_title in sheet_snowballing["Title"].values:
                exclusion_criteria = sheet_snowballing.loc[
                    sheet_snowballing["Title"] == article_title, ["Inclusion or Exclusion Reason"]].values[0][0]
                if not pd.isna(exclusion_criteria):
                    self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " # + \excl_crit_desc[exclusion_criteria]
        self.df = pd.concat([self.df, snowball_df], ignore_index=True)
        # TODO: missing keywords, url for these articles
        # TODO: missing exclusion criteria on different page than other articles

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Determine inclusion/exclusion decisions for articles.
        
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
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Included"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Excluded"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Excluded"
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title]["Inclusion or Exclusion Reason"].values[0]
                    if not pd.isna(exclusion_criteria):
                        self.df.loc[self.df['title'] == article_title, criteria] = self.reformat_exclusion_criteria(exclusion_criteria)  # + excl_crit_desc[exclusion_criteria]

    def reformat_exclusion_criteria(self, exclusion_criteria):
        """
        Reformat exclusion criteria text for consistency.
        
        Args:
            exclusion_criteria (str): Raw exclusion criteria text
            
        Returns:
            str: Reformatted exclusion criteria text
        """
        return exclusion_criteria[:9] + ": " + exclusion_criteria[10:]


if __name__ == '__main__':
    try:
        sr_project = TestNN()
        print('Dataset Summary:')
        print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
        print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
              sum(sr_project.df['final_decision'] == 'Included'), 'Included')
    except Exception as e:
        print(f"Error processing TestNN dataset: {e}")