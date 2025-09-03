from pathlib import Path
import pandas
from nltk import edit_distance
import os
import re
from Scripts.SRProject import standardize_title, code_source, IEEE
from Scripts.os_path import MAIN_PATH, EXTRACTED_PATH


def check_if_right_link(new_metadata, title, author=None, venue=None, year=None):
    """
    Enhanced title matching function for identifying incorrectly extracted articles.
    
    This is a more permissive version of the title matching function that includes
    additional criteria for detecting potential matches. It's used specifically
    for quality control to identify articles where the extracted title doesn't
    properly match the original title.
    
    Args:
        new_metadata (dict): Dictionary containing extracted metadata with 'Title' key
        title (str): Original article title to match against
        author (str, optional): Author information (not currently used)
        venue (str, optional): Venue information (not currently used)  
        year (str, optional): Publication year (not currently used)
        
    Returns:
        bool: True if titles are considered matching, False otherwise
        
    Enhanced matching criteria:
        1. Substring matching (bidirectional)
        2. Edit distance < 3 for close matches
        3. Edit distance < 10 AND word count difference < 2 for looser matches
        4. Overall length restrictions for validation
        
    Note:
        More permissive than the standard check_if_right_link function to catch
        edge cases where titles might be slightly different but refer to the same article.
    """
    if new_metadata is None or new_metadata['Title'] == "" or title == "" or new_metadata['Title'] is None:
        return False
    # TODO: enlever les deux points, les virgules, les tirets, / ou prendre distance? ou auteurs et année?
    tmp_title = standardize_title(title)
    tmp_meta_title = standardize_title(new_metadata['Title'])
    print(tmp_title)
    print(tmp_meta_title)
    if tmp_title in tmp_meta_title or tmp_meta_title in tmp_title or edit_distance(tmp_title, tmp_meta_title) < 3 or (edit_distance(tmp_title, tmp_meta_title) < 10 and abs(len(tmp_title.split()) - len(tmp_meta_title.split())) < 2):
        if abs(len(tmp_title.split()) - len(tmp_meta_title.split())) < 4 or abs(len(tmp_title) - len(tmp_meta_title)) < 10:
            return True
    return False
sr_project = 'CodeClone'
df = pandas.read_csv(Path(MAIN_PATH) / 'Datasets' / sr_project / f'{sr_project}.tsv', sep='\t', encoding='utf-8')
results = []

for idx, row in df.iterrows():
    tmp_dict = {'Title': row['title']}
    if not check_if_right_link(tmp_dict, row['meta_title']):
        results.append([idx, tmp_dict['Title'], row['meta_title']])
pandas.DataFrame(results, columns=['idx', 'title', 'meta_title']).to_excel(Path(MAIN_PATH) / 'Datasets' / sr_project / 'wrong-titles.xlsx')


def extract_title(filename):
    # Split on underscores from the right
    parts = filename.rsplit('_', 1)  # ['2025-06-04_a toolset for program understanding', '00']

    # Remove the date part from the beginning
    date_and_title = parts[0]  # '2025-06-04_a toolset for program understanding'
    parts = date_and_title.split('_', 1)
    date, title = parts[0], parts[1]

    return date, title

titles = [str(t[2]) for t in results]
# Paths to your folders
folders = [Path(EXTRACTED_PATH) / "Bibtex"]
# folders = [Path(EXTRACTED_PATH) / "Bibtex", Path(EXTRACTED_PATH) / "HTML extracted"]

# Compile regex pattern once
# Matches: 2025-xx-xx_TITLE_anything.ext
pattern = re.compile(r"2025-(\d{2})-(\d{2})_(.+)_(\d{2})\.(bib|html)")

print(len(titles))
print(results)
# # Loop through folders and files
# for folder in folders:
#     print(len(os.listdir(folder)))
#     for filename in os.listdir(folder):
#         for title in titles:
#             try:
#                 file = filename.lower()
#                 formated_name = title.lower()
#                 do_delete = False
#                 try:
#                     tmp_source = code_source[file[-7:-5]]
#                 except:
#                     try:
#                         tmp_source = code_source[file[-6:-4]]
#                     except:
#                         tmp_source = True
#                 if tmp_source == IEEE:
#                     if file[11:-8] == formated_name + "%2freferences#references":
#                         print(file)
#                         do_delete = True
#                     elif file[11:-8] == formated_name + "%2fkeywords#keywords":
#                         print(file)
#                         do_delete = True
#                     elif file[-3:] == 'bib' and file[11:-7] == formated_name:
#                         print(file)
#                         do_delete = True
#                 elif tmp_source is not None and (file[11:-8] == formated_name or file[11:-7] == formated_name):
#                     print(file)
#                     do_delete = True
#                 if do_delete:
#                     file_path = os.path.join(folder, filename)
#                     try:
#                         os.remove(file_path)
#                         print(f"Deleted: {file_path}")
#                     except Exception as e:
#                         print(f"Failed to delete {file_path}: {e}")
#             except:
#                 print("erreur")
#                 continue

