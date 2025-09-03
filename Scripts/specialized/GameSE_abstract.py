from ..core.SRProject import *
import pandas as pd

# Author : Guillaume Genois, 20248507
# This script is for the GameSE SR project


excl_crit_desc = {
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


# TODO: in methodology, articles excluded if not meeting inclusion criterias
# TODO: verify meaning of proceedings and not sure


def convert(x):
    # return x
    # x = x.replace("0xE20x800x99", "'")
    return x.encode('utf-8').decode('utf-8')


convert_dict = {"Title": convert}  # TODO: add other columns


class GameSE_abstract(SRProject):
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
            sheet_snowballing = pd.read_excel(f, sheet_name="Snowballing", converters=convert_dict)  # 591 rows - 70 duplicates
            print(sheet_snowballing)
            sheet_final_selection = pd.read_excel(f, sheet_name="FinalSelection", converters=convert_dict)  # 98 rows
            print(sheet_final_selection)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_abstract_included["Title"]
        self.df['abstract'] = sheet_abstract_included["Abstract"]
        self.df["keywords"] = sheet_abstract_included["Keywords"]
        self.df["authors"] = sheet_abstract_included["Author"]
        self.df['venue'] = sheet_abstract_included["Journal"]
        self.df["doi"] = sheet_abstract_included["URL"]
        self.df["year"] = sheet_abstract_included["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened decisions
        self.find_decision_on_articles(sheet_text_included, sheet_abstract_included)

        # Add snowballing articles
        self.add_snowballing_articles(sheet_snowballing)

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_final_selection, sheet_text_included, True)

        self.df["reviewer_count"] = 2  # TODO: not indicated in Excel which are conflicted

        # self.df["doi"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")
        # self.df['year'] = self.df['year'].round(0)

        self.df['project'] = "GameSE_abstract"
        self.export_path = f"{MAIN_PATH}/Datasets/GameSE_abstract/GameSE_abstract.tsv"

        print(self.df)

    def add_snowballing_articles(self, sheet_snowballing):
        """
        Add snowballing articles to the abstract phase dataset with proper metadata mapping.
        
        Args:
            sheet_snowballing: DataFrame containing snowballing articles
            
        Note:
            Snowballing articles are marked with mode='snowballing' and may have
            different exclusion criteria than database search articles.
        """
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
                                                                               EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]
        self.df = pd.concat([self.df, snowball_df], ignore_index=True)
        # TODO: missing keywords, url for these articles
        # TODO: missing exclusion criteria on different page than other articles

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Process abstract screening decisions by comparing titles across sheets.
        
        Args:
            sheet_included: DataFrame containing articles that passed abstract screening
            sheet_criteria: DataFrame containing all articles with exclusion criteria
            is_final: Whether this is final decision processing (vs. screened decision)
            
        Note:
            GameSE_abstract focuses specifically on abstract-level screening decisions.
            Articles are evaluated based on abstract content against exclusion criteria.
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        criteria = 'exclusion_criteria'  # GameSE uses exclusion criteria for both phases
        for article_title in self.df['title'].values:
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


if __name__ == '__main__':
    """
    Main execution block for testing GameSE_abstract dataset processing.
    """
    try:
        sr_project = GameSE_abstract()
        print(f"\nGameSE_abstract Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with abstracts: {sr_project.df['abstract'].notna().sum()}")
        print(f"Articles with keywords: {sr_project.df['keywords'].notna().sum()}")
        print(f"Database search articles: {(sr_project.df['mode'] == 'new_screen').sum()}")
        print(f"Snowballing articles: {(sr_project.df['mode'] == 'snowballing').sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts
        if 'screened_decision' in sr_project.df.columns:
            screened_counts = sr_project.df['screened_decision'].value_counts()
            print(f"\nScreening decisions: {dict(screened_counts)}")
            
        if 'final_decision' in sr_project.df.columns:
            final_counts = sr_project.df['final_decision'].value_counts()
            print(f"Final decisions: {dict(final_counts)}")
            
    except Exception as e:
        print(f"Error running GameSE_abstract processing: {e}")