from Scripts.SRProject import *
import pandas as pd

# Author : Guillaume Genois, 20248507
# This script is for the CodeClone SR project

excl_crit_desc = {
    'EC1': 'The articles repeated in citation databases were removed. We kept only one version of each duplicated article.',
    'EC2': 'Articles whose main text was written in any language other than English or only their abstract and keywords were in English were eliminated.',
    'EC3': 'Articles whose total text was less than three pages were removed. After reviewing them, we removed these articles and ensured they did not contain significant contributions. If there are good clues in these articles to find other suitable topics and articles, we consider these clues while applying the inclusion criteria and snowballing phases.',
    'EC4': 'Articles that did not directly discuss a source code similarity measurement approach in their abstract were removed. For example, some papers have discussed binary code similarity.',
    'EC5': 'The papers that had not proposed an automated approach for source code similarity measurement were removed. We excluded these articles since the similarity measurement technique was necessary when classifying methods.',
    'EC6': 'Theses, books, journal covers and metadata, secondary, tertiary, empirical, and case studies were removed.',
    'YES': '',
}

"""
Special characters conversion for data source of CodeClone
"Â", ""
"â€™", "'"
"â€œ", '"'
'â€“', '-'
'â€', '"'
"""

class CodeClone(SRProject):
    """
    A systematic literature review on source code similarity measurement and clone detection: Techniques, applications, and challenges
    https://doi.org/10.1016/j.jss.2023.111796
    Size: 10454
    Included: 573
    Excluded: 9881
    Inclusion rate: 5%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Full-text decision available
    """
    # TODO: add snowballing articles
    # TODO: some articles are missing titles, venue,
    # TODO: all articles are missing abstract, keywords, authors, doi, references, bibtex
    # TODO: add description of exclusion criteria next to code

    def __init__(self):
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/CodeClone/CodeClone-source.xlsx"
        sheet_initial_articles = pd.read_excel(self.path, sheet_name="initial-articles")  # 10454 rows
        sheet_initial_selection = pd.read_excel(self.path, sheet_name="initial-selection")  # 573 rows
        sheet_final_selected = pd.read_excel(self.path, sheet_name="final-selected")  # 301 rows
        print(sheet_initial_articles)
        print(sheet_initial_selection)
        print(sheet_final_selected)

        # self.project = "CodeClone"
        # self.title = sheet_initial_articles["Article title"]
        # self.venue = sheet_initial_articles["Venue name"]
        # self.exclusion_criteria = sheet_initial_articles["Applied exclusion criteria"]
        # self.mode = "new_screen"

        self.df['title'] = sheet_initial_articles["Article title"]
        self.df['venue'] = sheet_initial_articles["Venue name"]
        self.df['source'] = sheet_initial_articles["Publisher"]
        self.df['exclusion_criteria'] = sheet_initial_articles["Applied exclusion criteria"]
        self.df['mode'] = "new_screen"
        self.df['reviewer_count'] = 1
        self.df["reviewer_count"].astype(int)

        self.df['project'] = "CodeClone"
        self.export_path = f"{MAIN_PATH}/Datasets/CodeClone/CodeClone.tsv"
        self.find_decision_on_articles(sheet_initial_selection, sheet_initial_articles)
        self.find_decision_on_articles(sheet_final_selected, sheet_initial_selection, True)

        print(self.df)

    # def find_decision_on_articles(self, sheet_initial_articles, sheet_initial_selection, sheet_final_selected):
    #     # Note: No conflict in this SR, so no ConflictIncluded and ConflictExcluded
    #     # df1[ df1.index.isin(sample1.index) & df1.index.isin(sample2.index) ]
    #     for article_title in sheet_initial_articles["Article title"]:
    #         if article_title == "": continue   # TODO: change how to check for matching articles, use whole row instead
    #         if article_title in sheet_final_selected["Article title"].values:
    #             self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Included"
    #         else:
    #             self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Excluded"
    #         if article_title in sheet_initial_selection["Article title"].values:
    #             self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Included"
    #             self.df.loc[self.df['title'] == article_title, 'inclusion_criteria'] = sheet_initial_selection.loc[self.df['title'] == article_title, "Inclusion criteria"]
    #         else:
    #             self.df.loc[self.df["title"] == article_title, 'screened_decision'] = "Excluded"

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        decision = 'screened_decision' if not is_final else 'final_decision'
        criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        header_criteria = 'Applied exclusion criteria' if not is_final else 'Inclusion criteria'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Article title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Article title"].values:
                    exclusion_criteria = str.upper(sheet_criteria.loc[sheet_criteria["Article title"] == article_title, [header_criteria]].values[0][0])
                    if not pd.isna(exclusion_criteria) and exclusion_criteria not in ['SELECTED', 'NO']:
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + excl_crit_desc[exclusion_criteria]


if __name__ == '__main__':
    sr_project = CodeClone()
    print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
          sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
    print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
          sum(sr_project.df['final_decision'] == 'Included'), 'Included')
