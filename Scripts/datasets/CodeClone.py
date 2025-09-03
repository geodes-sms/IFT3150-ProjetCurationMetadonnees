"""
CodeClone Systematic Literature Review Dataset Processing Script

Processes the CodeClone systematic review dataset on "A systematic literature review 
on source code similarity measurement and clone detection: Techniques, applications, 
and challenges" for metadata curation and standardization.

Author: Guillaume Genois, 20248507
Dataset: CodeClone (Code Clone Detection and Management)
Paper: https://doi.org/10.1016/j.jss.2023.111796
"""

from Scripts.core.SRProject import SRProject
from Scripts.core.os_path import MAIN_PATH
import pandas as pd


# Exclusion criteria descriptions as defined in the original paper
EXCLUSION_CRITERIA_DESCRIPTIONS = {
    'EC1': 'The articles repeated in citation databases were removed. We kept only one version of each duplicated article.',
    'EC2': 'Articles whose main text was written in any language other than English or only their abstract and keywords were in English were eliminated.',
    'EC3': 'Articles whose total text was less than three pages were removed. After reviewing them, we removed these articles and ensured they did not contain significant contributions. If there are good clues in these articles to find other suitable topics and articles, we consider these clues while applying the inclusion criteria and snowballing phases.',
    'EC4': 'Articles that did not directly discuss a source code similarity measurement approach in their abstract were removed. For example, some papers have discussed binary code similarity.',
    'EC5': 'The papers that had not proposed an automated approach for source code similarity measurement were removed. We excluded these articles since the similarity measurement technique was necessary when classifying methods.',
    'EC6': 'Theses, books, journal covers and metadata, secondary, tertiary, empirical, and case studies were removed.',
    'YES': '',
}

# Special characters found in CodeClone source data requiring encoding fixes:
# "Â" -> ""
# "â€™" -> "'"
# "â€œ" -> '"'
# "â€"" -> '-'
# "â€" -> '"'

class CodeClone(SRProject):
    """
    CodeClone Systematic Literature Review Dataset Processor
    
    Processes the systematic review on "A systematic literature review on source code 
    similarity measurement and clone detection: Techniques, applications, and challenges" 
    for LLM training dataset creation.
    
    Dataset Characteristics:
        - Paper: https://doi.org/10.1016/j.jss.2023.111796
        - Total Articles: 10,454
        - Initially Selected: 573
        - Finally Selected: 301
        - Inclusion Rate: ~5.5% (initial) / ~2.9% (final)
        - Conflict Data: No
        - Criteria Labeled: Yes (6 exclusion criteria: EC1-EC6)
        - Abstract Text: No
        - Review Phases: Initial screening → Full-text review → Final selection
        
    Processing Details:
        - Loads data from CodeClone-source.xlsx with multiple sheets
        - Maps exclusion criteria EC1-EC6 to original paper descriptions
        - Handles two-phase screening process (initial and final)
        - Source data contains UTF-8 encoding artifacts
        
    Known Data Gaps:
        - Missing abstract, keywords, authors, DOI, references, and BibTeX data
        - Some articles have incomplete title and venue information
        - Snowballing articles not yet integrated
    """

    def __init__(self):
        """
        Initialize CodeClone systematic review dataset processor.
        
        Loads and processes data from the CodeClone source Excel file with multiple
        sheets representing different screening phases.
        """
        super().__init__()
        self.path = f"{MAIN_PATH}/Datasets/CodeClone/CodeClone-source.xlsx"
        
        try:
            # Load data from multiple Excel sheets representing screening phases
            sheet_initial_articles = pd.read_excel(self.path, sheet_name="initial-articles")  # 10454 rows
            sheet_initial_selection = pd.read_excel(self.path, sheet_name="initial-selection")  # 573 rows
            sheet_final_selected = pd.read_excel(self.path, sheet_name="final-selected")  # 301 rows
            
            print(f"Loaded CodeClone data: {len(sheet_initial_articles)} initial, "
                  f"{len(sheet_initial_selection)} initially selected, "
                  f"{len(sheet_final_selected)} finally selected")
            
            # Map source columns to standardized schema
            self._map_columns_to_schema(sheet_initial_articles)
            
            # Set dataset-specific metadata
            self._set_dataset_metadata()
            
            # Process screening decisions
            self._process_screening_decisions(sheet_initial_selection, sheet_initial_articles, sheet_final_selected)
            
            print(f"CodeClone dataset initialized with {len(self.df)} articles")
            
        except Exception as e:
            print(f"Error initializing CodeClone dataset: {e}")
            raise
    
    def _map_columns_to_schema(self, sheet_initial_articles):
        """
        Map source Excel columns to standardized dataset schema.
        
        Args:
            sheet_initial_articles: DataFrame containing all initial articles data
        """
        # Map available columns to standardized schema
        self.df['title'] = sheet_initial_articles["Article title"]
        self.df['venue'] = sheet_initial_articles["Venue name"]
        self.df['source'] = sheet_initial_articles["Publisher"]
        self.df['exclusion_criteria'] = sheet_initial_articles["Applied exclusion criteria"]
        
        # Note: This dataset lacks abstract, keywords, authors, DOI, year, references, and BibTeX data
        # These fields remain empty and may be populated during metadata extraction
    
    def _set_dataset_metadata(self):
        """
        Set dataset-specific metadata and configuration.
        """
        self.df['project'] = "CodeClone"
        self.df['mode'] = "new_screen"  # All articles from initial database search
        self.df['reviewer_count'] = 1
        self.df["reviewer_count"] = self.df["reviewer_count"].astype(int)
        self.export_path = f"{MAIN_PATH}/Datasets/CodeClone/CodeClone.tsv"
    
    def _process_screening_decisions(self, sheet_initial_selection, sheet_initial_articles, sheet_final_selected):
        """
        Process two-phase screening decisions: initial selection and final selection.
        
        Args:
            sheet_initial_selection: DataFrame with initially selected articles (573)
            sheet_initial_articles: DataFrame with all initial articles with criteria (10,454)
            sheet_final_selected: DataFrame with finally selected articles (301)
        """
        # Process initial screening decisions (preserving original logic)
        self.find_decision_on_articles(sheet_initial_selection, sheet_initial_articles)
        # Process final screening decisions (preserving original logic)
        self.find_decision_on_articles(sheet_final_selected, sheet_initial_selection, True)

    # def find_decision_on_articles(self, sheet_initial_articles, sheet_initial_selection, sheet_final_selected):
    #     # Note: No conflict in this SR, so no ConflictIncluded and ConflictExcluded
    #     # df1[ df1.index.isin(sample1.index) & df1.index.isin(sample2.index) ]
    #     for article_title in sheet_initial_articles["Article title"]:
    #         if article_title == "": continue   # TODO: change how to check for matching articles, use whole row instead
    #         if article_title in sheet_final_selected["Article title"].values:
    #             self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Included"
    #         else:
    #             self.df.loc[self.df['title'] == article_title, 'final_decision'] = "Excluded"
    #         if article_title in sheet_initial_selection["Article title"].values:
    #             self.df.loc[self.df['title'] == article_title, 'screened_decision'] = "Included"
    #             self.df.loc[self.df['title'] == article_title, 'inclusion_criteria'] = sheet_initial_selection.loc[self.df['title'] == article_title, "Inclusion criteria"]
    #         else:
    #             self.df.loc[self.df["title"] == article_title, 'screened_decision'] = "Excluded"

    def find_decision_on_articles(self, sheet_included, sheet_criteria, is_final=False):
        """
        Process article screening decisions by comparing titles across sheets.
        
        Args:
            sheet_included: DataFrame containing articles that passed this screening phase
            sheet_criteria: DataFrame containing all articles with exclusion criteria
            is_final: Whether this is final decision processing (vs. screened decision)
            
        Note:
            CodeClone uses a two-phase process:
            1. Initial screening: 10,454 → 573 articles
            2. Final selection: 573 → 301 articles
        """
        decision = 'screened_decision' if not is_final else 'final_decision'
        criteria = 'exclusion_criteria' if not is_final else 'inclusion_criteria'
        header_criteria = 'Applied exclusion criteria' if not is_final else 'Inclusion criteria'
        
        for article_title in self.df['title'].values:
            if article_title in sheet_included["Article title"].values:
                self.df.loc[self.df['title'] == article_title, decision] = "Included"
            else:
                self.df.loc[self.df['title'] == article_title, decision] = "Excluded"
                if article_title in sheet_criteria["Article title"].values:
                    exclusion_criteria = str.upper(sheet_criteria.loc[sheet_criteria["Article title"] == article_title, [header_criteria]].values[0][0])
                    if not pd.isna(exclusion_criteria) and exclusion_criteria not in ['SELECTED', 'NO']:
                        self.df.loc[self.df['title'] == article_title, criteria] = exclusion_criteria + ": " + EXCLUSION_CRITERIA_DESCRIPTIONS[exclusion_criteria]


if __name__ == '__main__':
    """
    Main execution block for testing CodeClone dataset processing.
    """
    try:
        sr_project = CodeClone()
        print(f"\nCodeClone Dataset Summary:")
        print(f"Total articles: {len(sr_project.df)}")
        print(f"Articles with titles: {sr_project.df['title'].notna().sum()}")
        print(f"Articles with venues: {sr_project.df['venue'].notna().sum()}")
        print(f"Export path: {sr_project.export_path}")
        
        # Display screening decision counts (preserving original format)
        if 'screened_decision' in sr_project.df.columns:
            print('\nscreened_decision:', sum(sr_project.df['screened_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['screened_decision'] == 'Included'), 'Included')
            
        if 'final_decision' in sr_project.df.columns:
            print('final_decision:', sum(sr_project.df['final_decision'] == 'Excluded'), 'Excluded,',
                  sum(sr_project.df['final_decision'] == 'Included'), 'Included')
            
    except Exception as e:
        print(f"Error running CodeClone processing: {e}")
