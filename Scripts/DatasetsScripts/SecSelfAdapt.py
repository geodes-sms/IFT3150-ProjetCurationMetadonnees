from Scripts.SRProject import *
import pandas as pd
import openpyxl


# Author : Guillaume Genois, 20248507
# This script is for the ModelingAssist SR project


excl_crit_desc = {
    'I1': "Is the paper exclusively dedicated to a particular proposal, rather than being a compilation of proposals, aimed at assisting users during modelling tasks in MDSE tools? Compilation of proposals like literature reviews, systematic mappings, or systematic literature reviews does not fulfil I1.",
    'I2': "Is the proposal designed to assist users during modelling tasks in MDSE tools? We focus on proposals that assist users during modelling tasks in MDSE tools, including—but not limited to—modelling, model tracing, model debugging, model re-pair, and model validation, among others.",
    'E1': "The proposal’s main contribution is not to assist users during modelling in MDSE tools. If assisting users during modelling tasks is not the main contribution, we exclude the proposal using E1.",
    'E2': "The proposal is not related to software engineering.",
    'E3': "The proposal is not written in English",
    'E4': "The proposal is not a peer-reviewed publication",
    'E5': "The proposal's full text is not available."
}


class SecSelfAdapt(SRProject):
    """
    A systematic review on security and safety of self-adaptive systems
    https://doi.org/10.1016/j.jss.2023.111716
    Size: 1433
    Included: 65
    Excluded: 1,368
    Inclusion rate: 5%
    Has Conflict data: No
    Criteria labeled: No
    Has abstract text: No
    Comment: Full-text decision available + conflict info for full-text
    """

    def __init__(self):
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/SecSelfAdapt/SecSelfAdapt-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="Merge Results")  # 685 rows
            print(sheet_all)


        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Publication Title"]
        # self.df['abstract'] = sheet_all["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        self.df["authors"] = sheet_all["Authors"]
        # self.df['venue'] = sheet_all["Source"]
        self.df["doi"] = sheet_all["doi"]
        self.df["year"] = sheet_all["Publication Year"]
        # self.df["link"] = sheet_without_duplicates["url"]
        # self.df["pages"] = sheet_all["Pages"]
        # self.df["publisher"] = sheet_all["Publisher"]
        self.df["source"] = sheet_all["Search Database"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        # self.df['mode'] = ['snowballing' if not pd.isna(s) else 'new_screen' for s in sheet_without_duplicates['Strategy']]

        # Find all screened decisions
        # self.find_decision_on_articles(sheet_screen_title, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')
        # self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')

        # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_screen_final, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria', True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)
        # self.df.loc[~self.df['doi'].isna(), 'doi'] = "https://doi.org/" + self.df.loc[~self.df['doi'].isna(), 'doi']
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "SecSelfAdapt"
        self.export_path = f"{MAIN_PATH}/Datasets/SecSelfAdapt/SecSelfAdapt.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, sheet_criteria, criteria_column, is_final=False):
        decision = 'screened_decision' if not is_final else 'final_decision'
        # criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                conflicted_decision = "Included"
                if is_final:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if row['Include after second reviewer opinion? '].values[0] != row['Include after full-text review?'].values[0]:
                        conflicted_decision = "ConflictIncluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision
            else:
                conflicted_decision = "Excluded"
                if is_final and article_title in sheet_criteria['Title'].values:
                    row = sheet_criteria.loc[sheet_criteria['Title'] == article_title]
                    if row['Include after second reviewer opinion? '].values[0] != row['Include after full-text review?'].values[0]:
                        conflicted_decision = "ConflictExcluded"
                self.df.loc[self.df['title'] == article_title, decision] = conflicted_decision
                if article_title in sheet_criteria["Title"].values:
                    exclusion_criteria = sheet_criteria.loc[sheet_criteria["Title"] == article_title, [criteria_column]].values[0][0]
                    if not pd.isna(exclusion_criteria):
                        criteria = 'exclusion_criteria' if exclusion_criteria[0] == 'E' else 'inclusion_criteria'
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + excl_crit_desc[exclusion_criteria]


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
    sr_project = SecSelfAdapt()
    print(sr_project.df['doi'].isna().sum())
    sr_project.df.to_csv(sr_project.export_path, sep='\t')