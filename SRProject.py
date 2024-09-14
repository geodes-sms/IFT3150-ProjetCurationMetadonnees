import re
from datetime import datetime
import pandas as pd

from os_path import EXTRACTED_PATH, MAIN_PATH

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
ScienceDirect = "Elsevier BV"
ACM = "ACM"
SpringerLink = "Springer Science and Business Media LLC"
Scopus = "scopus"
ScopusSignedIn = "ScopusSignedIn"
WoS = "wos"
PubMedCentral = "PubMedCentral"
arXiv = "arXiv"

sources_name = ['acm', 'ieee', 'wos', 'scopus', 'springer', 'sciencedirect']
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
    with open(f"{MAIN_PATH}/Scripts/articles_source_links.tsv", 'a') as f:
        f.write(title + "\t" + link + "\n")


# Abstract class for all systematic reviews datasets
class SRProject:
    # Blank dataframe
    df = empty_df.copy()
    # All columns
    project = None
    key = None
    title = None
    abstract = None
    keywords = None
    authors = None
    venue = None
    doi = None
    references = None
    bibtex = None
    screened_decision = None
    final_decision = None
    mode = None
    inclusion_criteria = None
    exclusion_criteria = None
    reviewer_count = None

    # Paths
    path = None
    export_path = None

    def __init__(self):
        pass


def update_metadata(old, new):
    tmp = {}
    for k, v in new.items():
        if v is not None or v != "":
            tmp[k] = v
    old.update(tmp)


def format_link(link):
    formated_link = link
    for k in special_char_conversion.keys():
        formated_link = formated_link.replace(k, "%" + special_char_conversion[k])
    return formated_link


def save_extracted_html(link, html):
    formated_link = link
    for k in special_char_conversion.keys():
        formated_link = formated_link.replace(k, "%" + special_char_conversion[k])
    with open(f"{EXTRACTED_PATH}/HTML extracted/{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html", 'wb') as f:
        f.write(html.encode("utf-8"))
    print(f"{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html")
    print(formated_link)


def clean_title(title):
    # TODO: for title in title separated by : - —
    # tmp_title = title[title.index(":"):] if ":" in title else title
    # print(title)
    # tmp_title = title[title.index("-"):] if "-" in title else title
    tmp_title = title
    print(tmp_title)
    # tmp_title = str.lower(tmp_title)
    tmp_title = re.sub(r":|/|-|—|,|\.|<.*>|³N|\?|\*|&|;|â€“|‘|'|\"", " ", str.lower(tmp_title))
    print(tmp_title)
    print([e for e in tmp_title.split(" ") if e != ""])
    return " ".join([e for e in tmp_title.split(" ") if e != ""])


def check_if_right_link(new_metadata, title, author=None, venue=None, year=None):
    if new_metadata is None or new_metadata['Title'] == "" or title == "":
        return False
    # TODO: enlever les deux points, les virgules, les tirets, / ou prendre distance? ou auteurs et année?
    tmp_title = clean_title(title)
    tmp_meta_title = clean_title(new_metadata['Title'])
    print(tmp_title)
    print(tmp_meta_title)
    if tmp_title in tmp_meta_title or tmp_meta_title in tmp_title:
        return True
    return False


