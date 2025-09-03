"""
CSV file comparison utility for systematic review processing verification.

This script compares two CSV files line by line and outputs the differences
to help verify the accuracy of the systematic review processing pipeline.
It's used to validate that the metadata curation process produces consistent
results by comparing reference datasets with replicated outputs.

Based on: https://stackoverflow.com/questions/38996033/python-compare-two-csv-files-and-print-out-differences

Process:
1. Reads two CSV files line by line
2. Identifies lines that exist in the second file but not the first
3. Writes the differences to a comparison output file

This is useful for quality assurance and debugging the metadata processing pipeline.
"""

# Compare two CSV files and identify differences
with open('Reference datasets/lc_replicated.csv', 'r') as t1, open('Reference datasets/lc_2.csv', 'r') as t2:
    fileone = t1.readlines()  # Read all lines from first file
    filetwo = t2.readlines()  # Read all lines from second file

# Write lines that appear in second file but not in first file
with open('Reference datasets/comparaison.csv', 'w') as outFile:
    for line in filetwo:
        if line not in fileone:
            outFile.write(line)
