"""HTML Parser Module for Academic Metadata Extraction

This module provides functions to parse HTML content from various academic databases
and extract structured metadata including titles, authors, abstracts, keywords, and more.

Supported Academic Sources:
- IEEE Xplore
- ACM Digital Library  
- ScienceDirect (Elsevier)
- SpringerLink
- Scopus (both guest and signed-in)
- Web of Science
- PubMed Central
- arXiv
"""

from ..core.SRProject import *
from bs4 import BeautifulSoup
import re
from pybtex.database.input import bibtex as bibtex_parser
from unidecode import unidecode

from ..core.os_path import EXTRACTED_PATH


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_source(link):
    """Determine the academic source from a link URL.
    
    Args:
        link (str): URL or filename containing source information
        
    Returns:
        str: Source name (e.g., 'IEEE', 'ACM', 'ScienceDirect') or None
    """
    source = None
    for name in sources_name:
        if str.lower(name) in str.lower(link):
            source = name
        elif link[-8:-5] in ['_' + k for k in code_source.keys()]:
            source = code_source[link[-7:-5]]
    return source


def update_metadata(old, new):
    """Update metadata dictionary with non-None values only.
    
    Args:
        old (dict): Existing metadata dictionary to update
        new (dict): New metadata values to merge in
    """
    tmp = {}
    for k, v in new.items():
        if v is not None:
            tmp[k] = v
    old.update(tmp)

# =============================================================================
# TEXT CLEANING FUNCTIONS
# =============================================================================

def clean_abstract(abstract):
    """Clean and normalize abstract text.
    
    Removes common prefixes like 'Abstract:' and copyright notices.
    Converts Unicode characters to ASCII equivalents.
    
    Args:
        abstract (str): Raw abstract text
        
    Returns:
        str: Cleaned abstract text
    """
    if not abstract:
        return abstract
    
    # Convert Unicode to ASCII
    abstract = unidecode(abstract)
    
    # Remove common abstract prefixes
    abstract = abstract[len('Abstract:'):] if abstract.startswith('Abstract:') else abstract
    abstract = abstract[len('Abstract'):] if abstract.startswith('Abstract') else abstract
    
    # Remove copyright notices
    abstract = re.sub(r'(?:\(c\)|\(C\)|Copyright)\s*(.*)', '', abstract)
    
    return abstract
    
def clean_authors(authors):
    """Clean and normalize author names.
    
    Removes numbers, ORCID identifiers, and unwanted punctuation.
    Filters out connecting words like 'and'.
    
    Args:
        authors (list): List of raw author name strings
        
    Returns:
        list: List of cleaned author names
    """
    results = []
    for author in authors:
        # Convert Unicode to ASCII
        author = unidecode(author)
        if len(author) == 0: 
            continue
        
        # Remove unwanted punctuation and identifiers
        author = re.sub(',;', '', author)
        author = re.sub(r'[0-9]+', '', author)  # Remove numbers
        author = re.sub(r"ORCID:orcid\.org/---", '', author)  # Remove ORCID IDs
        
        # Remove connecting words and extra spaces
        author = " ".join([x for x in author.split() if x != "and" and x != ""])
        
        # Remove trailing punctuation
        if author and author[-1] in [',', '&']:
            author = author[:-1]
        
        results.append(author)
    return results

def clean_publisher(publisher: str):
    """Clean and normalize publisher name.
    
    Removes copyright notices, leading/trailing numbers, and punctuation.
    
    Args:
        publisher (str): Raw publisher name
        
    Returns:
        str: Cleaned publisher name
    """
    if not publisher:
        return publisher
    
    # Convert Unicode to ASCII
    publisher = unidecode(publisher)
    
    # Remove copyright notices
    publisher = publisher.replace('All rights reserved.', '')
    
    # Remove leading numbers and separators
    publisher = re.sub(r'^\d+[-,\d\s]*?(?=[A-Za-z])', '', publisher.strip())
    
    # Remove trailing numbers and content
    publisher = re.sub(r'\d+\s*.*$', '', publisher.strip())
    
    # Remove trailing period
    if publisher and publisher[-1] == '.':
        publisher = publisher[:-1]
    
    return publisher

def clean_title(title: str):
    """Clean and normalize article title.
    
    Removes common article type prefixes and converts Unicode to ASCII.
    
    Args:
        title (str): Raw article title
        
    Returns:
        str: Cleaned title
    """
    if not title:
        return title
    
    # Convert Unicode to ASCII
    title = unidecode(title)
    
    # Remove common article type prefixes
    title = re.sub(r"^(Original Article|RETRACTED ARTICLE:|Technical Note|^Review(?=[A-Z])|^Article(?=[A-Z])|Demo:|Original article|REVIEW)\s*", "", title)
    
    return title


# =============================================================================\n# METADATA PROCESSING\n# =============================================================================\n\ndef assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher, source):
    \"\"\"Create a standardized metadata dictionary from extracted content.\n    \n    Args:\n        title (str): Article title\n        venue (str): Publication venue/journal\n        authors (list): List of author names\n        pages (str): Page numbers or range\n        abstract (str): Article abstract\n        keywords (list): List of keywords\n        references (list): List of references\n        doi (str): Digital Object Identifier\n        publisher (str): Publisher name\n        source (str): Academic database source\n        \n    Returns:\n        dict: Standardized metadata dictionary\n    \"\"\"\n    # Initialize with base metadata structure
    metadata = metadata_base.copy()
    metadata['Title'] = clean_title(title)
    metadata['Venue'] = venue
    metadata['Pages'] = pages
    metadata['Authors'] = "; ".join(clean_authors(authors)) if authors is not None else None
    metadata['Abstract'] = clean_abstract(abstract)
    metadata['Keywords'] = "; ".join(str(x).strip() for x in keywords) if keywords is not None else None
    metadata['References'] = "; ".join(references) if references is not None else None
    metadata['DOI'] = doi
    metadata['Publisher'] = clean_publisher(publisher)
    metadata['Source'] = source

    # verify if contains symbols not accepted
    for key in ['Authors']:
        for s in ['{', '}', '\\']:
            if metadata[key] and s in metadata[key]:
                metadata[key] = None

    return metadata


def get_source_from_doi_with_crossref(html):\n    \"\"\"Extract publisher information from CrossRef API HTML response.\n    \n    Args:\n        html (str): HTML content from CrossRef API\n        \n    Returns:\n        str: Publisher name extracted from CrossRef data\n    \"\"\"\n    soup = BeautifulSoup(html, 'lxml')
    # Extract the venue
    source = None
    source_tag = soup.find('div', {'id': 'json'})
    if source_tag:
        venue_section = source_tag.get_text(strip=True)
        first_half = venue_section[venue_section.find('\"publisher\"')+12:]
        source = first_half[:first_half.find(",")][1:-1]
    else:
        source_tag = soup.find('tr', {'id': '/message/publisher'})
        if source_tag:
            source = source_tag.get_text(strip=True)
    return source


def get_metadata_from_bibtex(bib_data):\n    \"\"\"Extract metadata from parsed BibTeX data.\n    \n    Args:\n        bib_data: Parsed BibTeX database object from pybtex\n        \n    Returns:\n        dict: Extracted metadata dictionary\n    \"\"\"\n    metadata = metadata_base.copy()
    bib_key = list(bib_data.entries.keys())[0]
    bib_dict = bib_data.entries[bib_key].fields
    metadata['Title'] = bib_dict['title'] if 'title' in bib_dict.keys() else None
    metadata['Venue'] = bib_dict['journal'] if 'journal' in bib_dict.keys() else None
    metadata['Authors'] = '; '.join(clean_authors([str(x) for x in bib_data.entries[bib_key].persons['author']])) if 'author' in bib_data.entries[bib_key].persons.keys() else None
    metadata['Abstract'] = clean_abstract(bib_dict['abstract']) if 'abstract' in bib_dict.keys() else None
    metadata['Keywords'] = '; '.join(str(x) for x in bib_dict['keywords'].split(',') + bib_dict['keywords'].split(';') if x != "") if 'keywords' in bib_dict.keys() else None
    metadata['References'] = bib_dict['cited-references'] if 'cited-references' in bib_dict.keys() else None
    metadata['Pages'] = bib_dict['pages'] if 'pages' in bib_dict.keys() else None
    metadata['Year'] = bib_dict['year'] if 'year' in bib_dict.keys() else None
    metadata['Bibtex'] = bib_data.to_string("bibtex")
    metadata['DOI'] = bib_dict['doi'] if 'doi' in bib_dict.keys() else None
    metadata['Source'] = bib_dict['source'] if 'source' in bib_dict.keys() else None
    metadata['Link'] = bib_dict['url'] if 'url' in bib_dict.keys() else None
    metadata['Publisher'] = clean_publisher(bib_dict['publisher']) if 'publisher' in bib_dict.keys() else None

    for key in metadata.keys():
        if metadata[key]:
            metadata[key] = unidecode(metadata[key])

    return metadata


def get_metadata_from_already_extract(file, source=None):\n    \"\"\"Extract metadata from previously downloaded HTML or BibTeX files.\n    \n    This function serves as a dispatcher that routes to appropriate parsers\n    based on file type and identified source.\n    \n    Args:\n        file (str): Filename of the cached content\n        source (str, optional): Known source identifier\n        \n    Returns:\n        dict: Extracted metadata dictionary\n    \"\"\"\n    metadata = metadata_base.copy()
    if file[-4:] == "html":
        # Process HTML files
        with open(f"{EXTRACTED_PATH}/HTML extracted/" + file, 'rb') as f:
            html = unidecode(f.read().decode('utf-8', 'ignore'))
            source = get_source(file) if source is None else source
            
            # If source still unknown, try to get it from CrossRef
            if source is None:
                with open(f"{EXTRACTED_PATH}/HTML extracted/"
                          + file[:11] + "http%3A%2F%2Fapi.crossref.org%2Fworks%2F" + file[file.find("doi.org%2F")+10:-5] + ".html", 'rb') as g:
                    crossref_html = g.read()
                source = get_source_from_doi_with_crossref(crossref_html)
            
            # Route to appropriate parser based on identified source
            if source == IEEE or source == 'ieee':
                new_metadata = get_metadata_from_html_ieee(html)
                update_metadata(metadata, new_metadata)
            elif source == ScienceDirect or source == 'sciencedirect':
                new_metadata = get_metadata_from_html_sciencedirect(html)
                update_metadata(metadata, new_metadata)
            elif source == ACM or source == 'acm' or "ACM" in source:
                new_metadata = get_metadata_from_html_ACM(html)
                metadata.update(new_metadata)
            elif source == SpringerLink or source == 'springer':
                new_metadata = get_metadata_from_html_springerlink(html)
                metadata.update(new_metadata)
            elif source == Scopus or source == 'scopus':
                new_metadata = get_metadata_from_html_scopus(html)
                metadata.update(new_metadata)
            elif source == ScopusSignedIn:
                new_metadata = get_metadata_from_html_scopus_signed_in(html)
                metadata.update(new_metadata)
            elif source == WoS or source == 'wos':
                new_metadata = get_metadata_from_html_wos(html)
                metadata.update(new_metadata)
            elif source == PubMedCentral:
                new_metadata = get_metadata_from_html_pub_med_central(html)
                metadata.update(new_metadata)
            elif source == arXiv:
                new_metadata = get_metadata_from_html_arxiv(html)
                metadata.update(new_metadata)

    elif file[-3:] == "bib":
        # Process BibTeX files
        parser = bibtex_parser.Parser()
        bib_data = parser.parse_file(f'{EXTRACTED_PATH}/Bibtex/{file}')
        metadata = get_metadata_from_bibtex(bib_data)
        metadata['Source'] = code_source[file[-6:-4]]
    return metadata


# =============================================================================\n# SOURCE-SPECIFIC HTML PARSERS\n# =============================================================================\n\ndef get_metadata_from_html_ieee(html):\n    \"\"\"Extract metadata from IEEE Xplore HTML content.\n    \n    Args:\n        html (str): Raw HTML content from IEEE Xplore\n        \n    Returns:\n        dict: Extracted metadata dictionary\n    \"\"\"\n    soup = BeautifulSoup(html, 'lxml')

    # Extract the title
    title_tag = soup.find('h1', {'class': 'document-title'})
    title = title_tag.get_text(strip=True) if title_tag else None

    # Extract the pages
    pages_anchor = soup.find('div', {'class': 'doc-abstract-pubdate'})
    pages_section = pages_anchor.parent.find('div', {'class': 'u-pb-1'}) if pages_anchor else None
    pages_text = pages_section.get_text(strip=True) if pages_section else None
    pages = pages_text[pages_text.find('Page(s):')+len('Page(s):'):] if pages_text else None
    # pages_tag = pages_section.find('span') if pages_section else None
    # pages = pages_tag.get_text(strip=True) if pages_tag else None

    # Extract the venue
    venue_section = soup.find('div', {'class': 'stats-document-abstract-publishedIn'})
    if venue_section:
        venue_tag = venue_section.find('a')
        venue = venue_tag.get_text(strip=True) if venue_tag else None
    else:
        venue = None

    # Extract the abstract
    abstract_tag = soup.find('meta', {'property': 'og:description'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
    if not abstract:
        abstract_section = soup.find('div', {'class': 'abstract-text'})
        try:
            abstract_tag = abstract_section.find('div').find('div').find('div') if abstract_section else None
            abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
        except:
            abstract = None

    # Extract the authors
    authors = []
    authors_section = soup.find('div', {'class': 'authors-info-container'})
    if authors_section:
        authors_tag = authors_section.find_all('span', {'class': 'blue-tooltip'})
        authors = [author.get_text(strip=True) for author in authors_tag]
        if len(authors) == 0:
            authors_section = soup.find('div', {'class': 'authors-container'})
            authors_tag = authors_section.find_all('span', {'class': 'authors-info'}) if authors_section else []
            authors = [author.get_text(strip=True) for author in authors_tag]
    authors = None if len(authors) == 0 else authors

    # Extract the keywords
    keywords_section = soup.find('ul', {'class': 'doc-keywords-list stats-keywords-list'})
    if keywords_section:
        key_tags = keywords_section.find_all('a', {'class': 'stats-keywords-list-item'})
        keywords = [key.text.strip() for key in key_tags]
    else:
        keywords = None

    # Extract the references
    references_section = soup.find('div', {'id': 'references-section-container'})
    references = []
    if references_section:
        ref_tags = soup.find_all('div', {'class': 'reference-container'})
        references = [ref.text.strip() for ref in ref_tags]
    else:
        references = None

    # Extract the DOI
    doi_element = soup.find('div', {'class': 'stats-document-abstract-doi'})
    doi = doi_element.text.split(":")[1].strip() if doi_element else None

    # Extract the publisher
    publisher_section = soup.find('span', {'class': 'publisher-info-container'})
    publisher_text = publisher_section.get_text(strip=True) if publisher_section else None
    publisher = publisher_text[publisher_text.find("Publisher:")+10:] if publisher_text else None

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher, "IEEE")

def get_metadata_from_html_ACM(html):\n    \"\"\"Extract metadata from ACM Digital Library HTML content.\n    \n    Args:\n        html (str): Raw HTML content from ACM Digital Library\n        \n    Returns:\n        dict: Extracted metadata dictionary\n    \"\"\"\n    soup = BeautifulSoup(html, 'lxml')
    # Extract the title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else None

    # Extract the authors
    authors = []
    author_tags = soup.find_all('a', {'class': 'author-name'})
    if author_tags:
        for tag in author_tags:
            authors.append(tag['title'].strip())
    else:
        author_tags = soup.find_all('span', {'property': 'author'})
        if author_tags:
            for tag in author_tags:
                name = tag.find('span', {'property': 'givenName'})
                family_name = tag.find('span', {'property': 'familyName'})
                if name and family_name:
                    authors.append(name.get_text(strip=True) + " " + family_name.get_text(strip=True))
                else:
                    authors.append(tag.get_text(strip=True))
        else:
            authors_section = soup.find('ul', {'id':'authorsListId-mfxh'})
            if authors_section:
                author_tags = authors_section.find_all('li')
                authors = [x.get_text(strip=True) for x in author_tags if not ('class' in x.attrs.keys() and x.attrs['class'] in ['label', 'count-list'])]
            authors = None if len(authors) == 0 else authors

    # Extract the venue
    venue_tag = soup.find('span', {'class': 'epub-section__title'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None
    if venue is None:
        venue_tag = soup.find('div', {'property': 'core-self-citation'})
        venue = venue_tag.get_text(strip=True) if venue_tag else None
    if venue is None:
        venue_tag = soup.find('div', {'property': 'isPartOf'})
        venue = venue_tag.get_text(strip=True) if venue_tag else None


    # Extract the pages
    pages = None
    pages_tag = soup.find('span', {'class': 'epub-section__pagerange'})
    pages_text = pages_tag.get_text(strip=True) if pages_tag else None
    if pages_text is None:
        pages_tag = soup.find('div', {'property': 'pagination'})
        pages_text = pages_tag.get_text(strip=True) if pages_tag else None
    if pages_text is not None and "Pages" in pages_text:
        pages = pages_text[pages_text.find('Pages')+5:] if pages_text else None
    elif pages_text is not None and "pp" in pages_text:
        pages = pages_text[pages_text.find('pp')+2:] if pages_text else None
        
    # Extract the abstract
    abstract_tag = soup.find('div', {'class': 'abstractSection abstractInFull'})
    abstract = abstract_tag.text.strip() if abstract_tag else None
    if abstract is None:
        abstract_section = soup.find('section', {'id': 'abstract'})
        abstract_tag = abstract_section.find('div', {'role': 'paragraph'}) if abstract_section else None
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None

    # Extract the keywords
    keywords = []
    keywords_section = soup.find('section', {'property': 'keywords'})
    if keywords_section:
        for tag in keywords_section.find_all('li'):
            keywords.append(tag.get_text(strip=True))
    if len(keywords) == 0: keywords = None

    # Extract the references
    references = []
    reference_section = soup.find('div', {'class': 'references'})
    if reference_section:
        reference_tags = soup.find_all('div', {'class': 'reference'})
        for tag in reference_tags:
            references.append(tag.text.strip())
    else:
        references = None

    # Extract the DOI
    doi = None
    doi_tag = soup.find('meta', {'name': 'publication_doi'})
    doi = doi_tag.get_text(strip=True) if doi_tag else None
    if not doi:
        doi_tag = soup.find('meta', {'name': 'dc.Identifier', 'scheme': 'doi'})
        doi = doi_tag['content'].strip() if doi_tag else None
        if not doi:
            doi_tag = soup.find('div', {'class': 'doi'})
            doi_text = doi_tag.get_text(strip=True) if doi_tag else None
            doi = doi_text[doi_text.find('doi.org/')+8:] if doi_text else None

    # Extract the publisher
    publisher_tag = soup.find('p', {'class': 'publisher__name'})
    publisher = publisher_tag.get_text(strip=True) if publisher_tag else "Association for Computing Machinery"

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher, "ACM")


def get_metadata_from_html_sciencedirect(html):\n    \"\"\"Extract metadata from ScienceDirect (Elsevier) HTML content.\n    \n    Args:\n        html (str): Raw HTML content from ScienceDirect\n        \n    Returns:\n        dict: Extracted metadata dictionary\n    \"\"\"\n    soup = BeautifulSoup(html, 'lxml')

    # Extract the title
    title_tag = soup.find('h1', {'id': 'screen-reader-main-title'})
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        title_tag = soup.find('meta', {'name': 'citation_title'})
        title = title_tag['content'].strip() if title_tag else None

    # Extract the venue
    venue_tag = soup.find('a', {'class': 'publication-title-link'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None

    # Extract the pages
    pages_section = soup.find('div', {'class': 'publication-volume'})
    if pages_section:
        pages_tag = pages_section.find('div', {'class': 'text-xs'})
        pages_text = pages_tag.get_text(strip=True) if pages_tag else None
        pages = pages_text[pages_text.find("Pages")+5:] if pages_text and 'Pages' in pages_text else None
        if not pages:
            pages = pages_text[pages_text.rfind(',')+1:].strip() if pages_text else None
            if not all(x.isdigit() for x in pages): pages = None
    else:
        pages = None

    # Extract the abstract
    abstract_tag = soup.find('div', {'class': 'abstract'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None

    # Extract the authors
    authors = []
    author_tags = soup.find_all('a', {'class': 'author-name'})
    if author_tags:
        for tag in author_tags:
            authors.append(tag['title'].strip())
    else:
        author_tags = soup.find_all('button', {'data-xocs-content-type': 'author'})
        if author_tags:
            for tag in author_tags:
                authors.append(tag.get_text(strip=True))
    if len(authors) == 0: authors = None

    # Extract the keywords
    keywords_section = soup.find('div', {'class': 'keyword'})
    keywords = []
    if keywords_section:
        key_tags = soup.find_all('div', {'class': 'keyword'})
        keywords = [key.text.strip() for key in key_tags]
    else:
        keywords = None

    # Extract the references
    references = []
    reference_section = soup.find('section', {'id': 'references'})
    if reference_section:
        reference_tags = reference_section.find_all('li')
        for tag in reference_tags:
            references.append(tag.text.strip())
    else:
        references = None

    # Extract the DOI
    doi_tag = soup.find('meta', {'name': 'citation_doi'})
    doi = doi_tag['content'].strip() if doi_tag else None

    # Extract the publisher
    publisher = "Science Direct"  # Elsevier?

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher,
                           "Science Direct")


def get_metadata_from_html_springerlink(html):
    """Extract metadata from SpringerLink HTML content.
    
    Args:
        html (str): Raw HTML content from SpringerLink
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'lxml')

    # Extract the title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else None

    # Extract the authors
    authors = []
    author_tags = soup.find_all('li', {'class': 'c-article-author-list__item'})
    for tag in author_tags:
        authors.append(tag.get_text(strip=True))
    if len(authors) == 0: authors = None

    # Extract the pages
    pages_tag = soup.find('span', {'class': 'c-chapter-book-details__meta'})
    pages = pages_tag.get_text(strip=True) if pages_tag else None
    pages = pages[pages.find('pp') + 2:].strip() if pages and 'pp' in pages else pages

    # Extract the venue
    venue_tag = soup.find('li', {'class': 'app-book-series-listing__item'})
    if venue_tag is None: venue_tag = soup.find('span', {'class': 'app-article-masthead__journal-title'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None

    # Extract the abstract
    abstract_tag = soup.find('div', {'id': 'Abs1-content'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None

    # Extract the keywords
    keywords = []
    keyword_tags = soup.find_all('li', {'class': 'c-article-subject-list__subject'})
    for tag in keyword_tags:
        keywords.append(tag.get_text(strip=True))
    if len(keywords) == 0: keywords = None

    # Extract the references
    references = []
    reference_tags = soup.find_all('meta', {'name': 'citation_reference'})
    for tag in reference_tags:
        references.append(tag['content'].strip())
    if len(references) == 0: references = None

    # Extract the DOI
    doi_tag = soup.find('meta', {'name': 'dc.identifier', 'content': lambda x: x and x.startswith('doi:')})
    doi = doi_tag['content'].replace('doi:', '').strip() if doi_tag else None
    if doi is None:
        doi_section = soup.find('p', {'data-test': 'bibliographic-information__doi'})
        doi_tag = doi_section.find('span', {'class': 'c-bibliographic-information__value'}) if doi_section else None
        doi_text = doi_tag.get_text(strip=True) if doi_tag else None
        doi = doi_text[doi_text.find('doi.org/')+8:] if doi_text else None

    # Extract the publisher
    publisher_section = soup.find('p', {'data-test': 'bibliographic-information__publisher-name'})
    publisher_tag = publisher_section.find('span', {'class': 'c-bibliographic-information__value'}) if publisher_section else None
    publisher = publisher_tag.get_text(strip=True) if publisher_tag else 'Springer Link'

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher, "Springer Link")


def get_metadata_from_html_scopus(html):
    """Extract metadata from Scopus (guest access) HTML content.
    
    Args:
        html (str): Raw HTML content from Scopus
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Function to extract title
    title_tag = soup.find('h2', {'class': 'h3'})
    title = title_tag.get_text()[:title_tag.get_text().find("(")] if title_tag else None
    if title and (' | Signed in' in title or 'Document details - ' in title or 'Scopus - ' in title):
        title = re.sub('Scopus - ', '', title)
        title = re.sub('Document details - ', '', title)
        title = re.sub(' | Signed in', '', title)

    # Extract venue
    venue_section = soup.find('section', {'id': 'articleTitleInfo'})
    venue_tag = venue_section.find('span', {'id': 'guestAccessSourceTitle'}) if venue_section else None
    venue = venue_tag.get_text(strip=True) if venue_tag else None

    # Extract publisher
    publisher_tag = soup.find('span', {'id': 'guestAccessSourceTitle'})
    publisher = publisher_tag.get_text(strip=True) if publisher_tag else None

    # Extract pages
    pages_tag = soup.find('span', {'id': "journalInfo"})
    pages_text = pages_tag.get_text(strip=True) if pages_tag else None
    pages = pages_text[pages_text.find("Pages")+5:] if pages_text and "Pages" in pages_text else None

    # Function to extract authors
    authors = []
    authors_section = soup.find('section', {'id': 'authorlist'})
    if authors_section:
        authors_tag = authors_section.find_all('span', {'class', 'previewTxt'})
        for author in authors_tag:
            authors.append(author.get_text(strip=True))
    authors = authors if authors else None

    # Function to extract abstract
    abstract = None
    abstract_section = soup.find('section', {'id': 'abstractSection'})
    if abstract_section:
        abstract_tag = abstract_section.find('p')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
    if not abstract_section:
        abstract_section = soup.find('div', {'class': 'Abstract-module__pTWiT'})
        abstract = abstract_section.get_text(strip=True) if abstract_section else None

    # Function to extract keywords
    keywords = []
    keywords_section = soup.find('section', {'id': 'authorKeywords'})
    if keywords_section:
        keywords_tag = keywords_section.find_all('span', {'class', 'badges'})
        for keyword in keywords_tag:
            key_text = keyword.get_text(strip=True)
            key_text = re.sub(';', '', key_text)
            key_text = key_text.replace(';', '')
            keywords.append(key_text)
    keywords = keywords if len(keywords) > 0 else None

    # Function to extract references
    references = []
    references_section = soup.find('ol', class_='references')
    if references_section:
        for ref in references_section.find_all('li'):
            references.append(ref.get_text(strip=True))
    references = references if references else None

    # Function to extract DOI
    doi_tag = soup.find('meta', {'name': 'dc.identifier'})
    doi = doi_tag['content'] if doi_tag else None

    # Extract the publisher
    publisher_section = soup.find('ul', {'id': 'documentInfo'})
    publisher_section_text = publisher_section.get_text(strip=True) if publisher_section else None
    publisher = publisher_section_text[publisher_section_text.find('Publisher:')+10:] if publisher_section_text and 'Publisher' in publisher_section_text else None
    if not publisher and abstract and '(c)' in abstract:
        publisher = abstract[abstract.find('(c)')+3:]
    if not publisher and abstract and 'Copyright' in abstract:
        publisher = abstract[abstract.find('Copyright')+len('Copyright'):]

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher, "Scopus")


def get_metadata_from_html_scopus_signed_in(html):
    """Extract metadata from Scopus (signed-in) HTML content.
    
    Args:
        html (str): Raw HTML content from Scopus with user authentication
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'lxml')

    # Extract the title
    title_section = soup.find('div', {'data-testid': 'document-title'})
    title_tag = title_section.find('h2') if title_section else None
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else None
        if title and (' | Signed in' in title or 'Document details - ' in title or 'Scopus - ' in title):
            title = re.sub('Scopus - ', '', title)
            title = re.sub('Document details - ', '', title)
            title = re.sub(' | Signed in', '', title)

    # Extract the venue
    venue_tag = soup.find('a', {'class': 'source-preview-flyout'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None

    # Extract the pages
    pages_section = soup.find('div', {'class': 'PublicationInformationBar-module__mhocT'})
    if pages_section:
        pages_tag = pages_section.find('span', {'class': 'Typography-module__lVnit'})
        pages_text = pages_tag.get_text(strip=True) if pages_tag else None
        pages = pages_text[:pages_text.find("Pages")+5] if pages_text and "Pages" in pages_text else None
    else:
        pages = None

    # Extract the abstract
    abstract_tag = soup.find('div', {'class': 'Abstract-module__pTWiT'})
    abstract = abstract_tag.get_text() if abstract_tag else None


    # Extract the authors
    authors = []
    authors_section = soup.find_all('a', class_='authorName')
    authors = [author.get_text(strip=True) for author in authors_section] if authors_section else None

    # Extract the keywords
    keywords_section = soup.find('h3', {'id': 'author-keywords'})
    keywords = []
    if keywords_section:
        key_tags = soup.find_all('span', {'class': 'AuthorKeywords-module__tuDgJ'})
        keywords = [key.get_text(strip=True) for key in key_tags]
    else:
        keywords = None

    # Extract the references
    references = []
    reference_section = soup.find('tbody', {'class': 'referencesUL'})
    if reference_section:
        reference_tags = reference_section.find_all('div', {'class': 'refAuthorTitle'})
        for ref_tag in reference_tags:
            references.append(ref_tag.get_text(strip=True) if ref_tag else "")
    else:
        references = None

    # Extract the DOI
    doi_section = soup.find('dl', {'data-testid': 'source-info-entry-doi'})
    doi_tag = doi_section.find('dd') if doi_section else None
    doi = doi_tag.get_text(strip=True) if doi_tag else None

    # Extract the publisher
    publisher = None

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher,
                           "Scopus")


def get_metadata_from_html_wos(html):
    """Extract metadata from Web of Science HTML content.
    
    Args:
        html (str): Raw HTML content from Web of Science
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else None
    title = title[:title.index("-Web of Science Core Collection")] if "-Web of Science Core Collection" in title else title

    # Extract the authors
    authors_tag = soup.find_all('span', {'id': re.compile(r"SumAuthTa-FrAuthStandard-author-en-.*")})
    if not authors_tag:
        authors_tag = soup.find_all('span', {'id': re.compile(r"SumAuthTa-DisplayName-author-en-.*")})
    if not authors_tag:
        authors_tag = soup.find_all('a', {'id': re.compile(r"SumAuthTa-DisplayName-author-en-.*")})
    if not authors_tag:
        authors_tag = soup.find_all('a', {'id': re.compile(r"SumAuthTa-FrAuthStandard-author-en-.*")})
    authors = [author.get_text(strip=True)[1:-1] for author in authors_tag] if authors_tag else None

    # Extract the venue
    venue_tag = soup.find('a', {'class': 'summary-source-title-link'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None
    if not venue:
        venue_tag = soup.find('span', {'class': 'summary-source-title'})
        venue = venue_tag.get_text(strip=True) if venue_tag else None
    if venue and 'arrow_drop_down' in venue:
        venue = re.sub('arrow_drop_down', '', venue)

    # Extract the pages
    pages_tag = soup.find('span', {'id': 'FullRTa-pageNo'})
    pages = pages_tag.get_text(strip=True) if pages_tag else None

    # Extract the abstract
    abstract_tag = soup.find('div', {'id': 'FullRTa-abstract-basic'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None

    # Extract the keywords
    keywords_tag = soup.find_all('a', {'id': re.compile(r"FRkeywordsTa-authorKeywordLink-.*")})
    if keywords_tag:
        keywords = [keyword.get_text(strip=True) for keyword in keywords_tag]
    else:
        keywords = None

    # Extract the references
    references = None

    # Extract the DOI
    doi_tag = soup.find('span', {'id': 'FullRTa-DOI'})
    doi = doi_tag.get_text(strip=True) if doi_tag else None

    # Extract the publisher
    publisher_div = soup.find('div', {'class': 'journal-content'})
    if not publisher_div:
        publisher_div = soup.find('div', {'id': 'snJournalData'})
    publisher_section = publisher_div.find(lambda tag: tag.name=='div' and 'Publisher' in tag.text and 'class' in tag.attrs.keys()
                                                       and 'journal-content-row' in tag.attrs['class']) if publisher_div else None
    publisher_tag = publisher_section.find('span', {'class': 'value'}) if publisher_section else None
    if not publisher_tag:
        publisher_tag = publisher_section.find('span', {'class': 'cdx-grid-data'}) if publisher_section else None
    if not publisher_tag:
        publisher_tag = publisher_section.find('span', {'class': 'section-label-data'}) if publisher_section else None
    publisher = publisher_tag.get_text(strip=True) if publisher_tag else None

    if not publisher:
        publisher_section = soup.find('div', {'id': 'snJournalData'})
        publisher_section_text = publisher_section.get_text(strip=True) if publisher_section else None
        publisher_start_index = publisher_section_text.find('Publisher name') + len(
            'Publisher name') if publisher_section_text else None
        publisher_end_index = publisher_section_text[publisher_start_index:].find(
            'Journal') + publisher_start_index if publisher_start_index else None
        publisher = publisher_section_text[publisher_start_index:publisher_end_index] if publisher_end_index else None

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher,
                           "Web of Science")


def get_metadata_from_html_pub_med_central(html):
    """Extract metadata from PubMed Central HTML content.
    
    Args:
        html (str): Raw HTML content from PubMed Central
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else None

    # Extract the authors
    authors_tag = soup.find_all('span', {'class': 'authors-list-item'})
    if authors_tag:
        authors = [author.get_text(strip=True) for author in authors_tag]
    else:
        authors = None

    # Extract the venue
    venue_tag = soup.find('button', {'id': 'full-view-journal-trigger'})
    venue = venue_tag.get_text(strip=True) if venue_tag else None

    # Extract the pages
    pages_tag = soup.find('span', {'class': 'cit'})
    pages_text = pages_tag.get_text(strip=True) if pages_tag else None
    pages = pages_text[pages_text.rfind(':')+1:-1] if pages_text else None

    # Extract the abstract
    abstract_tag = soup.find('div', {'id': 'abstract'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
    if abstract and abstract[:8] == 'Abstract':
        abstract = abstract[8:]

    # Extract the keywords
    keywords = None

    # Extract the references
    references = None

    # Extract the DOI
    doi_tag = soup.find('span', {'class': 'doi'})
    doi = doi_tag.get_text(strip=True) if doi_tag else None

    # Extract the publisher
    publisher_section = soup.find('div', {'id': 'snJournalData'})
    publisher_section_text = publisher_section.get_text(strip=True) if publisher_section else None
    publisher_start_index = publisher_section_text.find('Publisher name') + len('Publisher name') if publisher_section_text else None
    publisher_end_index = publisher_section_text[publisher_start_index:].find('Journal') + publisher_start_index if publisher_start_index else None
    publisher = publisher_section_text[publisher_start_index:publisher_end_index] if publisher_end_index else None

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher,
                           "Pub Med Central")


def get_metadata_from_html_arxiv(html):
    """Extract metadata from arXiv HTML content.
    
    Args:
        html (str): Raw HTML content from arXiv preprint server
        
    Returns:
        dict: Extracted metadata dictionary
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1', {'class': 'title'})
    title_text = title_tag.get_text(strip=True) if title_tag else None
    title = title_text[title_text.find("Title:")+6:]

    # Extract the authors
    authors_section = soup.find('div', {'class': 'authors'})
    authors_tag = authors_section.find_all('a') if authors_section else None
    if authors_tag:
        authors = [author.get_text(strip=True) for author in authors_tag]
    else:
        authors = None

    # Extract the venue
    venue = "arXiv"

    # Extract the pages
    pages = None

    # Extract the abstract
    abstract_tag = soup.find('blockquote', {'class': 'abstract'})
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else None

    # Extract the keywords
    keywords = None

    # Extract the references
    references = None

    # Extract the DOI
    doi_tag = soup.find('a', {'id': 'arxiv-doi-link'})
    doi_text = doi_tag.get_text(strip=True) if doi_tag else None
    doi = doi_text[doi_text.find("doi.org/")+8:] if doi_text else None

    # Extract the publisher
    publisher = 'arXiv'

    # Return the metadata
    return assign_metadata(title, venue, authors, pages, abstract, keywords, references, doi, publisher,
                           "arXiv")

