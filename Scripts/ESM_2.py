from SRProject import SRProject
import pandas as pd

# Author : Guillaume Genois, 20248507
# This script is for the CodeClone SR project

code_publisher = {
    'ACM': 'ACM',
    'IEE': 'IEEE',
    'SCO': 'Scopus',
    'MED': 'Medline',
    'SCI': 'ScienceDirect',
    'SPR': 'Springer Link'
}


class ESM_2(SRProject):
    """
    Adaptive user interfaces in systems targeting chronic disease: a systematic literature review
    https://doi.org/10.48550/arXiv.2211.09340
    Size: 114
    Included: 61
    Excluded: 53
    Inclusion rate: 54%%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: Yes
    Comment: "Numbers don't match paper, initial papers not available. Criteria labeled do not match EC in paper"
    """

    def __init__(self):
        super().__init__()
        self.path = "../Datasets/ESM_2/ESM_2-source.xlsx"
        sheet_abstract = pd.read_excel(self.path, sheet_name="Abstract")  # 114
        sheet_final = pd.read_excel(self.path, sheet_name="Intro+method+conclusion")  # 61

        # self.project = "ESM_2"
        # self.key = sheet_abstract["Number"]
        # self.authors = sheet_abstract["Author"]
        # self.title = sheet_abstract["Titile"]
        # self.abstract = sheet_abstract["Abstract"]
        # self.screened_decision = sheet_abstract["Decision"]
        # self.mode = "new_screen"

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_abstract["Titile"]
        self.df['abstract'] = sheet_abstract["Abstract"]
        # self.df["keywords"] = sheet_abstract["Keywords"]
        self.df["authors"] = sheet_abstract["Author"]
        # self.df['venue'] = sheet_abstract["Journal"]
        # self.df["doi"] = sheet_abstract["URL"]
        # self.df["year"] = sheet_abstract["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "snowballing"  # we don't have the original screening
        # self.df['publisher'] = [code_publisher[e[:3]] for e in sheet_abstract['Number']]
        # self.df['source'] = self.df['publisher']

        # Find all screened decisions
        self.find_decision_on_articles(sheet_final, sheet_abstract)

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_final, sheet_final, True)
        self.df.loc[self.df['screened_decision'] == 'Excluded', 'final_decision'] = 'Excluded'

        self.df["reviewer_count"] = 2  # TODO: to be verified

        self.df['title'] = self.df['title'].str[:-1]

        self.df['project'] = "ESM_2"
        self.export_path = "../Datasets/ESM_2/ESM_2.tsv"
        print(self.df[['screened_decision', 'final_decision', 'exclusion_criteria']])

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        decision = 'screened_decision' if not is_final else 'final_decision'
        for idx, row in sheet_criteria.iterrows():
            article_title = row["Titile"]

            if row['Decision'] == 'In':
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
                print(self.df.loc[self.df['title'] == article_title])
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                criteria = 'exclusion_criteria'
                exclusion_criteria = sheet_criteria.loc[sheet_criteria["Titile"] == article_title, ["Note"]].values[0][0]
                if not pd.isna(exclusion_criteria):
                    self.df.loc[self.df['title'] == article_title, criteria] = self.clean_exclusion_criteria(exclusion_criteria)

    def clean_exclusion_criteria(self, exclusion_criteria):
        return exclusion_criteria
