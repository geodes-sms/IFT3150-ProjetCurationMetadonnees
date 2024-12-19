from Scripts.SRProject import *
import pandas as pd


# Author : Guillaume Genois, 20248507
# This script is for the SmellReprod SR project


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


class SmellReprod(SRProject):
    """
    How far are we from reproducible research on code smell detection? A systematic literature review
    https://www.sciencedirect.com/science/article/pii/S095058492100224X
    Size: 1736
    Included: 169
    Excluded: 1567
    Inclusion rate: 10%
    Has Conflict data: No
    Criteria labeled: Yes
    Has abstract text: No
    Comment: Full-text decision available
    """

    def __init__(self):
        super().__init__()
        # self.path = "../../Datasets/SmellReprod/SmellReprod-source.xlsx"
        self.path = f"{MAIN_PATH}/Datasets/SmellReprod/SmellReprod-source.xlsx"

        # converters = {"Title": lambda x: x.encode('utf-8')}
        # All sheets
        with open(self.path, 'rb') as f:
            sheet_all = pd.read_excel(f, sheet_name="SmellReprod")  # 1733 rows
            print(sheet_all)
            sheet_screened = sheet_all.loc[sheet_all['include decision'] == 'Y']  # 169 rows
            print(sheet_screened)
            sheet_final = sheet_screened.loc[sheet_screened['Final result'] == 'Accepted']  # 46 rows
            print(sheet_final)

        # Add columns
        # self.df["key"]
        self.df['title'] = sheet_all["Title"]
        # self.df['abstract'] = sheet_all["abstract"]
        # self.df["keywords"] = sheet_all["keywords"]
        self.df["authors"] = sheet_all["List of authors"]
        self.df['venue'] = sheet_all["Venue"]
        self.df["doi"] = sheet_all["DOI"]
        # self.df["year"] = sheet_all["Year"]
        # self.df["year"].astype(int)
        # self.df["references"]
        # self.df["bibtex"]
        self.df['mode'] = "new_screen"

        # Find all screened and final decisions
        self.df['screened_decision'] = sheet_all['include decision'].apply(lambda x: 'Included' if x == 'Y' else 'Excluded')
        self.df['final_decision'] = sheet_all['Final result'].apply(lambda x: 'Included' if x == 'Accepted' else 'Excluded')

        criteria_columns = {
            "The entry is a single journal paper, chapter of a book or conference proceedings publication which requires peer review (i.e., it is not an editorial, abstract, technical report etc).": "The entry is not a single journal paper, chapter of a book or conference proceedings publication which requires peer review (i.e., it is not an editorial, abstract, technical report etc).",
            "The paper is written in English": "The paper is not written in English",
            "The paper was published in 1999 or later": "The paper was not published in 1999 or later",
            "Title or abstract of the paper indicates that it is related to software engineering": "Title or abstract of the paper does not indicate that it is related to software engineering",
            "Title or abstract of the paper indicates that at least one code smell/anti-pattern plays an important part of the study": "Title or abstract of the paper does not indicate that at least one code smell/anti-pattern plays an important part of the study",
            "Title or abstract of the paper indicates that it might use machine learning techniques.": "Title or abstract of the paper does not indicate that it might use machine learning techniques.",
            "Abstract of the paper indicates that it focuses on code smells/anti-patterns in programming languages": "Abstract of the paper does not indicate that it focuses on code smells/anti-patterns in programming languages",
            "Abstract of the paper indicates that it focuses on code smells/anti-patterns detection using source code": "Abstract of the paper does not indicate that it focuses on code smells/anti-patterns detection using source code",
            "The paper does not focus on techniques for resolving code smells/anti-patterns": "The paper focuses on techniques for resolving code smells/anti-patterns",
            "The paper does not focus on using code smells/anti-patterns as predictors of other code or project traits.": "The paper focuses on using code smells/anti-patterns as predictors of other code or project traits.",
            "The paper focuses on detection of code smells/anti-patterns": "The paper does not focus on detection of code smells/anti-patterns",
            "If the paper is a chapter of a book or conference proceedings publication, its authors have not published a study under same title in a journal (we want to include the paper once and it may be expected that the journal version includes more details)": "If the paper is a chapter of a book or conference proceedings publication, its authors have published a study under same title in a journal (we want to include the paper once and it may be expected that the journal version includes more details)",
            "Full text of the paper is available": "Full text of the paper is not available",
            # "Not accessible": None,
            # "Out of scope": None,
            # "Out of scope - antipattern library, not detection": None,
            # "Out of scope - clones only": None,
            # "Out of scope - code smell correction, not detection": None,
            # "Out of scope - detection not from source code": None,
            # "Out of scope - literature review": None,
            # "Out of scope - no data": None,
            # "Out of scope - no ML": None,
            # "Out of scope - no smells analyzed": None,
            # "Out of scope - not in English": None,
            # "Out of scope - only a brief": None,
            # "Out of scope - refactoring rather than detection": None,
            # "Out of scope - results already reported in 10.1109/WCRE.2012.56": None,
            # "Out of scope - uses diagrams instead of source code": None,
            # "Out of scope - uses dynamic instrumentation not source code": None,
            # "Out of scope - WSDL modelling, not programming": None,
            # "Out of scope: no data": None
        }

        self.df['exclusion_criteria'] = sheet_all.apply(
                                            lambda row: ', '.join([criteria_columns[col] for col in criteria_columns.keys() if row[col] == 'N']),
                                            axis=1
                                            )
        # self.df['exclusion_criteria'] = sheet_all.apply()
        # self.df['inclusion_criteria'] = self.df['']

        self.df["reviewer_count"] = 2  # TODO: verify

        self.df['project'] = "SmellReprod"
        self.export_path = f"{MAIN_PATH}/Datasets/SmellReprod/SmellReprod.tsv"
        print(self.df)


if __name__ == '__main__':
    sr_project = SmellReprod()
    print('screened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
          sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
    print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
          sum(sr_project.df['final_decision'] == 'Included'), 'Included')
