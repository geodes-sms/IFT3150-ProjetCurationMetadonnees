"""
OODP Systematic Literature Review Dataset Processing Script

Processes the OODP systematic review dataset on "A mapping study of language features 
improving object-oriented design patterns" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: OODP (Object-Oriented Design Patterns)
Paper: https://doi.org/10.1016/j.infsof.2023.107222
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
import openpyxl


# Note: OODP dataset does not have labeled exclusion criteria
# Articles are simply classified as included/excluded without specific criteria codes


class OODP(SRProject):
    """
    OODP Systematic Literature Review Dataset Processor
    
    Processes the systematic review on "A mapping study of language features 
    improving object-oriented design patterns" for LLM training dataset creation.
    
    Dataset Characteristics:
        - Paper: https://doi.org/10.1016/j.infsof.2023.107222
        - Total Articles: 685
        - Included Articles: 34
        - Excluded Articles: 651
        - Inclusion Rate: 5%
        - Conflict Data: No
        - Criteria Labeled: No
        - Abstract Text: Yes
        - Review Phases: Single-phase screening
        
    Processing Details:
        - Loads data from OODP-source.xlsx with two sheets
        - Combines query results with manually included articles
        - Simple binary classification (included/excluded)
        - Contains full abstract text for content analysis
        - No specific exclusion criteria codes used
        
    Note:
        Numbers may not exactly match the paper due to query re-execution
        by the original authors to provide complete article lists.
    """

    def __init__(self):
        """
        Initialize OODP systematic review dataset processor.
        
        Loads and processes data from the OODP source Excel file with query results
        and manually included articles.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/OODP/OODP-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="query results")  # 685 rows
            print(sheet_all)
            sheet_final = pd.read_excel(f, sheet_name="Included")  # 34 rows
            print(sheet_final)
            sheet_final.drop(['Number', 'Type', 'Subjects', 'Subject Type', 'Venue Type'], inplace=True, axis=1)
            sheet_final.rename(columns={'Name': 'Title', 'Year': 'Publication year', 'Publication Venue': 'Source'}, inplace=True)
            sheet_all = pd.concat([sheet_all, sheet_final], ignore_index=True)
            sheet_all.drop_duplicates(subset=['Title'], inplace=True)
            print(sheet_all)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title"]
        self.df['abstract'] = sheet_all["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        self.df["authors"] = sheet_all["Author"]
        self.df['venue'] = sheet_all["Source"]
        self.df["doi"] = sheet_all["DOI"]
        self.df["year"] = sheet_all["Publication year"]
        # self.df["link"] = sheet_without_duplicates["url"]
        self.df["pages"] = sheet_all["Pages"]
        self.df["publisher"] = sheet_all["Publisher"]
        # self.df["source"] = sheet_all["Source"]
        # self.df["year"].astype(int)
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
        self.df.loc[~self.df['doi'].isna(), 'doi'] = "https://doi.org/" + self.df.loc[~self.df['doi'].isna(), 'doi']
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "OODP"
        self.export_path = f"{MAIN_PATH}/Datasets/OODP/OODP.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, is_final=False):
        """
        Process article screening decisions using simple included/excluded classification.
        
        Args:
            sheet_included: DataFrame containing articles that were included
            is_final: Whether this is final decision processing (vs. screened decision)
            
        Note:
            OODP uses simple binary classification without specific exclusion criteria.
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"


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
    Main execution block for testing OODP dataset processing.
    """
    try:
        sr_project = OODP()
        print(f"\nOODP Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with abstracts: {sr_project.df['abstract'].notna().sum()}")
        print(f"Articles with authors: {sr_project.df['authors'].notna().sum()}")
        print(f"Articles with DOIs: {sr_project.df['doi'].notna().sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts (preserving original output)
        if 'screened_decision' in sr_project.df.columns:
            print(f"\nScreening decisions:")
            print(sr_project.df['screened_decision'].value_counts())
            
        if 'final_decision' in sr_project.df.columns:
            print(f"\nFinal decisions:")
            print(sr_project.df['final_decision'].value_counts())
            
    except Exception as e:
        print(f"Error running OODP processing: {e}")
