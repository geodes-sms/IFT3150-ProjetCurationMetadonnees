"""
DTCPS Systematic Literature Review Dataset Processing Script

Processes the DTCPS systematic review dataset on "Digital Twin Cyber-Physical Systems" 
for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: DTCPS (Digital Twin Cyber-Physical Systems)
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd


# Inclusion, exclusion, and quality criteria descriptions as defined in the original paper
EXCLUSION_CRITERIA_DESCRIPTIONS = {
    'IC1': "A least one testing technique is described",
    'IC2': "The system under test must be a cyber–physical system",
    'IC3': "Testing is performed using a digital twin",
    'EC1': "The digital twin described does not use a live data coupling",
    'EC2': "The study describes future use of a digital twin",
    'EC3': "Non-english study",
    'EC4': "Not published in a journal or conference proceedings",
    'QC1': "Are the research questions of the examined study answered?",
    'QC2': "Is the study reproducible?",
}

find_criteria_id = {
    'Testing context but no explained method': 'IC1',
    'Non testing context': 'IC1',
    'Model based verification': 'IC1', #?
    'DT not used for testing CPS': 'IC2',
    'No Physical Element': 'IC2',
    'Non Cyber-Physical System': 'IC2',
    'No Digital Twin': 'IC3',
    'Not focused on Digital Twin': 'IC3',
    # '': 'EC1',
    'Future Works': 'EC2',
    'Non English Study': 'EC3',
    'Non paper': 'EC4',
    'Non Paper': 'EC4',
    'Does not fulfill RQs': 'QC1',
    # '': 'QC2',
    '': None
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
        print(sheet_without_duplicates)
        sheet_screen_title_and_abstract = sheet_without_duplicates.loc[(sheet_without_duplicates['Title + Abstract'] == 'Accepted') | (sheet_without_duplicates['Title + Abstract'] == 'Accepted - Dream Paper')]  # 147
        print(sheet_screen_title_and_abstract)
        sheet_screen_full_text = sheet_screen_title_and_abstract.loc[sheet_screen_title_and_abstract['Full Text'] == 'Accepted']  # 26
        print(sheet_screen_full_text)

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
        self.df['mode'] = 'new_screen'
        self.df["doi"].astype(str)
        self.df.loc[self.df['doi'] != '', 'doi'] = 'https://doi.org/' + self.df['doi'].loc[self.df['doi'] != '']

        # Find all screened decisions
        self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_without_duplicates, 'Title + Abstract')

        # Find all final decisions based on which articles are included in different sheets
        self.find_decision_on_articles(sheet_screen_full_text, sheet_screen_title_and_abstract, 'Full Text', True)

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
                        if 'Rejected' in exclusion_criteria:
                            exclusion_criteria = exclusion_criteria[len('Rejected - '):]
                            exclusion_criteria = find_criteria_id[exclusion_criteria]
                            if exclusion_criteria:
                                criteria = 'inclusion_criteria' if exclusion_criteria[:2] == 'IC' else 'exclusion_criteria'
                                self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]
                        else:
                            pass

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

if __name__ == '__main__':
    dtcps = DTCPS()
    dtcps.df.to_csv(dtcps.export_path, sep='\t')