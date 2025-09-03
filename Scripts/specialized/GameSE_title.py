"""
GameSE Title Systematic Literature Review Dataset Processing Script

Processes the GameSE title-level systematic review dataset on "The consolidation of 
game software engineering" focusing on title/keywords screening phase for metadata 
curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: GameSE_title (Game Software Engineering - Title Phase)
Paper: https://www.sciencedirect.com/science/article/pii/S0950584923001854
"""

from ..core.SRProject import *
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


class GameSE_title(SRProject):
    """
    GameSE Title Phase Systematic Literature Review Dataset Processor
    
    Processes the title/keywords screening phase of the GameSE systematic review on 
    "The consolidation of game software engineering" for LLM training dataset creation.
    
    Dataset Characteristics:
        - Paper: https://www.sciencedirect.com/science/article/pii/S0950584923001854
        - Phase: Title and keywords screening (initial screening phase)
        - Input Articles: All articles after deduplication
        - Focus: Title and keywords analysis
        - Abstract Text: Available but not primary screening criterion
        - Review Phase: Title/Keywords screening → Abstract screening
        
    Processing Details:
        - Loads data from GameSE-source.xlsx title screening sheets
        - Processes articles from initial database search after deduplication
        - Applies exclusion criteria based on title and keywords analysis
        - Handles UTF-8 encoding for international characters
        - Prepares data for subsequent abstract screening phase
        
    Note:
        This is a specialized processor for the title/keywords screening phase only.
        Use GameSE.py for the complete multi-phase processing pipeline.
    """
    """
    The consolidation of game software engineering: A systematic literature review of software engineering for
    industry-scale computer games
    https://www.sciencedirect.com/science/article/pii/S0950584923001854
    Size: 1539
    Included: 614
    Excluded: 925
    Inclusion rate: 40%%
    Has Conflict data: No
    Criteria labeled: No
    Has abstract text: Yes
    Comment: In all datasets, we should compare classification performance w.r.t. the corresponding phase (as we
    already do) and the final set of selected articles (which include reading the full-text, QA and classification)
    """

    def __init__(self):
        """
        Initialize GameSE title phase systematic review dataset processor.
        
        Loads and processes data from the GameSE source Excel file focusing on
        the title/keywords screening phase.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/GameSE/GameSE-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="TotalArticles")  # 3491 rows
            print(sheet_all)
            sheet_without_duplicates = pd.read_excel(f, sheet_name="ReviewByTitle",
                                                     converters=convert_dict)  # 2974 rows
            print(sheet_without_duplicates)
            sheet_title_keywords_included = pd.read_excel(f, sheet_name="RevisionByTitle",
                                                          converters=convert_dict)  # 1539 rows
            print(sheet_title_keywords_included)
            sheet_abstract_included = pd.read_excel(f, sheet_name="ReviewAndRevisionByAbstract",
                                                    converters=convert_dict)  # 614 rows
            print(sheet_abstract_included)
            sheet_text_included = pd.read_excel(f, sheet_name="ReviewAndRevisionByFullText",
                                                converters=convert_dict)  # 252 rows
            print(sheet_text_included)
            sheet_snowballing = pd.read_excel(f, sheet_name="Snowballing", converters=convert_dict)  # 591 rows
            print(sheet_snowballing)
            sheet_final_selection = pd.read_excel(f, sheet_name="FinalSelection", converters=convert_dict)  # 98 rows
            print(sheet_final_selection)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_without_duplicates["Title"]
        self.df['abstract'] = sheet_without_duplicates["Abstract"]
        self.df["keywords"] = sheet_without_duplicates["Keywords"]
        self.df["authors"] = sheet_without_duplicates["Author"]
        self.df['venue'] = sheet_without_duplicates["Journal"]
        self.df["doi"] = sheet_without_duplicates["URL"]
        self.df["year"] = sheet_without_duplicates["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened decisions
        self.find_decision_on_articles(sheet_title_keywords_included, sheet_without_duplicates)
        self.find_decision_on_articles(sheet_abstract_included, sheet_title_keywords_included)

        # Add snowballing articles
        self.add_snowballing_articles(sheet_snowballing)

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_final_selection, sheet_abstract_included, True)
        self.find_decision_on_articles(sheet_final_selection, sheet_text_included, True)

        self.df["reviewer_count"] = 2  # TODO: not indicated in Excel which are conflicted

        # self.df["doi"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")
        # self.df['year'] = self.df['year'].round(0)

        self.df['project'] = "GameSE_title"
        self.export_path = f"{MAIN_PATH}/Datasets/GameSE_title/GameSE_title.tsv"

        print(f"GameSE_title dataset initialized with {len(self.df)} articles")

    def add_snowballing_articles(self, sheet_snowballing):
        snowball_df = empty_df.copy()
        tmp_sheet = sheet_snowballing.loc[sheet_snowballing['Duplications'] == 0]
        snowball_df[['title', 'abstract', 'authors', 'venue', 'year']] = tmp_sheet[
            ["Title", "Abstract", "Author", "Journal", "Year"]]
        snowball_df['mode'] = "snowballing"
        decision = 'screened_decision'
        criteria = 'exclusion_criteria'
        for article_title in snowball_df['title'].values:
            if article_title in sheet_snowballing["Title"].values:
                exclusion_criteria = sheet_snowballing.loc[
                    sheet_snowballing["Title"] == article_title, ["Exclusion Criteria by Title"]].values[0][0]
                if not pd.isna(exclusion_criteria):
                    self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + \
                                                                               excl_crit_desc[exclusion_criteria]
        self.df = pd.concat([self.df, snowball_df], ignore_index=True)
        # TODO: missing keywords, url for these articles
        # TODO: missing exclusion criteria on different page than other articles

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Process title/keywords screening decisions by comparing titles across sheets.
        
        Args:
            sheet_included: DataFrame containing articles that passed title/keywords screening
            sheet_criteria: DataFrame containing all articles with exclusion criteria
            is_final: Whether this is final decision processing (vs. screened decision)
            
        Note:
            GameSE_title focuses specifically on title and keywords-level screening decisions.
            Articles are evaluated based on title and keywords content against exclusion criteria.
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        criteria = 'exclusion_criteria'  # GameSE uses exclusion criteria for both phases
        
        for article_title in self.df['title'].values:
            if pd.isna(article_title) or article_title == "":
                continue
                
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[
                        sheet_criteria["Title"] == article_title, ["Exclusion Criteria by Title"]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + \
                                                                                   EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]

