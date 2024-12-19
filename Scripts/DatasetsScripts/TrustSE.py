from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for the TrustSE SR project


excl_crit_desc = {
'book': 'Studies that were books or gray literature',
'Book': 'Studies that were books or gray literature',
'Book cannot access': 'Studies that were books or gray literature',
'Cannot access': 'Studies that were not accessible in full-text',
'cannot access': 'Studies that were not accessible in full-text',
'incomplete paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Not a paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Not peer-reviewed': 'Studies that were not peer-reviewed',
'Short paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Tech Report': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'thesis': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
'Working paper': 'Studies that were incomplete, short papers, or only provided literature in the form of abstracts, prefaces, or presentation slides',
}


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
            sheet_all = pd.read_excel(f, sheet_name="Selected manuscripts", header=1)  # 556 rows
            print(sheet_all)
            sheet_final = sheet_all.loc[sheet_all['SLR paper?'] == 'Yes']  # 112 rows
            print(sheet_final)


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
        self.find_decision_on_articles(sheet_final, sheet_all)
        self.df['final_decision'] = self.df['screened_decision']
        # self.find_decision_on_articles(sheet_abstract_included, sheet_title_keywords_included)
        #
        # # Add snowballing articles
        # self.add_snowballing_articles(sheet_snowballing)
        #
        # # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_final_selection, sheet_abstract_included, True)
        # self.find_decision_on_articles(sheet_final_selection, sheet_text_included, True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)

        self.df['project'] = "TrustSE"
        self.export_path = f"{MAIN_PATH}/Datasets/TrustSE/TrustSE.tsv"
        print(self.df)

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
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, ["SLR paper?"]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        self.df.loc[self.df['title'] == article_title, criteria] = excl_crit_desc[exclusion_criteria]


if __name__ == '__main__':
    sr_project = TrustSE()
