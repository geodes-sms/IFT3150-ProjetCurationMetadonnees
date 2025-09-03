"""
ModelingAssist Systematic Literature Review Dataset Processing Script

Processes the ModelingAssist systematic review dataset on "Understanding the Landscape 
of Software Modelling Assistants: A Systematic Mapping" for metadata curation and 
standardization.

Author: Guillaume Genois, 20248507
Dataset: ModelingAssist (Modeling Assistance Tools)
Paper: https://zenodo.org/records/10262145
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
import openpyxl


# Exclusion and inclusion criteria descriptions as defined in the original paper
EXCLUSION_CRITERIA_DESCRIPTIONS = {
    'I1': "Is the paper exclusively dedicated to a particular proposal, rather than being a compilation of proposals, aimed at assisting users during modelling tasks in MDSE tools? Compilation of proposals like literature reviews, systematic mappings, or systematic literature reviews does not fulfil I1.",
    'I2': "Is the proposal designed to assist users during modelling tasks in MDSE tools? We focus on proposals that assist users during modelling tasks in MDSE tools, including—but not limited to—modelling, model tracing, model debugging, model re-pair, and model validation, among others.",
    'E1': "The proposal’s main contribution is not to assist users during modelling in MDSE tools. If assisting users during modelling tasks is not the main contribution, we exclude the proposal using E1.",
    'E2': "The proposal is not related to software engineering.",
    'E3': "The proposal is not written in English",
    'E4': "The proposal is not a peer-reviewed publication",
    'E5': "The proposal's full text is not available."
}


class ModelingAssist(SRProject):
    """
    ModelingAssist Systematic Literature Review Dataset Processor
    
    Processes the systematic review on "Understanding the Landscape of Software 
    Modelling Assistants: A Systematic Mapping" for LLM training dataset creation.
    
    Dataset Characteristics:
        - Paper: https://zenodo.org/records/10262145 (under review)
        - Total Articles: 2,350
        - Included Articles: 132
        - Excluded Articles: 2,218
        - Inclusion Rate: 6%
        - Conflict Data: Yes
        - Criteria Labeled: Yes (2 inclusion + 5 exclusion criteria: I1-I2, E1-E5)
        - Abstract Text: No
        - Review Phases: Title screening → Abstract screening → Full-text review
        
    Processing Details:
        - Loads data from ModelingAssist-source.xlsx
        - Handles both database search and snowballing articles
        - Processes conflict resolution between reviewers
        - Maps inclusion and exclusion criteria to detailed descriptions
        - Two reviewers per article with conflict resolution process
    """

    def __init__(self):
        """
        Initialize ModelingAssist systematic review dataset processor.
        
        Loads and processes data from the ModelingAssist source Excel file with 
        multiple screening phases and conflict resolution.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/ModelingAssist/ModelingAssist-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="Database-Search-Data")  # 2613 rows
            print(sheet_all)
        sheet_without_duplicates = sheet_all.loc[sheet_all['Status'] != 'Duplicated']  # 2350
        sheet_screen_title = sheet_without_duplicates.loc[sheet_without_duplicates['Include after title screening?'] == 'YES']  # 1535
        sheet_screen_title_and_abstract = sheet_without_duplicates.loc[sheet_without_duplicates['Include after abstract screening?'] == 'YES']  # 132
        sheet_screen_full_text = sheet_screen_title_and_abstract.loc[sheet_screen_title_and_abstract['Include after full-text review?'] == 'YES']  # 63
        sheet_screen_non_conflicted = sheet_screen_full_text.loc[sheet_screen_full_text['Include after second reviewer opinion? '] == 'YES']  # 63
        sheet_screen_final = sheet_screen_full_text.loc[sheet_screen_full_text['Include after discussion?'] == 'YES']  # 44 : Status == Included

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_without_duplicates["Title"]
        # self.df['abstract'] = sheet_without_duplicates["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        # self.df["authors"] = sheet_without_duplicates["author"]
        # self.df['venue'] = sheet_without_duplicates["journal"]
        # self.df["doi"] = sheet_without_duplicates["doi"]
        self.df["year"] = sheet_without_duplicates["year"]
        # self.df["link"] = sheet_without_duplicates["url"]
        # self.df["pages"] = sheet_without_duplicates["pages"]
        # self.df["publisher"] = sheet_without_duplicates["publisher"]
        # self.df["source"] = self.find_source(sheet_without_duplicates["publisher"])
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = ['snowballing' if not pd.isna(s) else 'new_screen' for s in sheet_without_duplicates['Strategy']]

        # Find all screened decisions
        self.find_decision_on_articles(sheet_screen_title, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')
        self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_screen_final, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria', True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "ModelingAssist"
        self.export_path = f"{MAIN_PATH}/Datasets/ModelingAssist/ModelingAssist.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, sheet_criteria, criteria_column, is_final=False):
        """
        Process article screening decisions with conflict resolution support.
        
        Args:
            sheet_included: DataFrame containing articles that passed this screening phase
            sheet_criteria: DataFrame containing all articles with exclusion criteria
            criteria_column: Column name containing criteria information
            is_final: Whether this is final decision processing (vs. screened decision)
            
        Note:
            ModelingAssist includes conflict resolution between two reviewers.
            Conflicts are marked as ConflictIncluded or ConflictExcluded.
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                conflicted_decision = "Included"
                if is_final:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if row['Include after second reviewer opinion? '].values[0] != row['Include after full-text review?'].values[0]:
                        conflicted_decision = "ConflictIncluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision
            else:
                conflicted_decision = "Excluded"
                if is_final and article_title in sheet_criteria['Title'].values:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if row['Include after second reviewer opinion? '].values[0] != row['Include after full-text review?'].values[0]:
                        conflicted_decision = "ConflictExcluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, [criteria_column]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        criteria = 'exclusion_criteria' if exclusion_criteria[0] == 'E' else 'inclusion_criteria'
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]


    def find_source(self, publishers):
        """
        Map publisher names to standardized source categories.
        
        Args:
            publishers: List of publisher names from source data
            
        Returns:
            List of standardized source names (ACM, ScienceDirect, IEEE, Springer, etc.)
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
    """
    Main execution block for testing ModelingAssist dataset processing.
    """
    try:
        sr_project = ModelingAssist()
        print(f"\nModelingAssist Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with years: {sr_project.df['year'].notna().sum()}")
        print(f"Database search articles: {(sr_project.df['mode'] == 'new_screen').sum()}")
        print(f"Snowballing articles: {(sr_project.df['mode'] == 'snowballing').sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts (preserving original format)
        if 'screened_decision' in sr_project.df.columns:
            print('\nscreened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
            
        if 'final_decision' in sr_project.df.columns:
            print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['final_decision'] == 'Included'), 'Included')
            
        # Display conflict information
        conflict_included = (sr_project.df['final_decision'] == 'ConflictIncluded').sum()
        conflict_excluded = (sr_project.df['final_decision'] == 'ConflictExcluded').sum()
        if conflict_included > 0 or conflict_excluded > 0:
            print(f"Conflicts: {conflict_included} ConflictIncluded, {conflict_excluded} ConflictExcluded")
            
    except Exception as e:
        print(f"Error running ModelingAssist processing: {e}")
