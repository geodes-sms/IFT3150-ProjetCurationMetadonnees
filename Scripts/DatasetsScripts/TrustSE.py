from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for the TrustSE SR project


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


class TrustSE(SRProject):
    """
    A systematic literature review on trust in the software ecosystem
    https://doi.org/10.1007/s10664-022-10238-y
    Size: 556
    Included: 112
    Excluded: 444
    Inclusion rate: 20%%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Exclusion criteria are not about the content but the format
    """

    def __init__(self):
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/TrustSE/TrustSE-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="Selected manuscripts", header=1)  # 3491 rows
            print(sheet_all)


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
        # self.find_decision_on_articles(sheet_title_keywords_included, sheet_without_duplicates)
        # self.find_decision_on_articles(sheet_abstract_included, sheet_title_keywords_included)
        #
        # # Add snowballing articles
        # self.add_snowballing_articles(sheet_snowballing)
        #
        # # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_final_selection, sheet_abstract_included, True)
        # self.find_decision_on_articles(sheet_final_selection, sheet_text_included, True)

        self.df["reviewer_count"] = 2  # TODO: not indicated in Excel which are conflicted

        self.df["doi"].astype(str)

        self.df['project'] = "TrustSE"
        self.export_path = f"{MAIN_PATH}/Datasets/TrustSE/TrustSE.tsv"
        print(self.df)

    def add_snowballing_articles(self, sheet_snowballing):
        snowball_df = empty_df.copy()
        snowball_df[['title', 'abstract', 'authors', 'venue', 'year']] = sheet_snowballing[["Title", "Abstract", "Author", "Journal", "Year"]]
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
        decision = 'screened_decision' if not is_final else 'final_decision'
        # criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        criteria = 'exclusion_criteria' if not is_final else 'exclusion_criteria'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, ["Exclusion Criteria by Title"]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + excl_crit_desc[exclusion_criteria]

