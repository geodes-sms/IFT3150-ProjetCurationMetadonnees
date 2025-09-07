"""
Web Scraping Module for Systematic Literature Review Metadata Extraction

This module provides automated web scraping capabilities for extracting metadata
from academic databases using Selenium WebDriver. It supports multiple platforms
(Windows/Linux) and handles authentication for institutional access.

Key Features:
- Cross-platform Firefox configuration (Windows/Linux)
- Institutional authentication for ScienceDirect and Scopus
- Multi-database support (IEEE, ACM, Springer, ScienceDirect, etc.)
- Metadata extraction from HTML and BibTeX sources

Author: Guillaume Genois, 20248507
Purpose: Automated metadata extraction for systematic literature reviews
"""

import os
import platform
import time
from datetime import datetime

import pandas as pd
from lxml.etree import XPath
from selenium import webdriver
from pybtex.database.input import bibtex as bibtex_parser
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from . import htmlParser
from . import searchInSource
from ..core.SRProject import *
from ..core.os_path import MAIN_PATH, FIREFOX_PROFILE_PATH

# Global connection state
ALREADY_CONNECTED = False

# Institutional credentials (should be moved to environment variables)
INSTITUTIONAL_EMAIL = "guillaume.genois@umontreal.ca"
INSTITUTIONAL_PASSWORD = "Guigui-031!"

class WebScraper:
    """
    Main web scraper class for automated metadata extraction from academic databases.
    
    Handles browser initialization, authentication, and metadata extraction from
    multiple academic sources including IEEE, ACM, Springer, ScienceDirect, etc.
    """
    
    def __init__(self):
        """Initialize the web scraper with platform-specific Firefox configuration."""
        global ALREADY_CONNECTED
        
        # Configure Firefox based on operating system
        options = webdriver.FirefoxOptions()
        
        # Common configuration for both systems
        options.set_preference('network.proxy.type', 0)
        options.set_preference("general.useragent.override", 
                             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0")
        
        if platform.system() == "Linux":
            # Linux configuration (for Ubuntu/server environments)
            install_dir = "/snap/firefox/current/usr/lib/firefox"
            driver_loc = os.path.join(install_dir, "geckodriver")
            binary_loc = os.path.join(install_dir, "firefox")
            
            # Set up service and binary location for Linux
            service = webdriver.FirefoxService(driver_loc)
            options.binary_location = binary_loc
            # options.add_argument("-headless")  # Uncomment for headless mode on server
            
            # Initialize driver with service for Linux
            self.driver = webdriver.Firefox(options=options, service=service)
        else:
            # Windows configuration (development environment)
            profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
            options.profile = profile
            
            # Initialize driver without service for Windows
            self.driver = webdriver.Firefox(options=options)
        
        # Initialize academic database connections
        self._initialize_database_connections()
        
        # Initialize the search engine
        self.searcher = searchInSource.SearcherInSource(self.driver)

    def _initialize_database_connections(self):
        """Initialize connections to various academic databases."""
        global ALREADY_CONNECTED
        
        # Navigate to main academic databases
        self.driver.get("https://www.webofscience.com/wos/woscc/basic-search")  # Web of Science
        self.driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")  # IEEE
        self.driver.get("https://dl.acm.org/")  # ACM
        
        # Authenticate with ScienceDirect
        self._authenticate_sciencedirect()
        
        # Navigate to Scopus
        self.driver.get("https://www.scopus.com/")
        time.sleep(2)

        if not ALREADY_CONNECTED:
            ALREADY_CONNECTED = True

    def _authenticate_sciencedirect(self):
        """Handle institutional authentication for ScienceDirect."""
        self.driver.get("https://www.sciencedirect.com/")
        time.sleep(2)
        
        try:
            # Click institutional sign-in
            sign_in_btn = self.driver.find_element(By.XPATH, '//*[@id="gh-institutionalsignin-btn"]')
            sign_in_btn.click()
            time.sleep(2)
            
            # Enter email
            email_field = self.driver.find_element(By.XPATH, '//*[@id="bdd-email"]')
            email_field.send_keys(INSTITUTIONAL_EMAIL)
            time.sleep(2)
            
            # Search for institution
            search_btn = self.driver.find_element(By.XPATH, '//*[@id="bdd-els-searchBtn"]')
            search_btn.click()
            time.sleep(2)
            
            # Enter password
            password_field = self.driver.find_element(By.XPATH, '//*[@id="bdd-password"]')
            password_field.send_keys(INSTITUTIONAL_PASSWORD)
            time.sleep(2)
            
            # Submit login
            login_btn = self.driver.find_element(By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]')
            login_btn.click()
            time.sleep(2)
            
        except Exception as e:
            print(f"Authentication failed: {e}")

    def close(self):
        """Close the browser and reset connection state."""
        global ALREADY_CONNECTED
        ALREADY_CONNECTED = False
        self.driver.close()

    def get_source_from_doi_with_url(self, link):
        """
        Determine the academic source from a DOI link.
        
        Args:
            link (str): The DOI or URL to analyze
            
        Returns:
            str: The identified source name
        """
        self.driver.get(link)
        time.sleep(5)
        current_url = self.driver.current_url
        
        source_mapping = {
            "sciencedirect.com": ScienceDirect,
            "link.springer.com": SpringerLink,
            "dl.acm.org": ACM,
            "ieeexplore.ieee.org": IEEE,
            "scopus.com": Scopus,
            "arxiv.org": arXiv,
            "pubmed.ncbi.nlm.nih.gov": PubMedCentral
        }
        
        for domain, source in source_mapping.items():
            if domain in current_url:
                return source
        
        return None

    def get_html_from_link(self, link=None):
        """
        Retrieve HTML content from a given link.
        
        Args:
            link (str, optional): URL to fetch. If None, uses current page.
            
        Returns:
            str: HTML content of the page
        """
        if link:
            print(f"Navigating to: {link}")
            self.driver.get(link)
            time.sleep(2)
        return self.driver.page_source

    def get_metadata_from_link(self, title, link, source=None):
        """
        Extract metadata from a specific link based on the academic source.
        
        Args:
            title (str): Article title for validation
            link (str): URL or DOI to extract from
            source (str, optional): Academic source identifier
            
        Returns:
            dict: Extracted metadata dictionary
        """
        link_opened = False
        
        # Determine source if not provided
        if source is None:
            source = self.get_source_from_doi_with_url(link)
            link_opened = True
            if source is None:
                crossref_html = self.get_html_from_link(f"http://api.crossref.org/works/{link[16:]}")
                source = htmlParser.get_source_from_doi_with_crossref(crossref_html)
        
        metadata = metadata_base.copy()
        metadata['Link'] = link

        # Route to appropriate metadata extraction method based on source
        extraction_methods = {
            IEEE: self._extract_ieee_metadata,
            ScienceDirect: self._extract_sciencedirect_metadata,
            ACM: self._extract_acm_metadata,
            SpringerLink: self._extract_springer_metadata,
            Scopus: self._extract_scopus_metadata,
            WoS: self._extract_wos_metadata,
            PubMedCentral: self._extract_pubmed_metadata,
            arXiv: self._extract_arxiv_metadata
        }

        if source in extraction_methods:
            return extraction_methods[source](title, link, metadata, link_opened)
        else:
            print(f'Source "{source}" not recognized, searching all options')
            return self._search_all_sources(title, metadata)

    def _extract_ieee_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from IEEE source."""
        if 'doi' in link:
            self.driver.get(link)
            link = self.driver.current_url

        # Extract keywords
        html = self.get_html_from_link(f"{link}/keywords#keywords")
        new_metadata = htmlParser.get_metadata_from_html_ieee(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}/keywords#keywords_00", html)
        update_metadata(metadata, new_metadata)

        # Extract references
        html = self.get_html_from_link(f"{link}/references#references")
        save_extracted_html(f"{title}/references#references_00", html)
        new_metadata = htmlParser.get_metadata_from_html_ieee(html)
        update_metadata(metadata, new_metadata)
        
        # Extract BibTeX
        self.searcher.extract_bibtex_in_IEEE(title)
        self._process_bibtex(title, "00", metadata)
        
        return metadata

    def _extract_sciencedirect_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from ScienceDirect source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_sciencedirect(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}_02", html)
        update_metadata(metadata, new_metadata)
        
        self.searcher.extract_bibtex_in_ScienceDirect(title)
        self._process_bibtex(title, "02", metadata)
        
        return metadata

    def _extract_acm_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from ACM source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_ACM(html)
        save_extracted_html(f"{title}_01", html)
        metadata.update(new_metadata)
        
        self.searcher.extract_bibtex_in_ACM(title)
        self._process_bibtex(title, "01", metadata)
        
        return metadata

    def _extract_springer_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from Springer source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_springerlink(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}_03", html)
        metadata.update(new_metadata)
        
        self.searcher.extract_bibtex_in_SpringerLink(title)
        self._process_bibtex(title, "03", metadata)
        
        return metadata

    def _extract_scopus_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from Scopus source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_scopus(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}_07", html)
        metadata.update(new_metadata)
        
        self.searcher.extract_bibtex_in_scopus_signed_in(title)
        self._process_bibtex(title, "07", metadata)
        
        return metadata

    def _extract_wos_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from Web of Science source."""
        html = self.get_html_from_link(link if not link_opened else None)
        save_extracted_html(f"{title}_05", html)
        new_metadata = htmlParser.get_metadata_from_html_wos(html)
        if not check_if_right_link(new_metadata, title):
            return None
        metadata.update(new_metadata)
        
        self.searcher.extract_bibtex_in_WoS(title)
        self._process_bibtex(title, "05", metadata)
        
        return metadata

    def _extract_pubmed_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from PubMed Central source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}_08", html)
        metadata.update(new_metadata)
        
        self.searcher.extract_bibtex_in_PubMedCentral(title)
        self._process_bibtex(title, "08", metadata)
        
        return metadata

    def _extract_arxiv_metadata(self, title, link, metadata, link_opened):
        """Extract metadata from arXiv source."""
        html = self.get_html_from_link(link if not link_opened else None)
        new_metadata = htmlParser.get_metadata_from_html_arxiv(html)
        if not check_if_right_link(new_metadata, title):
            return None
        save_extracted_html(f"{title}_09", html)
        metadata.update(new_metadata)
        
        return metadata

    def _process_bibtex(self, title, source_code, metadata):
        """Process BibTeX file and update metadata."""
        try:
            parser = bibtex_parser.Parser()
            bib_file = f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_{source_code}.bib'
            bib_data = parser.parse_file(bib_file)
            bibtex_metadata = htmlParser.get_metadata_from_bibtex(bib_data)
            update_metadata(metadata, bibtex_metadata)
        except Exception as e:
            print(f"Failed to process BibTeX for {title}: {e}")

    def _search_all_sources(self, title, metadata):
        """Search all available sources when source is unknown."""
        print("Searching in all available sources")
        for source_name in sources_name:
            new_metadata = self.get_metadata_from_title(title, None, source_name, None)
            if check_if_right_link(new_metadata, title):
                update_metadata(metadata, new_metadata)
                break
        return metadata

    def get_metadata_from_title(self, title, author=None, source=None, year=None):
        """
        Search for and extract metadata using article title.
        
        Args:
            title (str): Article title to search for
            author (str, optional): Author name for refined search
            source (str, optional): Specific academic source to search
            year (str, optional): Publication year for refined search
            
        Returns:
            dict: Extracted metadata dictionary
        """
        print(f"Searching for: {title}")
        print(f"Source: {source}, Author: {author}, Year: {year}")
        
        # Normalize source name
        if source and source not in all_sources_name:
            for name in all_sources_name:
                if name in str(source):
                    source = name
                    break

        metadata = metadata_base.copy()

        # Route to appropriate search method
        search_methods = {
            IEEE: self.searcher.search_in_IEEE,
            ScienceDirect: self.searcher.search_in_ScienceDirect,
            ACM: self.searcher.search_in_ACM,
            SpringerLink: self.searcher.search_in_SpringerLink,
            Scopus: self.searcher.search_in_Scopus,
            ScopusSignedIn: self.searcher.search_in_Scopus_signed_in,
            WoS: self.searcher.search_in_WoS,
            PubMedCentral: self.searcher.search_in_PubMedCentral
        }

        if source in search_methods:
            new_metadata = search_methods[source](title)
            if new_metadata:
                update_metadata(metadata, new_metadata)
        else:
            print(f'Source "{source}" not valid, searching all options')
            for source_name in sources_name:
                new_metadata = self.get_metadata_from_title(title, author, source_name, year)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break

        return metadata


class ManualWebScraper:
    """
    Manual web scraper for interactive metadata extraction and testing.
    
    This class provides manual control over the scraping process and is primarily
    used for debugging, testing, and manual metadata extraction tasks.
    """
    
    def __init__(self):
        """Initialize manual web scraper with Linux-specific configuration."""
        # Note: This class assumes Linux environment - should be updated for cross-platform
        install_dir = "/snap/firefox/current/usr/lib/firefox"
        driver_loc = os.path.join(install_dir, "geckodriver")
        binary_loc = os.path.join(install_dir, "firefox")
        
        service = webdriver.FirefoxService(driver_loc)
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        options.binary_location = binary_loc
        options.set_preference('network.proxy.type', 0)
        options.set_preference("general.useragent.override", 
                             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Firefox/130.0")

        self.driver = webdriver.Firefox(options=options, service=service)
        
        # Authenticate with databases
        self._authenticate_sciencedirect()
        
        self.driver.get("https://www.scopus.com/")
        time.sleep(2)
        
        self.searcher = searchInSource.SearcherInSource(self.driver)

    def _authenticate_sciencedirect(self):
        """Handle institutional authentication for ScienceDirect."""
        self.driver.get("https://www.sciencedirect.com/")
        time.sleep(2)
        
        try:
            sign_in_btn = self.driver.find_element(By.XPATH, '//*[@id="gh-institutionalsignin-btn"]')
            sign_in_btn.click()
            time.sleep(2)
            
            email_field = self.driver.find_element(By.XPATH, '//*[@id="bdd-email"]')
            email_field.send_keys(INSTITUTIONAL_EMAIL)
            time.sleep(2)
            
            search_btn = self.driver.find_element(By.XPATH, '//*[@id="bdd-els-searchBtn"]')
            search_btn.click()
            time.sleep(2)
            
            password_field = self.driver.find_element(By.XPATH, '//*[@id="bdd-password"]')
            password_field.send_keys(INSTITUTIONAL_PASSWORD)
            time.sleep(2)
            
            login_btn = self.driver.find_element(By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]')
            login_btn.click()
            time.sleep(2)
            
        except Exception as e:
            print(f"Authentication failed: {e}")

    def get_bibtex_from_already_extracted(self):
        """Extract BibTeX from previously found links."""
        links_already_searched = pd.read_csv(
            f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv',
            sep='\t', encoding='windows-1252')
        already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
        
        for idx, row in links_already_searched.iterrows():
            try:
                title = row['Title']
                link = row['Link']
                print(f"Processing: {title}, {link}")
                
                for source in sources_name:
                    if source in link:
                        is_already_extracted = any(
                            file[11:-7] == format_link(title) 
                            for file in already_extracted_bibtex
                        )
                        
                        if not is_already_extracted:
                            print('Extracting...')
                            print(self.get_metadata_from_link(title, source, link))
            except Exception as e:
                print(f"Error processing {title}: {e}")

    def get_html_from_link(self, link):
        """Retrieve HTML content from a given link."""
        print(f"Fetching: {link}")
        self.driver.get(link)
        return self.driver.page_source

    def close(self):
        """Close the browser."""
        self.driver.close()


# Main execution for testing
if __name__ == '__main__':
    # Example usage and testing
    for sr in ['CodeCompr']:
        web_scraper = ManualWebScraper()
        web_scraper.get_bibtex_from_source_link(sr)
        web_scraper.close()