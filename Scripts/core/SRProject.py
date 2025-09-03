import re
from datetime import datetime
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from unidecode import unidecode
from nltk import edit_distance
from .os_path import EXTRACTED_PATH, MAIN_PATH

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
    """
    Saves a title-link pair to the articles source links tracking file.
    
    This function maintains a cache of successfully found article links to avoid
    redundant searches in future runs. The file format is TSV (tab-separated values)
    with two columns: Title and Link.
    
    Args:
        title (str): The title of the article
        link (str): The URL/link to the article source
        
    Returns:
        None: Appends the entry to the articles_source_links.tsv file
        
    Note:
        Uses windows-1252 encoding to handle special characters in titles.
        The file is opened in append mode to preserve existing entries.
    """
    with open(f"{MAIN_PATH}/Scripts/data/articles_source_links.tsv", 'a', encoding='windows-1252') as f:
        f.write(title + "\t" + link + "\n")


# Abstract class for all systematic reviews datasets
class SRProject:
    """
    Abstract base class for systematic literature review datasets.
    
    This class defines the common structure and interface for all systematic
    review projects in the metadata curation pipeline. It provides a standardized
    schema for academic article metadata and serves as the foundation for
    dataset-specific implementations.
    
    The class maintains a pandas DataFrame with standardized columns for all
    metadata fields, ensuring consistency across different systematic review
    sources and facilitating uniform processing.
    
    Standard schema includes:
        - Bibliographic data: title, authors, venue, doi, year, pages
        - Content data: abstract, keywords, references, bibtex
        - Review process data: screened_decision, final_decision, mode
        - Criteria data: inclusion_criteria, exclusion_criteria, reviewer_count
        - System data: key, project, source, link, publisher, metadata_missing
    
    Attributes:
        df (pd.DataFrame): Main data container with standardized schema
        project (str): Name of the systematic review project
        path (str): Path to the source data file
        export_path (str): Path where processed data will be exported
        
    Note:
        This is an abstract class meant to be subclassed by specific
        systematic review implementations (e.g., ArchiML, CodeClone, etc.)
    """

    def __init__(self):
        """
        Initialize a new systematic review project with empty standardized structure.
        
        Creates an empty DataFrame with the standard schema and initializes
        all metadata fields to None. Subclasses should populate these fields
        with data from their specific sources.
        """
        # Blank dataframe with standardized schema
        self.df = empty_df.copy()
        
        # Project identification
        self.project = None

        # Bibliographic metadata fields
        self.key = None
        self.title = None
        self.abstract = None
        self.keywords = None
        self.authors = None
        self.venue = None
        self.doi = None
        self.references = None
        self.bibtex = None
        
        # Review process metadata
        self.screened_decision = None
        self.final_decision = None
        self.mode = None
        self.inclusion_criteria = None
        self.exclusion_criteria = None
        self.reviewer_count = None

        # File system paths
        self.path = None              # Source data file path
        self.export_path = None       # Output file path


def update_metadata(old, new):
    """
    Updates metadata dictionary by merging new non-empty values with existing ones.
    
    This function safely updates an existing metadata dictionary with new values,
    only adding entries that are not None and not empty strings. This prevents
    overwriting valid existing data with empty values.
    
    Args:
        old (dict): The existing metadata dictionary to update
        new (dict): The new metadata dictionary containing potential updates
        
    Returns:
        None: Modifies the old dictionary in place
        
    Example:
        old_meta = {'Title': 'Example', 'Author': ''}
        new_meta = {'Author': 'John Doe', 'Keywords': ''}
        update_metadata(old_meta, new_meta)
        # old_meta now contains: {'Title': 'Example', 'Author': 'John Doe'}
    """
    tmp = {}
    for k, v in new.items():
        if v is not None and v != "":
            tmp[k] = v
    old.update(tmp)


def format_link(link):
    """
    Formats a link by URL-encoding special characters for safe file system usage.
    
    This function converts special characters (like /, :, *, ?, <, >, |, \, ") 
    into their URL-encoded equivalents to create safe filenames. This is essential
    for saving HTML files and other resources that use article titles or URLs
    as filenames.
    
    Args:
        link (str): The original link or text to format
        
    Returns:
        str: The formatted string with special characters URL-encoded, 
             truncated to 200 characters to avoid filesystem path length limits
             
    Example:
        format_link("Title: A Study of AI/ML?")
        # Returns: "Title%3A A Study of AI%2FML%3F"
    """
    formated_link = link
    for k in special_char_conversion.keys():
        formated_link = formated_link.replace(k, "%" + special_char_conversion[k])
    formated_link = formated_link[:200]
    return formated_link


def save_extracted_html(link, html):
    """
    Saves extracted HTML content to a file with a formatted filename.
    
    This function stores HTML content retrieved from academic sources to disk
    for later processing and metadata extraction. The filename includes the
    current date and a formatted version of the link/title to ensure uniqueness
    and avoid conflicts.
    
    Args:
        link (str): The original link or identifier to be formatted for filename
        html (str): The HTML content to save
        
    Returns:
        None: Saves the HTML file to the EXTRACTED_PATH/HTML extracted/ directory
        
    File naming format:
        YYYY-MM-DD_formatted_link.html
        
    Note:
        The HTML content is encoded as UTF-8 before writing to handle special characters.
        Prints the filename and formatted link for debugging/tracking purposes.
    """
    formated_link = format_link(link)
    with open(f"{EXTRACTED_PATH}/HTML extracted/{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html", 'wb') as f:
        f.write(html.encode("utf-8"))
    print(f"{datetime.today().strftime('%Y-%m-%d')}_{formated_link}.html")
    print(formated_link)


def standardize_title(title):
    """
    Standardizes article titles for comparison and matching purposes.
    
    This function performs extensive cleaning and normalization of article titles
    to enable accurate matching between titles from different sources. It removes
    special characters, punctuation, HTML entities, and other formatting artifacts
    that could prevent successful title matching.
    
    Args:
        title (str): The original article title to standardize
        
    Returns:
        str: The standardized title with only alphabetic characters and spaces,
             words longer than 1 character, and Unicode characters converted to ASCII
             
    Cleaning operations performed:
        1. Remove illegal XML/Excel characters
        2. Convert to lowercase
        3. Remove various quote characters and HTML entities
        4. Remove punctuation, symbols, and formatting characters
        5. Keep only alphabetic characters and spaces
        6. Convert Unicode to ASCII equivalents
        7. Remove single-character words
        8. Join remaining words with single spaces
        
    Example:
        standardize_title("A Study of AI/ML: Modern Approaches")
        # Returns: "study modern approaches"
        
    Note:
        This is used primarily for title matching and comparison, not for display.
        Prints intermediate steps for debugging purposes.
    """
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
    """
    Validates if extracted metadata corresponds to the target article title.
    
    This function performs fuzzy matching between the original article title and
    the title extracted from a web source to determine if they refer to the same
    article. It uses multiple criteria including substring matching, edit distance,
    and length differences to make the determination.
    
    Args:
        new_metadata (dict): Dictionary containing metadata extracted from web source,
                           must contain 'Title' key
        title (str): The original article title to match against
        author (str, optional): Author information for additional validation (not currently used)
        venue (str, optional): Venue information for additional validation (not currently used)
        year (str, optional): Publication year for additional validation (not currently used)
        
    Returns:
        bool: True if the metadata appears to match the target article, False otherwise
        
    Matching criteria (any must be satisfied):
        1. One standardized title is a substring of the other
        2. Edit distance between standardized titles < 3
        3. Word count difference < 4 OR character count difference < 10
        
    Example:
        metadata = {'Title': 'A Study of Machine Learning Approaches'}
        original = 'Study of ML Approaches'
        check_if_right_link(metadata, original)  # Returns True
        
    Note:
        Uses standardize_title() for normalization before comparison.
        Prints intermediate standardized titles for debugging.
        Additional matching criteria using author, venue, year could be implemented.
    """
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


