"""
ArchiML Systematic Literature Review Dataset Processing Script

Processes the ArchiML systematic review dataset on "Architecting ML-enabled systems: 
Challenges, best practices, and design decisions" for metadata curation and 
standardization.

Author: Guillaume Genois, 20248507
Dataset: ArchiML (Architecture and Machine Learning)
Paper: https://doi.org/10.1016/j.jss.2023.111749
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional


# Exclusion criteria descriptions for the ArchiML systematic review
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


class ArchiML(SRProject):
    """
    ArchiML Systematic Literature Review Dataset Processor
    
    Processes the systematic review on "Architecting ML-enabled systems: Challenges,
    best practices, and design decisions" for LLM training dataset creation.
    
    Dataset Characteristics:
        - Paper: https://doi.org/10.1016/j.jss.2023.111749
        - Total Articles: 2,766
        - Included Articles: 34
        - Excluded Articles: 2,732
        - Inclusion Rate: 1.2%
        - Conflict Data: No
        - Criteria Labeled: Yes
        - Abstract Text: No
        - Review Phases: Title/Abstract screening + Full-text screening
        
    Processing Details:
        - Loads data from ArchiML-source.xlsx "Selection Criteria" sheet
        - Maps exclusion criteria to standardized descriptions
        - Handles UTF-8 encoding for international characters
        - Assigns standardized review process metadata
    """

    def __init__(self):
        """
        Initialize ArchiML systematic review dataset processor.
        
        Loads and processes data from the ArchiML source Excel file, mapping columns
        to the standardized schema and applying UTF-8 encoding conversion.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/ArchiML/ArchiML-source.xlsx"
        
        try:
            # Load data from Excel source file
            with open(self.path, 'rb') as f:
                # Main selection criteria sheet contains all 2,766 articles
                sheet_all = pd.read_excel(f, sheet_name="Selection Criteria", header=1)
                print(f"Loaded {len(sheet_all)} articles from ArchiML source")
                
            # Map source columns to standardized schema
            self._map_columns_to_schema(sheet_all)
            
            # Set dataset-specific metadata
            self._set_dataset_metadata()
            
            # Process screening decisions
            self._process_screening_decisions(sheet_all)
            
            print(f"ArchiML dataset initialized with {len(self.df)} articles")
            
        except Exception as e:
            print(f"Error initializing ArchiML dataset: {e}")
            raise
    
    def _map_columns_to_schema(self, sheet_all: pd.DataFrame) -> None:
        """
        Map source Excel columns to standardized dataset schema.
        
        Args:
            sheet_all (pd.DataFrame): Source data from Excel file
        """
        # Map available columns to standardized schema
        self.df['title'] = sheet_all["Title  "].apply(convert_text_encoding)
        self.df["authors"] = sheet_all["Authors"]
        self.df['venue'] = sheet_all["Venue"]
        self.df['source'] = sheet_all['Source']
        self.df["year"] = pd.to_numeric(sheet_all["Year"], errors='coerce').astype("Int64")
        
        # Note: This dataset lacks abstract, keywords, DOI, references, and BibTeX data
        # These fields remain empty and may be populated during metadata extraction
    
    def _set_dataset_metadata(self) -> None:
        """
        Set dataset-specific metadata and configuration.
        """
        self.df['project'] = "ArchiML"
        self.df['mode'] = "new_screen"  # All articles from initial database search
        self.df["reviewer_count"] = 2  # Two reviewers per article
        self.export_path = f"{MAIN_PATH}/Datasets/ArchiML/ArchiML.tsv"
    
    def _process_screening_decisions(self, sheet_all: pd.DataFrame) -> None:
        """
        Process and assign screening decisions based on inclusion/exclusion status.
        
        Args:
            sheet_all (pd.DataFrame): Source data containing decision information
            
        Note:
            ArchiML dataset includes full-text screening decisions.
            Screening and final decisions are the same in this dataset.
        """
        # TODO: Implement decision processing when decision columns are identified
        # Currently all decisions are set to default values
        pass

    def find_decision_on_articles(self, sheet_included: pd.DataFrame, sheet_criteria: pd.DataFrame) -> None:
        """
        Process article screening decisions by comparing titles across sheets.
        
        Args:
            sheet_included (pd.DataFrame): Sheet containing included articles
            sheet_criteria (pd.DataFrame): Sheet containing all articles with criteria
            
        Note:
            In ArchiML, screening and final decisions are equivalent as both
            title/abstract and full-text screening results are combined.
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
    Main execution block for testing ArchiML dataset processing.
    """
    try:
        sr_project = ArchiML()
        print(f"\nArchiML Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with years: {sr_project.df['year'].notna().sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts if available
        if 'screened_decision' in sr_project.df.columns:
            print(f"\nScreening decisions:")
            print(sr_project.df['screened_decision'].value_counts())
            
    except Exception as e:
        print(f"Error running ArchiML processing: {e}")