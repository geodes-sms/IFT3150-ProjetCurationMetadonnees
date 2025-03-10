import re
from datetime import datetime
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from unidecode import unidecode
from nltk import edit_distance
from Scripts.os_path import EXTRACTED_PATH, MAIN_PATH

"""
  Key               String
  Title             String
  Abstract          String
  Keywords          String
  Authors           String
  Venue             String
  DOI               String
  References        String
  Bibtex            String
  ScreenedDecision  String {Included, Excluded, ConflictIncluded, ConflictExcluded}
  FinalDecision     String {Included, Excluded, ConflictIncluded, ConflictExcluded}
  Mode              String {new_screen, snowballing}
  InclusionCriteria String
  ExclusionCriteria String
  ReviewerCount     Int
"""

"""
self.df["key"]
self.df["project"]
self.df["title"]
self.df["abstract"]
self.df["keywords"]
self.df["authors"]
self.df["venue"]
self.df["doi"]
self.df["references"]
self.df["bibtex"]
self.df["screened_decision"]
self.df["final_decision"]
self.df["mode"]
self.df["inclusion_criteria"]
self.df["exclusion_criteria"]
self.df["reviewer_count"]
"""

metadata_base = {"Title": "",
                 "Venue": "",
                 "Authors": "",
                 "Abstract": "",
                 "Keywords": "",
                 "References": "",
                 "Pages": "",
                 "Year": "",
                 "Bibtex": "",
                 "DOI": "",
                 "Source": "",
                 "Link": "",
                 "Publisher": ""}

# TODO: list de noms pour chaque venue
IEEE = "IEEE"
ScienceDirect = "Science Direct"
ACM = "ACM"
SpringerLink = "Springer Link"
Scopus = "Scopus"
ScopusSignedIn = "Scopus Signed In"
WoS = "Web of Science"
PubMedCentral = "Pub Med Central"
arXiv = "arXiv"

sources_name = ['scopus', 'acm', 'ieee', 'wos', 'springer', 'sciencedirect', 'arxiv']
all_sources_name = ['ieee', 'springer', 'acm', 'sciencedirect', 'scopus', 'wos',
                    IEEE, SpringerLink, ACM, ScienceDirect, Scopus, WoS,
                   "Association for Computing Machinery (ACM)", "ACM Press"]

special_char_conversion = {
    "\\": "5C",
    "/": "2F",
    ":": "3A",
    "*": "2A",
    "?": "3F",
    '"': "22",
    "<": "3C",
    ">": "3E",
    "|": "7C"
}

code_source = {
    '00': IEEE,
    '01': ACM,
    '02': ScienceDirect,
    '03': SpringerLink,
    '04': Scopus,
    '05': WoS,
    '06': "DOI",
    '07': ScopusSignedIn,
    '08': PubMedCentral,
    '09': arXiv
}

empty_df = pd.DataFrame(columns=["key", "project", "title", "abstract", "keywords", "authors", "venue", "doi",
                                 "references", "pages", "bibtex", "screened_decision", "final_decision", "mode",
                                 "inclusion_criteria", "exclusion_criteria", "reviewer_count",
                                 "source", "year", "meta_title", "link", "publisher", "metadata_missing"], dtype=str)


def save_link(title, link):
    with open(f"{MAIN_PATH}/Scripts/articles_source_links.tsv", 'a', encoding='windows-1252') as f:
        f.write(title + "\t" + link + "\n")


# Abstract class for all systematic reviews datasets
class SRProject:


    def __init__(self):
        # Blank dataframe
        self.df = empty_df.copy()
        # All columns
        self.project = None

        self.key = None
        self.title = None
        self.abstract = None
        self.keywords = None
        self.authors = None
        self.venue = None
        self.doi = None
        self.references = None
        self.bibtex = None
        self.screened_decision = None
        self.final_decision = None
        self.mode = None
        self.inclusion_criteria = None
        self.exclusion_criteria = None
        self.reviewer_count = None

        # Paths
        self.path = None
        self.export_path = None


def update_metadata(old, new):
    tmp = {}
    for k, v in new.items():
        if v is not None and v != "":
            tmp[k] = v
    old.update(tmp)


def format_link(link):
    formated_link = link
    for k in special_char_conversion.keys():
        formated_link = formated_link.replace(k, "%" + special_char_conversion[k])
    formated_link = formated_link[:200]
    return formated_link


def save_extracted_html(link, html):
    formated_link = format_link(link)
    with open(f"{EXTRACTED_PATH}/HTML extracted/{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html", 'wb') as f:
        f.write(html.encode("utf-8"))
    print(f"{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html")
    print(formated_link)


def standardize_title(title):
    # TODO: for title in title separated by : - —
    # tmp_title = title[title.index(":"):] if ":" in title else title
    # print(title)
    # tmp_title = title[title.index("-"):] if "-" in title else title
    tmp_title = ILLEGAL_CHARACTERS_RE.sub(r'', title)
    print(tmp_title)
    # tmp_title = str.lower(tmp_title)
    tmp_title = re.sub(r"\\'|#x0027|#x201c|#x201d", '', str.lower(tmp_title))
    tmp_title = re.sub(r"\\emdash|\\endash|&amp;|â€”|â€™|:|/|-|—|,|\.|<[^>]+>|³N|\?|\*|&|;|â€“|‘|'|\"|’|–|”|“|±|\+|\\|\(|\)", " ", tmp_title)
    print(tmp_title)
    tmp_title = ''.join([char for char in tmp_title if char.isalpha() or char.isspace()])
    tmp_title = unidecode(tmp_title)
    print([e for e in tmp_title.split(" ") if e != ""])
    return " ".join([e for e in tmp_title.split(" ") if len(e) > 1])


def check_if_right_link(new_metadata, title, author=None, venue=None, year=None):
    if new_metadata is None or new_metadata['Title'] == "" or title == "" or new_metadata['Title'] is None:
        return False
    # TODO: enlever les deux points, les virgules, les tirets, / ou prendre distance? ou auteurs et année?
    tmp_title = standardize_title(title)
    tmp_meta_title = standardize_title(new_metadata['Title'])
    print(tmp_title)
    print(tmp_meta_title)
    if tmp_title in tmp_meta_title or tmp_meta_title in tmp_title or edit_distance(tmp_title, tmp_meta_title) < 3:
        if abs(len(tmp_title.split()) - len(tmp_meta_title.split())) < 4 or abs(len(tmp_title) - len(tmp_meta_title)) < 10:
            return True
    return False


