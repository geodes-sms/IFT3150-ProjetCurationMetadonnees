from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for the ArchiML SR project


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


class ArchiML(SRProject):
    """
    Architecting ML-enabled systems: Challenges, best practices, and design decisions
    https://doi.org/10.1016/j.jss.2023.111749
    Size: 2,766
    Included: 34
    Excluded: 2,732
    Inclusion rate: 1%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Inclusion includes full-text screening as well
    """

    def __init__(self):
        super().__init__()
        # self.path = "../../Datasets/ArchiML/ArchiML-source.xlsx"
        self.path = f"{MAIN_PATH}/Datasets/ArchiML/ArchiML-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="Selection Criteria", header=1)  # 2766 rows
            print(sheet_all)
            print(sheet_all.columns)
            # sheet_final = pd.read_excel(f, sheet_name="final_data_from_database_search")  # 148 rows
            # print(sheet_final)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title  "]
        # self.df['abstract'] = sheet_all["abstract"]
        # self.df["keywords"] = sheet_all["keywords"]
        self.df["authors"] = sheet_all["Authors"]
        self.df['venue'] = sheet_all["Venue"]
        # self.df["doi"] = sheet_all["abstract"]
        self.df['source'] = sheet_all['Source']
        self.df["year"] = sheet_all["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened and final decisions
        # self.find_decision_on_articles(sheet_final, sheet_all)

        self.df["reviewer_count"] = 2  # TODO: verify

        self.df['project'] = "ArchiML"
        self.export_path = f"{MAIN_PATH}/Datasets/ArchiML/ArchiML.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, sheet_criteria):
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Included"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Excluded"
                self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Excluded"


if __name__ == '__main__':
    sr_project = ArchiML()
    print(ArchiML.df['doi'])