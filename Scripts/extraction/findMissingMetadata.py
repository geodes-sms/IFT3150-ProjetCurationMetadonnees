"""Missing Metadata Extraction Module

This module provides the core pipeline for finding and extracting missing metadata
from systematic literature review datasets. It coordinates web scraping, cached file
retrieval, and data cleaning to automatically populate incomplete article records.

Key Features:
- Automated metadata extraction from 8+ academic databases
- Intelligent caching system to avoid redundant web requests
- Fallback strategies when primary extraction methods fail
- Quality validation and error tracking
- Support for both link-based and title-based article searches

Author: Guillaume Genois, 20248507
Purpose: Automated metadata curation for systematic literature reviews
"""

import os
import random
import time
import traceback

import pandas as pd
from selenium.common import NoSuchElementException

from . import htmlParser
from . import webScraping
from ..core.SRProject import *
from .webScraping import WebScraper
from ..core.os_path import *
from unidecode import unidecode


def get_link_from_articles_source_links(title):
    """
    Retrieves a cached article link from the source links tracking file.
    
    This function checks if an article title has been previously processed and
    stored in the articles_source_links.tsv cache file. If found, it returns
    the cached link to avoid redundant web scraping operations.
    
    Args:
        title (str): The article title to search for in the cache
        
    Returns:
        str or None: The cached link URL if found, None otherwise
        
    Note:
        - Uses windows-1252 encoding to handle special characters
        - Returns the last found link if multiple entries exist for the same title
        - Prints a message when a cached link is found for debugging purposes
        
    File format:
        Tab-separated values with columns: Title, Link
    """
    try:
        # Load the cached article links database
        links_already_searched = pd.read_csv(
            f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv', 
            sep='\t',
            encoding='windows-1252', 
            encoding_errors='ignore'
        )
        links_already_searched['Title'] = links_already_searched['Title'].astype(str)
        
        # Check if the title exists in our cache
        if title in links_already_searched['Title'].values:
            print("link already searched, adding it instead of DOI")
            # Return the most recent link if multiple entries exist
            return links_already_searched.loc[links_already_searched['Title'] == title]['Link'].values[-1]
            
    except FileNotFoundError:
        print("Warning: articles_source_links.tsv cache file not found")
        
    return None


def get_from_already_extract(formated_name, already_extracted_files, source=None):
    """
    Extracts metadata from previously saved HTML/BibTeX files matching the article name.
    
    This function searches through cached HTML and BibTeX files to find matches
    for a given article name, then extracts and returns the metadata. It handles
    different naming conventions and file formats used by various academic sources.
    
    Args:
        formated_name (str): The formatted article name/title to search for
        already_extracted_files (list): List of previously extracted filenames
        source (str, optional): Expected source type to filter files
        
    Returns:
        dict or None: Merged metadata dictionary if files are found and processed
                      successfully, None otherwise
                      
    File naming conventions handled:
        - IEEE: Separate files for references, keywords, and bibtex
        - Other sources: Single HTML/BibTeX files per article
        - Files named with pattern: YYYY-MM-DD_formatted_title_source_code.ext
        
    Metadata sources prioritized:
        1. HTML files (for content parsing)
        2. BibTeX files (for bibliographic data)
        
    Note:
        - Tries both exact match and stripped version of formatted name
        - Merges metadata from multiple files for the same article
        - Handles different source code patterns in filenames
        - Logs processing steps for debugging
        
    Raises:
        Exception: Re-raises any exception encountered during metadata extraction
    """
    metadata = None
    print("formated_name", formated_name)
    
    # Try both the original formatted name and a stripped version
    for current_name in [formated_name, formated_name.strip()]:
        for file in already_extracted_files:
            try:
                new_metadata = None
                
                # Determine source from filename suffix code
                tmp_source = _extract_source_from_filename(file, source)
                
                # Handle IEEE special case (multiple files per article)
                if tmp_source == IEEE:
                    new_metadata = _extract_ieee_metadata(file, current_name)
                    
                # Handle other sources (single file per article)
                elif tmp_source is not None and _filename_matches_article(file, current_name):
                    print(file)
                    new_metadata = htmlParser.get_metadata_from_already_extract(file, tmp_source)
                
                # Merge extracted metadata
                if new_metadata:
                    if metadata:
                        update_metadata(metadata, new_metadata)
                    else:
                        metadata = new_metadata
                    print(metadata)
                    
            except Exception as e:
                print("Error extracting from file:", file, "Error:", e)
                raise Exception(e)
                
    return metadata


def _extract_source_from_filename(filename, fallback_source):
    """Extract academic source from filename suffix codes.
    
    Args:
        filename (str): The cached file name
        fallback_source (str): Default source if extraction fails
        
    Returns:
        str: The identified academic source
    """
    try:
        # Try extracting from 2-digit suffix (e.g., _01.html)
        return code_source[filename[-7:-5]]
    except (KeyError, IndexError):
        try:
            # Try extracting from 2-digit suffix (e.g., _1.html) 
            return code_source[filename[-6:-4]]
        except (KeyError, IndexError):
            return fallback_source


def _extract_ieee_metadata(filename, formatted_name):
    """Extract metadata from IEEE-specific file naming patterns.
    
    IEEE articles may have separate files for references, keywords, and bibtex.
    
    Args:
        filename (str): The IEEE file to process
        formatted_name (str): The formatted article name to match
        
    Returns:
        dict or None: Extracted metadata if file matches, None otherwise
    """
    # IEEE references file
    if filename[11:-8] == formatted_name + "%2Freferences#references":
        print(filename)
        return htmlParser.get_metadata_from_already_extract(filename, IEEE)
        
    # IEEE keywords file
    elif filename[11:-8] == formatted_name + "%2Fkeywords#keywords":
        print(filename)
        return htmlParser.get_metadata_from_already_extract(filename, IEEE)
        
    # IEEE BibTeX file
    elif filename[-3:] == 'bib' and filename[11:-7] == formatted_name:
        return htmlParser.get_metadata_from_already_extract(filename, IEEE)
        
    return None


def _filename_matches_article(filename, formatted_name):
    """Check if a filename matches the formatted article name.
    
    Args:
        filename (str): The file to check
        formatted_name (str): The formatted article name
        
    Returns:
        bool: True if filename matches the article
    """
    return (filename[11:-8] == formatted_name or filename[11:-7] == formatted_name)


# =============================================================================
# EXTRACTION STRATEGIES
# =============================================================================

def extract_without_link(row, already_extracted_files, web_scraper):
    """Extract metadata for articles without direct DOI/URL links.
    
    This function implements a multi-step fallback strategy:
    1. Check manual extraction cache
    2. Search cached extracted files by title
    3. Perform web scraping using title + author search
    4. Try extracting from newly discovered DOI
    
    Args:
        row (pd.Series): Article row from the dataset
        already_extracted_files (list): List of previously cached files
        web_scraper (WebScraper): Web scraping instance
        
    Returns:
        dict or None: Extracted metadata dictionary if successful
    """
    metadata = None
    source, year, authors = None, None, None
    
    # Extract available metadata from the row
    print(row[['title', 'source']])
    if not pd.isna(row['source']): 
        source = row['source']
    if not pd.isna(row['year']): 
        year = row['year']
    if not pd.isna(row['authors']): 
        authors = row['authors']

    print(f"Available metadata - Source: {source}, Authors: {authors}, Year: {year}")

    # Strategy 1: Check manual extraction cache
    try:
        articles_extract_manually = pd.read_csv(
            f'{MAIN_PATH}/Scripts/data/articles_extract_manually.tsv', 
            sep='\t'
        )
        
        if row['title'] in articles_extract_manually['meta_title'].values:
            print("Found in manual extraction cache, loading saved metadata")
            extract_row = articles_extract_manually.loc[
                articles_extract_manually['meta_title'] == row['title']
            ].iloc[0]
            extract_row = extract_row.apply(str)
            
            # Build metadata from manually extracted data
            metadata = metadata_base.copy()
            metadata['Title'] = unidecode(extract_row['title'])
            metadata['Abstract'] = unidecode(extract_row['abstract'])
            metadata['Keywords'] = unidecode(extract_row['keywords'])
            metadata['Authors'] = unidecode(extract_row['authors'])
            metadata['Venue'] = unidecode(extract_row['venue'])
            metadata['DOI'] = extract_row['doi']
            metadata['References'] = unidecode(extract_row['references'])
            metadata['Pages'] = unidecode(extract_row['pages'])
            metadata['Bibtex'] = unidecode(extract_row['bibtex'])
            metadata['Source'] = unidecode(extract_row['source'])
            metadata['Year'] = extract_row['year']
            metadata['Link'] = extract_row['link']
            metadata['Publisher'] = unidecode(extract_row['publisher'])
            return metadata
            
    except FileNotFoundError:
        print("Manual extraction cache not found, continuing with other strategies")

    # Strategy 2: Check if already extracted from cached files (by title)
    for column in ['title']:
        formated_name = format_link(str(row[column]))
        metadata = get_from_already_extract(formated_name, already_extracted_files)

    if metadata:
        print("Found in cached extraction files (without link)")
        print(f"Cached metadata DOI: {metadata['DOI']}")
        
        # Update source and authors from extracted metadata
        source = metadata['Source']
        authors = metadata['Authors']

        # Try to get the original link from our cache
        metadata['Link'] = get_link_from_articles_source_links(row['title'])
        
        # If DOI is missing, use the link as DOI
        if metadata['DOI'] is None or metadata['DOI'] == "":
            print("DOI missing in cached metadata, using link as DOI")
            metadata['DOI'] = metadata['Link']

    # Strategy 3: Web scraping when metadata is incomplete
    if (not metadata or 
        metadata['DOI'] is None or metadata['DOI'] == "" or 
        metadata['Bibtex'] is None or metadata['Bibtex'] == ""):

        print("Metadata incomplete or missing, attempting web scraping")
        print(f"Title: {row['title']}")
        print(f"Source: {source}")
        print(f"Authors: {authors}")
        print(f"Year: {year}")
        
        if web_scraper:
            # Perform title-based search on Scopus
            metadata = web_scraper.get_metadata_from_title(
                row['title'], 
                authors, 
                ScopusSignedIn
            )
            
            if metadata: 
                print("Successfully extracted metadata using title search")
            else: 
                print("No article found through title search")
            
            # Strategy 4: If we got a new DOI, try extracting from it
            if metadata and metadata['DOI']:
                print(f"Found new DOI: {metadata['DOI']}, attempting enhanced extraction")
                new_metadata = web_scraper.get_metadata_from_link(
                    row['title'], 
                    "https://doi.org/" + str(metadata['DOI']), 
                    metadata['Publisher']
                )
                
                if new_metadata and new_metadata['Title']:
                    update_metadata(metadata, new_metadata)
                    print("Enhanced metadata extraction from new DOI successful")

    print(metadata)
    return metadata


def extract_with_link(row, already_extracted_files, web_scraper: WebScraper):
    """Extract metadata for articles with existing DOI/URL links.
    
    This function implements a priority-based extraction strategy:
    1. Check if already extracted by URL/DOI
    2. Check if already extracted by title
    3. Perform fresh web scraping from the provided link
    4. Fall back to link-free extraction if needed
    
    Args:
        row (pd.Series): Article row containing DOI/URL
        already_extracted_files (list): List of cached files
        web_scraper (WebScraper): Web scraping instance
        
    Returns:
        dict or None: Extracted metadata dictionary if successful
    """
    metadata = None
    
    # Prepare URL and source information
    url = row['doi']
    formated_url = format_link(str(url))
    source = (htmlParser.get_source(formated_url) 
              if not row['source'] or pd.isna(row['source']) 
              else str(row['source']))
    
    # Strategy 1: Check if already extracted by URL
    metadata = get_from_already_extract(formated_url, already_extracted_files, source)

    # Strategy 2: Check if already extracted by title (fallback)
    formated_name = format_link(str(row['title']))
    if not metadata:
        metadata = get_from_already_extract(formated_name, already_extracted_files)

    # Update link information if found in cache
    if metadata:
        source_link = get_link_from_articles_source_links(row['title'])
        metadata['Link'] = source_link if source_link else url
        print("Found in extraction cache (with link)")

    # Strategy 3: Fresh web scraping if not in cache or incomplete
    if not metadata or metadata['Bibtex'] is None or metadata['Bibtex'] == "":
        if web_scraper:
            print(f"Attempting fresh extraction from link: {url}")
            
            # Retry mechanism for web scraping (up to 5 attempts)
            for attempt in range(5):
                try:
                    metadata = web_scraper.get_metadata_from_link(row['title'], url, source)
                    break
                except NoSuchElementException as e:
                    print(f"Web scraping attempt {attempt + 1} failed: {e}")
                    break  # Don't retry on NoSuchElementException
                except Exception as e:
                    print(f"Web scraping attempt {attempt + 1} failed: {e}")
                    if attempt < 4:  # Only reset scraper if we have more attempts
                        metadata = None
                        web_scraper.close()
                        web_scraper = webScraping.WebScraper()
                        continue
                        
            if metadata:
                print("Successfully extracted metadata from direct link")
                metadata['Link'] = url
            else: 
                print("Failed to extract metadata from provided link")

    # Strategy 4: Fall back to link-free extraction if direct link failed
    if (not metadata or 
        not metadata['Title'] or 
        metadata['Bibtex'] is None or metadata['Bibtex'] == ""):
        print("Direct link extraction incomplete, falling back to title-based search")
        metadata = extract_without_link(row, already_extracted_files, web_scraper)

    return metadata


# =============================================================================
# DATASET UPDATE FUNCTIONS
# =============================================================================

def update_dataset(row, metadata):
    """Update a dataset row with extracted metadata.
    
    This function applies extracted metadata to the corresponding dataset row,
    handling special cases for URLs, DOIs, and missing field tracking.
    
    Args:
        row (pd.Series): The dataset row to update
        metadata (dict): The extracted metadata dictionary
        
    Returns:
        pd.Series: Updated row with new metadata
        
    Special handling:
        - Preserves original title as 'meta_title' before updating
        - Formats DOI as full URL if not already formatted
        - Cross-references DOI and Link fields when one is missing
        - Tracks missing fields in 'metadata_missing' column
        - Quotes BibTeX content to handle special characters
    """
    # Update core metadata fields
    if metadata['Title']:
        row['meta_title'] = row['title']  # Preserve original title
        row['title'] = metadata['Title']
        
    if metadata['Venue']:
        row['venue'] = metadata['Venue']
        
    if metadata['Authors']:
        row['authors'] = metadata['Authors']
        
    if metadata['Abstract']:
        row['abstract'] = metadata['Abstract']
        
    if metadata['Keywords']:
        row['keywords'] = metadata['Keywords']
        
    if metadata['Pages']:
        row['pages'] = metadata['Pages']
        
    if metadata['Bibtex']:
        row['bibtex'] = '"' + metadata['Bibtex'] + '"'  # Quote for CSV safety
        
    if metadata['Source']:
        row['source'] = metadata['Source']
        
    if metadata['References']:
        row['references'] = metadata['References']
        
    if metadata['Publisher']:
        row['publisher'] = metadata['Publisher']
    
    # Handle DOI and Link fields with cross-referencing
    print(f"Processing DOI: {metadata['DOI']}")
    
    if metadata['DOI']:
        # Format DOI as full URL if not already formatted
        if "http" not in metadata['DOI']:
            row['doi'] = "https://doi.org/" + str(metadata['DOI'])
        else:
            row['doi'] = metadata['Link']  # Use link if DOI already formatted
            
    if metadata['Link']:
        row['link'] = metadata['Link']
    
    # Cross-reference missing DOI/Link fields
    if (metadata['DOI'] is None or metadata['DOI'] == "") and metadata['Link']:
        row['doi'] = row['link']
    elif (metadata['Link'] is None or metadata['Link'] == "") and metadata['DOI']:
        row['link'] = row['doi']
    
    # Track missing metadata fields for quality assessment
    for key in metadata.keys():
        if metadata[key] is None or metadata[key] == "":
            row['metadata_missing'] = str(row['metadata_missing']) + '; ' + str(key)
            
    return row
    

def main(sr_df, do_web_scraping=False, run=999, sr_name=""):
    """
    Main metadata extraction pipeline for systematic review datasets.
    
    This function orchestrates the complete metadata extraction process for a
    systematic review dataset. It processes each article row, attempts to find
    missing metadata from cached files or through web scraping, and updates
    the dataset with the extracted information.
    
    Args:
        sr_df (pd.DataFrame): The systematic review DataFrame to process
        do_web_scraping (bool): Whether to enable web scraping for missing metadata
        run (int): Run configuration (999=complete, 111=without link only, 0-5=partition)
        sr_name (str): Name of the systematic review project for error logging
        
    Returns:
        pd.DataFrame: Updated DataFrame with extracted metadata
        
    Processing pipeline:
        1. Initialize web scraper if enabled
        2. Load list of already extracted files (HTML and BibTeX)
        3. For each article row:
           a. Check if metadata extraction is needed
           b. Try extraction with existing DOI/link
           c. Try extraction without link (title-based search)
           d. Update dataset with extracted metadata
           e. Log any errors encountered
        4. Save error report and clean up resources
        
    Run configurations:
        - 999: Process all articles completely
        - 111: Process only articles without existing links
        - 0-5: Process only specific partition of articles
        
    Error handling:
        - Logs all processing errors to Excel file
        - Continues processing even if individual articles fail
        - Tracks both missing fields and complete failures
        
    Note:
        Creates error log file in Datasets/{sr_name}_erreurs_{run}.xlsx
        Web scraper is properly closed if initialized
    """
    # Initialize processing environment\n    completed_sr_project = sr_df.copy().reset_index()\n    articles_to_extract = len(pd.isna(completed_sr_project['meta_title']))\n    print(f\"{articles_to_extract} articles require metadata extraction\")\n    \n    # Define core metadata columns for validation\n    metadata_cols = ['title', 'venue', 'authors', 'abstract', 'keywords', 'references', 'doi', 'meta_title']\n\n    # Initialize web scraper if extraction is enabled\n    web_scraper = webScraping.WebScraper() if do_web_scraping else None\n    if web_scraper:\n        print(\"✅ Web scraper initialized for missing metadata extraction\")\n    else:\n        print(\"ℹ️ Web scraping disabled - using cached files only\")\n\n    # Configure processing partitions\n    parts = 6\n    partition_size = len(list(sr_df.iterrows())) // parts\n    errors_log = []  # Track processing errors\n\n    # Load cache of already extracted files\n    print(\"📁 Loading cached extraction files...\")\n    already_extracted_files = []\n    try:\n        already_extracted_html = os.listdir(f\"{EXTRACTED_PATH}/HTML extracted\")\n        already_extracted_bibtex = os.listdir(f\"{EXTRACTED_PATH}/Bibtex\")\n        already_extracted_files.extend(already_extracted_html)\n        already_extracted_files.extend(already_extracted_bibtex)\n        print(f\"Found {len(already_extracted_html)} HTML files and {len(already_extracted_bibtex)} BibTeX files in cache\")\n    except FileNotFoundError as e:\n        print(f\"⚠️ Cache directory not found: {e}\")"

    # =========================================================================\n    # MAIN PROCESSING LOOP\n    # =========================================================================\n    \n    print(f\"\\n🔄 Starting metadata extraction for {len(completed_sr_project)} articles...\")\n    print(f\"📊 Run configuration: {run} ({'Complete' if run == 999 else 'Without link only' if run == 111 else f'Partition {run}'})\")\n    \n    for idx, row in completed_sr_project.iterrows():\n        try:\n            print(f\"\\n--- Processing article {idx} ---\")\n            \n            # Apply run configuration filters\n            if run < parts and not (partition_size * run <= idx <= partition_size * (run + 1)):\n                continue  # Process only specific partition\n                \n            if run == 111 and not (idx == 152):  # Special case for testing\n                continue  # Process only articles without links\n\n            # Determine if metadata extraction is needed\n            url = str(row['doi'])\n            need_extraction = True  # Currently set to always extract\n            \n            # Alternative: Check specific missing fields\n            # need_extraction = any(pd.isna(row[col]) for col in metadata_cols)\n\n            if need_extraction:\n                metadata = None\n                print(f\"📖 Title: {row['title'][:80]}...\" if len(str(row['title'])) > 80 else f\"📖 Title: {row['title']}\")\n\n                # Extraction Strategy Selection\n                # Strategy 1: Extract using existing DOI/URL\n                if not metadata and not pd.isna(url) and str(url)[:4] == 'http':\n                    print(\"🔗 Attempting extraction with existing link\")\n                    metadata = extract_with_link(row, already_extracted_files, web_scraper)\n\n                # Strategy 2: Extract without direct link (title-based search)\n                if not metadata:\n                    print(\"🔍 Attempting extraction without direct link\")\n                    print(f\"Available info - Source: {row.get('source', 'N/A')}, Title: {row['title'][:50]}...\")\n                    metadata = extract_without_link(row, already_extracted_files, web_scraper)\n                \n                print(f\"📝 Extraction result: {'Success' if metadata else 'Failed'}\")\n                \n                # Update dataset with extracted metadata\n                if metadata:\n                    row = update_dataset(row, metadata)\n                    \n                    # Track missing fields for quality assessment\n                    for field_name in metadata.keys():\n                        if metadata[field_name] is None:\n                            errors_log.append((idx, field_name, 'missing_after_extraction'))\n                else:\n                    errors_log.append((idx, \"all_fields\", 'extraction_failed'))\n                    \n        except Exception as e:\n            error_msg = str(e)\n            error_trace = traceback.format_exc()\n            print(f\"❌ Error processing article {idx}: {error_msg}\")\n            print(f\"📋 Traceback: {error_trace}\")\n            errors_log.append((idx, error_msg, error_trace))\n            \n        # Update the main dataset with processed row\n        completed_sr_project.loc[idx] = row\n        \n        if idx % 10 == 0:  # Progress indicator every 10 articles\n            print(f\"📊 Progress: {idx}/{len(completed_sr_project)} articles processed\")"

    # =========================================================================\n    # CLEANUP AND REPORTING\n    # =========================================================================\n    \n    # Generate error report\n    if errors_log:\n        error_report_path = (\n            f\"{MAIN_PATH}/Datasets/{sr_name}_erreurs_{str(run)}.xlsx\" \n            if sr_name else f\"{MAIN_PATH}/Datasets/erreurs_{str(run)}.xlsx\"\n        )\n        \n        error_df = pd.DataFrame(errors_log, columns=['article_index', 'field_or_error', 'error_details'])\n        error_df.to_excel(error_report_path, index=False)\n        print(f\"📋 Error report saved to: {error_report_path}\")\n        print(f\"⚠️ Total errors logged: {len(errors_log)}\")\n    else:\n        print(\"✅ No errors encountered during processing\")\n    \n    # Clean up web scraper resources\n    if web_scraper:\n        web_scraper.close()\n        print(\"🧹 Web scraper closed successfully\")\n    \n    # Final summary\n    processed_articles = len([idx for idx, row in completed_sr_project.iterrows() if not pd.isna(row.get('meta_title', pd.NA))])\n    print(f\"\\n📊 Processing Summary:\")\n    print(f\"   • Articles processed: {len(completed_sr_project)}\")\n    print(f\"   • Metadata extracted: {processed_articles}\")\n    print(f\"   • Success rate: {(processed_articles/len(completed_sr_project)*100):.1f}%\")\n    print(f\"   • Errors encountered: {len(errors_log)}\")\n    \n    return completed_sr_project"
