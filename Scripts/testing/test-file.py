from pathlib import Path
import pandas as pd
from Scripts.os_path import MAIN_PATH, DOWNLOAD_PATH

# Load the Excel file
source_path = Path(DOWNLOAD_PATH) / 'datasets'
file = source_path / 'CodeClone-source.xlsx'
df = pd.read_excel(file, sheet_name='initial-articles')  # Change this to your filename

# Filter where 'number' is 2, 3, or 4
df_filtered = df[df["number"].isin([2, 3, 4])]

# Prepare list to store matches
matches = []

# Iterate over unique values in 'left of comma'
for cropped_title in df_filtered["left of comma"].unique():
    # Find all rows that match this cropped title
    group = df_filtered[df_filtered["left of comma"] == cropped_title]

    # Identify the full titles
    full_titles = group["Article title"].unique()

    # Only proceed if there's a mismatch in full vs cropped
    for title in full_titles:
        if title != cropped_title:
            matches.append({
                "cropped_title": cropped_title,
                "status": "duplicate",
                "full_title": title
            })

# Convert to DataFrame
df_matches = pd.DataFrame(matches)

# Save to Excel
df_matches.to_excel(source_path / "matched_duplicates.xlsx", index=False)

print("✅ Done! File saved as matched_duplicates.xlsx")
