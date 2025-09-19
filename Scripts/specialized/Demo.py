"""
Demo Systematic Literature Review Dataset Processing Script

Processes the Demo systematic review dataset on "Digital-twin-based testing for
cyber–physical systems: A systematic literature review" for metadata curation and
standardization.

Author: Guillaume Genois, 20248507
Dataset: Demo (Digital Twin Cyber-Physical Systems Testing)
Paper: https://www.sciencedirect.com/science/article/pii/S0950584922002543
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd
from typing import Dict, Optional


# Inclusion and exclusion criteria descriptions for the Demo systematic review
CRITERIA_DESCRIPTIONS = {
    'IC1': "At least one testing technique is described",
    'IC2': "The system under test must be a cyber–physical system",
    'IC3': "Testing is performed using a digital twin",
    'EC1': "The digital twin described does not use a live data coupling",
    'EC2': "The study describes future use of a digital twin",
    'EC3': "Non-english study",
    'EC4': "Not published in a journal or conference proceedings",
    'QC1': "Are the research questions of the examined study answered?",
    'QC2': "Is the study reproducible?",
}

# Mapping from decision text to criteria IDs
CRITERIA_ID_MAPPING = {
    'Testing context but no explained method': 'IC1',
    'Non testing context': 'IC1',
    'Model based verification': 'IC1',
    'DT not used for testing CPS': 'IC2',
    'No Physical Element': 'IC2',
    'Non Cyber-Physical System': 'IC2',
    'No Digital Twin': 'IC3',
    'Not focused on Digital Twin': 'IC3',
    'Future Works': 'EC2',
    'Non English Study': 'EC3',
    'Non paper': 'EC4',
    'Non Paper': 'EC4',
    'Does not fulfill RQs': 'QC1',
    '': None
}


class Demo(SRProject):
    """
    Demo Systematic Literature Review Dataset Processor

    Processes the systematic review on "Digital-twin-based testing for cyber–physical
    systems: A systematic literature review" for LLM training dataset creation.

    Dataset Characteristics:
        - Paper: https://www.sciencedirect.com/science/article/pii/S0950584922002543
        - Total Articles: 454
        - Title/Abstract Included: 147
        - Full-text Included: 26
        - Inclusion Rate: 32% (title/abstract) / 6% (full-text)
        - Conflict Data: No
        - Criteria Labeled: Yes (3 inclusion + 4 exclusion + 2 quality criteria)
        - Abstract Text: No
        - Review Phases: Duplicate removal → Title/Abstract screening → Full-text screening

    Processing Details:
        - Loads data from Demo-source.xlsx "export" sheet
        - Handles multi-phase screening (duplicates, title/abstract, full-text)
        - Maps exclusion criteria to standardized descriptions
        - Processes both screened and final decisions

    Known Data Gaps:
        - Missing abstract, keywords, references, and BibTeX data
        - Limited author information formatting
        - Some incomplete venue and DOI information
    """

    def __init__(self):
        """
        Initialize Demo systematic review dataset processor.

        Loads and processes data from the Demo source Excel file, handling multi-phase
        screening including duplicate removal, title/abstract screening, and full-text review.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/Demo/Demo-source.xlsx"

        try:
            # Load data from Excel source file
            with open(self.path, 'rb') as f:
                # Export sheet contains all 458 articles (including duplicates)
                sheet_all = pd.read_excel(f, sheet_name="export")
                print(f"Loaded {len(sheet_all)} articles from Demo source (including duplicates)")

            # Multi-phase screening process
            sheet_without_duplicates = sheet_all.loc[sheet_all['Duplicate'] == 'Accepted']  # 454 articles
            sheet_screen_title_and_abstract = sheet_without_duplicates.loc[
                (sheet_without_duplicates['Title + Abstract'] == 'Accepted') |
                (sheet_without_duplicates['Title + Abstract'] == 'Accepted - Dream Paper')
            ]  # 147 articles
            sheet_screen_full_text = sheet_screen_title_and_abstract.loc[
                sheet_screen_title_and_abstract['Full Text'] == 'Accepted'
            ]  # 26 articles

            print(f"After duplicate removal: {len(sheet_without_duplicates)} articles")
            print(f"After title/abstract screening: {len(sheet_screen_title_and_abstract)} articles")
            print(f"After full-text screening: {len(sheet_screen_full_text)} articles")

            # Map source columns to standardized schema
            self._map_columns_to_schema(sheet_without_duplicates)

            # Set dataset-specific metadata
            self._set_dataset_metadata()

            # Process screening decisions
            self._process_screening_decisions(
                sheet_screen_title_and_abstract,
                sheet_without_duplicates,
                sheet_screen_full_text
            )

            print(f"Demo dataset initialized with {len(self.df)} articles")

        except Exception as e:
            print(f"Error initializing Demo dataset: {e}")
            raise

    def _map_columns_to_schema(self, sheet_without_duplicates: pd.DataFrame) -> None:
        """
        Map source Excel columns to standardized dataset schema.

        Args:
            sheet_without_duplicates (pd.DataFrame): Source data after duplicate removal
        """
        # Map available columns to standardized schema
        self.df['title'] = sheet_without_duplicates["Title"]
        self.df["authors"] = sheet_without_duplicates["author"]
        self.df['venue'] = sheet_without_duplicates["journal"]
        self.df["doi"] = sheet_without_duplicates["doi"]
        self.df["year"] = pd.to_numeric(sheet_without_duplicates["year"], errors='coerce').astype("Int64")
        self.df["link"] = sheet_without_duplicates["url"]
        self.df["pages"] = sheet_without_duplicates["pages"]
        self.df["publisher"] = sheet_without_duplicates["publisher"]

        # Derive source from publisher information
        self.df["source"] = self.df['publisher'].apply(self._find_source)

        # Format DOI URLs
        self.df["doi"] = self.df["doi"].astype(str)
        mask = (self.df['doi'] != '') & (self.df['doi'] != 'nan')
        self.df.loc[mask, 'doi'] = 'https://doi.org/' + self.df.loc[mask, 'doi']

        # Convert link column to string
        self.df["link"] = self.df["link"].astype(str)

        # Note: This dataset lacks abstract, keywords, references, and BibTeX data
        # These fields remain empty and may be populated during metadata extraction

    def _set_dataset_metadata(self) -> None:
        """
        Set dataset-specific metadata and configuration.
        """
        self.df['project'] = "Demo"
        self.df['mode'] = 'new_screen'  # All articles from initial database search
        self.df["reviewer_count"] = 2  # Two reviewers per article
        self.export_path = f"{MAIN_PATH}/Datasets/Demo/Demo.tsv"

    def _process_screening_decisions(self, sheet_screen_title_and_abstract: pd.DataFrame,
                                   sheet_without_duplicates: pd.DataFrame,
                                   sheet_screen_full_text: pd.DataFrame) -> None:
        """
        Process multi-phase screening decisions: title/abstract and full-text screening.

        Args:
            sheet_screen_title_and_abstract: DataFrame with title/abstract accepted articles
            sheet_without_duplicates: DataFrame with all articles (criteria source)
            sheet_screen_full_text: DataFrame with full-text accepted articles
        """
        # Process title/abstract screening decisions
        self.find_decision_on_articles(
            sheet_screen_title_and_abstract,
            sheet_without_duplicates,
            'Title + Abstract'
        )

        # Process full-text screening decisions
        self.find_decision_on_articles(
            sheet_screen_full_text,
            sheet_screen_title_and_abstract,
            'Full Text',
            is_final=True
        )

    def find_decision_on_articles(self, sheet_included: pd.DataFrame,
                                sheet_criteria: pd.DataFrame,
                                criteria_column: str,
                                is_final: bool = False) -> None:
        """
        Process article screening decisions by comparing titles across sheets.

        Args:
            sheet_included (pd.DataFrame): Sheet containing articles that passed this screening phase
            sheet_criteria (pd.DataFrame): Sheet containing all articles with exclusion criteria
            criteria_column (str): Column name containing exclusion criteria information
            is_final (bool): Whether this is final decision processing (vs. screened decision)

        Note:
            Demo dataset uses a two-phase process:
            1. Title/Abstract screening: 454 → 147 articles
            2. Full-text screening: 147 → 26 articles
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        criteria = 'exclusion_criteria'  # Both phases use exclusion criteria

        for article_title in self.df['title'].values:
            if pd.isna(article_title) or article_title == "":
                continue

            if article_title in sheet_included["Title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"

                # Extract exclusion criteria if available
                if article_title in sheet_criteria["Title"].values:
                    try:
                        exclusion_criteria = sheet_criteria.loc[
                            sheet_criteria["Title"] == article_title, criteria_column
                        ].values[0]

                        if not pd.isna(exclusion_criteria) and 'Rejected' in str(exclusion_criteria):
                            # Extract criteria after 'Rejected - ' prefix
                            criteria_text = str(exclusion_criteria)[len('Rejected - '):]
                            criteria_id = CRITERIA_ID_MAPPING.get(criteria_text)

                            if criteria_id and criteria_id in CRITERIA_DESCRIPTIONS:
                                # Determine if it's inclusion or exclusion criteria
                                criteria_type = 'inclusion_criteria' if criteria_id.startswith('IC') else 'exclusion_criteria'
                                full_criteria = f"{criteria_id}: {CRITERIA_DESCRIPTIONS[criteria_id]}"
                                self.df.loc[self.df['title'] == article_title, criteria_type] = full_criteria

                    except (IndexError, KeyError) as e:
                        # Skip articles with missing or malformed criteria
                        continue

    def _find_source(self, publisher: str) -> str:
        """
        Determine the academic source from publisher information.

        Args:
            publisher (str): Publisher name from source data

        Returns:
            str: Standardized source name or original publisher if not recognized
        """
        if pd.isna(publisher):
            return publisher

        publisher_str = str(publisher).upper()

        # Map publishers to standardized source names
        if any(keyword in publisher_str for keyword in ['ACM', 'ASSOCIATION FOR COMPUTING MACHINERY', 'ICST']):
            return 'ACM'
        elif any(keyword in publisher_str for keyword in ['ELSEVIER', 'ACADEMIC PRESS']):
            return 'ScienceDirect'
        elif any(keyword in publisher_str for keyword in ['IEEE', 'INSTITUTE OF ELECTRICAL AND ELECTRONICS ENGINEERS']):
            return 'IEEE'
        elif 'SPRINGER' in publisher_str:
            return 'SpringerLink'
        else:
            return publisher


if __name__ == '__main__':
    """
    Main execution block for testing Demo dataset processing.
    """
    try:
        sr_project = Demo()
        print(f"\nDemo Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with years: {sr_project.df['year'].notna().sum()}")
        print(f"Articles with DOIs: {sr_project.df['doi'].notna().sum()}")
        print(f"Export path: {sr_project.export_path}")

        # Display screening decision counts
        if 'screened_decision' in sr_project.df.columns:
            print(f"\nTitle/Abstract screening decisions:")
            print(sr_project.df['screened_decision'].value_counts())

        if 'final_decision' in sr_project.df.columns:
            print(f"\nFull-text screening decisions:")
            print(sr_project.df['final_decision'].value_counts())

        # Export to TSV file
        sr_project.df.to_csv(sr_project.export_path, sep='\t', index=False, encoding='utf-8')
        print(f"\nDataset exported to: {sr_project.export_path}")

    except Exception as e:
        print(f"Error running Demo processing: {e}")
