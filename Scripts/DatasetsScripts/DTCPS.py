from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for the DTCPS SR project


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


class DTCPS(SRProject):
    """
    Digital-twin-based testing for cyber–physical systems: A systematic literature review
    https://www.sciencedirect.com/science/article/pii/S0950584922002543
    Size: 454
    Included: 147
    Excluded: 307
    Inclusion rate: 32%%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Full-text decision available
    """

    def __init__(self):
        super().__init__()
        # self.path = "../../Datasets/DTCPS/DTCPS-source.xlsx"
        self.path = f"{MAIN_PATH}/Datasets/DTCPS/DTCPS-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="export")  # 458 rows
            print(sheet_all)
        sheet_without_duplicates = sheet_all.loc[sheet_all['Duplicate'] == 'Accepted']  # 454
        sheet_screen_title_and_abstract = sheet_without_duplicates.loc[sheet_without_duplicates['Title + Abstract'] == 'Accepted']  # 147
        sheet_screen_full_text = sheet_screen_title_and_abstract.loc[sheet_screen_title_and_abstract['Full Text'] == 'Accepted']  # 26

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_without_duplicates["Title"]
        # self.df['abstract'] = sheet_without_duplicates["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        self.df["authors"] = sheet_without_duplicates["author"]
        self.df['venue'] = sheet_without_duplicates["journal"]
        self.df["doi"] = sheet_without_duplicates["doi"]
        self.df["year"] = sheet_without_duplicates["year"]
        self.df["link"] = sheet_without_duplicates["url"]
        self.df["pages"] = sheet_without_duplicates["pages"]
        self.df["publisher"] = sheet_without_duplicates["publisher"]
        self.df["source"] = self.df['publisher']
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        # self.df['mode'] = ['snowballing' if s != 'None' else 'new_screen' for s in sheet_without_duplicates['Snowballing']]
        self.df["doi"].astype(str)
        self.df['doi'].loc[self.df['doi'] != ''] = 'https://doi.org/' + self.df['doi'].loc[self.df['doi'] != '']

        # Find all screened decisions
        # self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_screen_title_and_abstract, 'Title + Abstract')

        # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_screen_full_text, sheet_screen_full_text, 'Full Text', True)

        self.df["reviewer_count"] = 2  # TODO: not indicated in Excel which are conflicted

        self.df["link"].astype(str)

        self.df['project'] = "DTCPS"
        self.export_path = f"{MAIN_PATH}/Datasets/DTCPS/DTCPS.tsv"
        print(self.df)
        print(self.df['doi'])

    def find_decision_on_articles(self, sheet_included, sheet_criteria, criteria_column, is_final=False):
        decision = 'screened_decision' if not is_final else 'final_decision'
        # criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        criteria = 'exclusion_criteria' if not is_final else 'exclusion_criteria'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, [criteria_column]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        exclusion_criteria = exclusion_criteria[11:]
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria  # + ": " + excl_crit_desc[exclusion_criteria]


    def find_source(self, publishers):
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
