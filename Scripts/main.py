# -*- coding: utf-8 -*-
"""
Systematic Review Metadata Curation Pipeline

This module provides the main processing pipeline for systematic literature review
datasets. It handles the complete workflow from raw source data to cleaned,
standardized datasets ready for machine learning applications.

Key Features:
- Automated metadata extraction from multiple academic sources
- Web scraping integration for missing metadata retrieval
- Data cleaning and standardization
- Quality assessment and reporting
- Support for 15+ systematic review datasets

Author: Guillaume Genois, 20248507
Purpose: Metadata curation for LLM-assisted systematic literature reviews
"""

import os
# import cudf.pandas
# cudf.pandas.install()
import sys
import argparse

from Scripts.specialized.Demo import Demo
from Scripts.specialized.IFT3710 import IFT3710
from Scripts.core.os_path import MAIN_PATH

# sys.stdout = open(os.devnull, 'w')
sys.path.extend([MAIN_PATH])

import chardet
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from Scripts.extraction import findMissingMetadata
from Scripts.datasets.ArchiML import ArchiML
from Scripts.datasets.Behave import Behave
from Scripts.datasets.CodeClone import CodeClone
from Scripts.datasets.CodeCompr import CodeCompr
from Scripts.datasets.DTCPS import DTCPS
from Scripts.datasets.ESM_2 import ESM_2
from Scripts.datasets.ESPLE import ESPLE
from Scripts.datasets.GameSE import GameSE
from Scripts.specialized.GameSE_abstract import GameSE_abstract
from Scripts.specialized.GameSE_title import GameSE_title
from Scripts.datasets.ModelGuidance import ModelGuidance
from Scripts.datasets.ModelingAssist import ModelingAssist
from Scripts.datasets.OODP import OODP
from Scripts.datasets.SecSelfAdapt import SecSelfAdapt
from Scripts.datasets.SmellReprod import SmellReprod
from Scripts.datasets.TestNN import TestNN
from Scripts.datasets.TrustSE import TrustSE
from Scripts.core.SRProject import *

# Author : Guillaume Genois, 20248507
# This script is for importing and uniformising data from multiple datasets of SR.


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


def printEncoding(file_path):
    """
    Detects and prints the character encoding of a file.
    
    This utility function reads a file in binary mode and uses the chardet library
    to automatically detect its character encoding. Useful for debugging encoding
    issues with input data files that may contain special characters.
    
    Args:
        file_path (str): Path to the file whose encoding should be detected
        
    Returns:
        None: Prints the detected encoding information to console
    """
    with open(file_path, 'rb') as file:
        print(chardet.detect(file.read()))


def postProcessing(sr_project):
    """
    Performs quality assurance checks on the processed systematic review data.
    
    This function analyzes the exported TSV file to provide statistics about:
    - Missing/empty values for each metadata field
    - Presence of undesirable Unicode characters
    - Overall dataset completeness metrics
    
    The function helps identify data quality issues and provides insights into
    the success rate of the metadata extraction process.
    
    Args:
        sr_project (SRProject): The systematic review project object containing
                               export path and dataframe information
                               
    Returns:
        None: Prints quality assessment statistics to console
        
    Side Effects:
        - Reads the exported TSV file from sr_project.export_path
        - Prints various statistics about data completeness
    """
    # Initialize counters for missing values in each field
    empty_counts = {"key": 0, "project": 0, "title": 0, "abstract": 0, "keywords": 0, "authors": 0, "venue": 0, "doi": 0,
       "references": 0, "bibtex": 0, "screened_decision": 0, "final_decision": 0, "mode": 0,
       "inclusion_criteria": 0, "exclusion_criteria": 0, "reviewer_count": 0}
    
    # Pattern to detect problematic Unicode characters that may cause issues
    undesirable_pattern = (
        r'[\u0000-\u001F\u007F\u0080-\u009F\u200B\u200C\u200D\u200E\u200F'
        r'\u202A\u202B\u202C\u202D\u202E\uFEFF\uFFFD\0xE2\0x80\0x99]'
    )

    # Read the exported file to analyze its contents
    file = pd.read_csv(sr_project.export_path, delimiter="\t")
    
    # Count missing values and check for undesirable characters
    for line in file.iterrows():
        row = line[1]
        for key in empty_counts:
            if pd.isna(row[key]):
                empty_counts[key] += 1
            elif re.search(undesirable_pattern, str(row[key])):
                continue
                print("Error:", line[0], row[key])
    
    # Output quality assessment statistics
    print(sr_project.df['project'].values[0])
    print("Number of blanks/NaN:", empty_counts)
    print("Number of articles:", len(file))
    print("Number of missing articles:", file['meta_title'].isna().sum())

    # TODO: check good number of lines exported
    # TODO: check for any unknown characters
    # TODO: check for right encoding
    # TODO: check for NaN or missing values


def cleanDataFrame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes data in a pandas DataFrame for export.
    
    This function performs several cleaning operations to ensure data quality
    and consistency:
    - Replaces problematic Unicode characters with standard equivalents
    - Removes copyright symbols and other unwanted characters
    - Standardizes delimiter usage in multi-value fields
    - Strips whitespace from string values
    - Handles NaN values and empty strings consistently
    - Removes illegal characters that could cause Excel/CSV issues
    
    Args:
        df (pd.DataFrame): The DataFrame to be cleaned
        
    Returns:
        pd.DataFrame: A cleaned copy of the input DataFrame
        
    Note:
        The function uses openpyxl's ILLEGAL_CHARACTERS_RE to ensure
        compatibility with Excel exports.
    """
    # Replace problematic Unicode dash with standard ASCII dash
    new_df = df.replace("–", "-")
    
    # Remove copyright symbols that may cause encoding issues
    new_df = new_df.replace("©", '')
    
    # Standardize double semicolons to single semicolons
    new_df = new_df.replace(";;", ';')
    
    # Strip whitespace from all string values
    new_df = new_df.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Replace string "nan" with empty string
    new_df = new_df.replace("nan", '')
    
    # Fill actual NaN values with empty strings
    new_df = new_df.fillna('')
    
    # Remove characters that are illegal in Excel/OpenPyXL
    new_df = new_df.map(lambda x: ILLEGAL_CHARACTERS_RE.sub(r'',x) if isinstance(x, str) else x)
    
    return new_df


def ExportToCSV(sr_project):
    """
    Exports the systematic review project data to a TSV file.
    
    This function takes the processed DataFrame from a systematic review project
    and exports it to a tab-separated values (TSV) file. The function:
    - Removes internal tracking columns (index, key)
    - Uses tab separation for better handling of text with commas
    - Sets UTF-8 encoding to preserve special characters
    - Uses the row index as the primary key column
    
    Args:
        sr_project (SRProject): The systematic review project object containing
                               the processed DataFrame and export path
                               
    Returns:
        None: Writes the data to the file specified in sr_project.export_path
        
    Side Effects:
        - Creates/overwrites the TSV file at sr_project.export_path
        - File format: TSV with UTF-8 encoding and row index as 'key' column
    """
    final_data_frame = sr_project.df

    # Remove internal columns that shouldn't be in the final export
    final_data_frame = final_data_frame.drop(columns=["index",'key'])
    
    # Export to TSV with UTF-8 encoding and row index as key
    final_data_frame.to_csv(sr_project.export_path, sep="\t", index_label="key", encoding='utf-8')


def pre_process_sr_project(sr_project):
    """
    Preprocesses the systematic review project data to handle duplicate titles.
    
    This function ensures that all titles in the dataset are unique by appending
    a numeric suffix to duplicate titles. This is important for:
    - Preventing data loss during processing
    - Ensuring each article can be uniquely identified
    - Avoiding conflicts in downstream processing steps
    
    Args:
        sr_project (SRProject): The systematic review project object whose
                               DataFrame will be modified
                               
    Returns:
        None: Modifies sr_project.df in place
        
    Side Effects:
        - Modifies the 'title' column in sr_project.df
        - Prints duplicate titles as they are found
        - Appends numeric suffixes to duplicate titles (e.g., "Title 2", "Title 3")
    """
    title_counts = {}

    def make_unique(title):
        """
        Inner function to generate unique titles by adding numeric suffixes.
        
        Args:
            title (str): The original title
            
        Returns:
            str: Unique title (original or with numeric suffix)
        """
        if title in title_counts:
            title_counts[title] += 1
            print(title)  # Alert user to duplicate
            return f"{title} {title_counts[title]}"
        else:
            title_counts[title] = 1
            return title

    # Apply uniqueness transformation to all titles
    sr_project.df["title"] = sr_project.df["title"].apply(make_unique)


def read_sr_project(arg):
    """
    Reads a previously processed systematic review project from its TSV file.
    
    This utility function loads a systematic review dataset that has already
    been processed and exported. Used primarily for incremental processing
    or when resuming work on a partially completed dataset.
    
    Args:
        arg (str): The name of the systematic review project/dataset
        
    Returns:
        pd.DataFrame: The loaded systematic review data
        
    Note:
        Assumes the TSV file follows the standard naming convention:
        {MAIN_PATH}/Datasets/{project_name}/{project_name}.tsv
    """
    return pd.read_csv(f"{MAIN_PATH}/Datasets/{arg}/{arg}.tsv", delimiter="\t")


def main(args=None, do_extraction=True, do_filter=True):
    """
    Main processing function for systematic review datasets.

    This function orchestrates the complete processing pipeline for one or more
    systematic review projects. It handles:
    - Dataset initialization and loading
    - Preprocessing (duplicate handling, data cleaning)
    - Metadata extraction (optional web scraping)
    - Data cleaning and standardization
    - Export to TSV format
    - Quality assessment reporting

    The function processes multiple datasets sequentially, applying the same
    standardized pipeline to each one.

    Args:
        args (list, optional): List of dataset names to process. If None or empty,
                              defaults to ['CodeCompr', 'ArchiML', 'ModelingAssist', 'CodeClone']
        do_extraction (bool, optional): Whether to perform web extraction for missing metadata.
                                       Defaults to True.
        do_filter (bool, optional): Whether to filter dataset to only process unprocessed articles.
                                   Defaults to True.

    Returns:
        None: Processes datasets and exports results to files

    Side Effects:
        - Creates/updates TSV files for each processed dataset
        - Creates Excel files with preprocessing data
        - Prints processing statistics and quality metrics
        - May perform web scraping if extraction is enabled
    """
    # Set default datasets to process if none provided
    if args is None or not len(args) > 0:
        args = ['CodeCompr', "ArchiML", 'ModelingAssist', 'CodeClone']
        # args = ['CodeCompr']  # Alternative single dataset for testing
    sr_project = None

    for arg in args:
        if arg == "ArchiML":  # missing
            sr_project = ArchiML()
        elif arg == "Behave":  # complete
            sr_project = Behave()
        elif arg == "CodeClone":  # missing
            sr_project = CodeClone()
        elif arg == "CodeCompr":  # missing
            sr_project = CodeCompr()
        elif arg == "DTCPS":  # complete
            sr_project = DTCPS()
        elif arg == "ESM_2":  # complete
            sr_project = ESM_2()
        elif arg == "ESPLE":  # complete
            sr_project = ESPLE()
        elif arg == "GameSE":  # complete
            sr_project = GameSE()
        elif arg == "GameSE_title":  # complete
            sr_project = GameSE_title()
        elif arg == "GameSE_abstract":  # complete
            sr_project = GameSE_abstract()
        elif arg == "ModelGuidance":  # 914 missing
            sr_project = ModelGuidance()
        elif arg == "ModelingAssist":  # 749 missing
            sr_project = ModelingAssist()
        elif arg == "OODP":  # 91 missing
            sr_project = OODP()
        elif arg == "SecSelfAdapt":  # complete
            sr_project = SecSelfAdapt()
        elif arg == "SmellReprod":  # complete
            sr_project = SmellReprod()
        elif arg == "TestNN":  # complete
            sr_project = TestNN()
        elif arg == "TrustSE":  # complete
            sr_project = TrustSE()
        elif arg == "Demo":
            sr_project = Demo()
        elif arg == "IFT3710":
            sr_project = IFT3710()
        else:
            print("Not a valid argument")
            continue

        pre_process_sr_project(sr_project)
        sr_project.df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}_pre-extract.xlsx")

        # Use the function parameters instead of hardcoded values
        if do_filter:
            sr_compiled_project = read_sr_project(arg)
            # Keep only the rows that still need processing (meta_title is null/empty)
            unprocessed = sr_compiled_project[sr_compiled_project['meta_title'].isnull()]
            # Filter the original dataframe to only keep those rows
            titles_to_process = unprocessed['title']
            sr_project.df = sr_project.df[sr_project.df['title'].isin(titles_to_process)]
            sr_project.export_path = f"{MAIN_PATH}/Datasets/{arg}/{arg}_unprocessed.xlsx"

        # printEncoding(sr_project.path)  # to make sure we use the right encoding if necessary
        completed_df = findMissingMetadata.main(sr_project.df, do_extraction, 999, arg)
        cleaned_df = cleanDataFrame(completed_df)
        sr_project.df = cleaned_df

        ExportToCSV(sr_project)
        # sys.stdout = sys.__stdout__127
        postProcessing(sr_project)

        # cleaned_df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}.xlsx")
        # sr_project.df.to_excel(f"{MAIN_PATH}/Datasets/{arg}/{arg}_tmp.xlsx")


def parse_arguments():
    """
    Parse command-line arguments for the systematic review processing pipeline.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing:
            - datasets: List of dataset names to process
            - no_extraction: Flag to disable web extraction
            - no_filter: Flag to disable filtering for unprocessed articles
    """
    parser = argparse.ArgumentParser(
        description="Systematic Literature Review Metadata Curation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py Demo                           # Process Demo with extraction and filtering
  python main.py Demo --no-extraction          # Process Demo without web extraction
  python main.py Demo --no-filter              # Process Demo without filtering
  python main.py CodeClone ArchiML             # Process multiple datasets
  python main.py Demo --no-extraction --no-filter  # Process with both options disabled
        """
    )

    parser.add_argument(
        'datasets',
        nargs='*',
        default=['CodeCompr', 'ArchiML', 'ModelingAssist', 'CodeClone'],
        help='Dataset names to process (default: %(default)s)'
    )

    parser.add_argument(
        '--no-extraction',
        action='store_true',
        help='Disable web extraction for missing metadata (default: extraction enabled)'
    )

    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Disable filtering to only process unprocessed articles (default: filtering enabled)'
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Convert negative flags to positive parameters
    do_extraction = not args.no_extraction
    do_filter = not args.no_filter

    main(args.datasets, do_extraction=do_extraction, do_filter=do_filter)
