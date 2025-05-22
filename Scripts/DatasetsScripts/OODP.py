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


class OODP(SRProject):
    """
    A mapping study of language features improving object-oriented design patterns
    https://doi.org/10.1016/j.infsof.2023.107222
    Size: 685
    Included: 34
    Excluded: 651
    Inclusion rate: 5%
    Has Conflict data: No
    Criteria labeled: No
    Has abstract text: Yes
    Comment: The numbers don't match the paper because the author re-ran the query to send me the list of all papers
    """

    def __init__(self):
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/OODP/OODP-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="query results")  # 685 rows
            print(sheet_all)
            sheet_final = pd.read_excel(f, sheet_name="Included")  # 34 rows
            print(sheet_final)
            sheet_final.drop(['Number', 'Type', 'Subjects', 'Subject Type', 'Venue Type'], inplace=True, axis=1)
            sheet_final.rename(columns={'Name': 'Title', 'Year': 'Publication year', 'Publication Venue': 'Source'}, inplace=True)
            sheet_all = pd.concat([sheet_all, sheet_final], ignore_index=True)
            sheet_all.drop_duplicates(subset=['Title'], inplace=True)
            print(sheet_all)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title"]
        self.df['abstract'] = sheet_all["Abstract"]
        # self.df["keywords"] = sheet_without_duplicates["Keywords"]
        self.df["authors"] = sheet_all["Author"]
        self.df['venue'] = sheet_all["Source"]
        self.df["doi"] = sheet_all["DOI"]
        self.df["year"] = sheet_all["Publication year"]
        # self.df["link"] = sheet_without_duplicates["url"]
        self.df["pages"] = sheet_all["Pages"]
        self.df["publisher"] = sheet_all["Publisher"]
        # self.df["source"] = sheet_all["Source"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        # self.df['mode'] = ['snowballing' if not pd.isna(s) else 'new_screen' for s in sheet_without_duplicates['Strategy']]

        # Find all screened decisions
        self.find_decision_on_articles(sheet_final)
        self.df['final_decision'] = self.df['screened_decision']
        # self.find_decision_on_articles(sheet_screen_title_and_abstract, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria')

        # Find all final decisions based on which articles are included in different sheets
        # self.find_decision_on_articles(sheet_screen_final, sheet_without_duplicates, 'Not fulfilled inclusion/exclusion criteria', True)

        self.df["reviewer_count"] = 2

        self.df["doi"].astype(str)
        self.df.loc[~self.df['doi'].isna(), 'doi'] = "https://doi.org/" + self.df.loc[~self.df['doi'].isna(), 'doi']
        self.df["link"].astype(str)
        self.df['year'] = self.df['year'].astype("Int64")

        self.df['project'] = "OODP"
        self.export_path = f"{MAIN_PATH}/Datasets/OODP/OODP.tsv"
        print(self.df)

    def find_decision_on_articles(self, sheet_included, is_final=False):
        decision = 'screened_decision' if not is_final else 'final_decision'
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"


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
    sr_project = OODP()
    print(sr_project.df['screened_decision'].value_counts())
    # sr_project.df.to_csv(sr_project.export_path, sep='\t')
