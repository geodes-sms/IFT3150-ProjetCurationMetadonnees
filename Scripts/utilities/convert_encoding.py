"""
Character encoding conversion utility for systematic review metadata files.

This script converts text files from various character encodings to clean ASCII
format using the unidecode library. It's specifically designed to handle the
articles_extract_manually.tsv file which may contain special characters from
different academic sources and international publications.

The conversion process:
1. Reads the file with UTF-8 encoding (ignoring errors)
2. Converts all Unicode characters to ASCII equivalents
3. Saves the cleaned version to a temporary file

This ensures compatibility across different systems and prevents encoding-related
issues during data processing.
"""

from pathlib import Path

import pandas
from unidecode import unidecode

from Scripts.os_path import MAIN_PATH

# Read the manually extracted articles file with UTF-8 encoding
with open(Path(MAIN_PATH) / 'Scripts' / 'data' / 'articles_extract_manually.tsv', 'r', encoding='utf-8', errors='ignore') as file:
    content = file.read()

# Convert all Unicode characters to ASCII equivalents
content = unidecode(content)

# Save the cleaned content to a temporary file
with open(Path(MAIN_PATH) / 'Scripts' / 'articles_extract_manually-tmp.tsv', 'w') as file:
    file.write(content)
# df = pandas.read_csv(Path(MAIN_PATH) / 'Scripts' / 'data' / 'articles_extract_manually.tsv', sep='\t', encoding='windows-1252')
# df.to_csv(Path(MAIN_PATH) / 'Scripts' / 'articles_extract_manually-tmp.tsv', sep='\t', encoding='utf-8')