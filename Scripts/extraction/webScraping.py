import os
import time

import pandas as pd
from lxml.etree import XPath
# from fake_useragent import UserAgent
# import selenium_stealth
from selenium import webdriver
from pybtex.database.input import bibtex as bibtex_parser
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from . import htmlParser
from . import searchInSource
from ..core.SRProject import *
from ..core.os_path import MAIN_PATH, FIREFOX_PROFILE_PATH

ALREADY_CONNECTED = False

class WebScraper:
    def __init__(self):
        global ALREADY_CONNECTED
        install_dir = "/snap/firefox/current/usr/lib/firefox"
        driver_loc = os.path.join(install_dir, "geckodriver")
        binary_loc = os.path.join(install_dir, "firefox")

        service = webdriver.FirefoxService(driver_loc)
        # https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu
        # ua = UserAgent()
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        options.binary_location = binary_loc
        options.set_preference('network.proxy.type', 0)
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0)1 Firefox/130.0")
        # options.set_preference("general.useragent.override", ua.random)
        # options.add_argument("-headless")
        # self.driver = webdriver.Firefox(options=options)
        self.driver = webdriver.Firefox(options=options, service=service)
        self.driver.get("https://www.webofscience.com/wos/woscc/basic-search")  # WoS
        self.driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")  # IEEE
        self.driver.get("https://dl.acm.org/")  # ACM
        # self.driver.get("https://www.scopus.com/search/form.uri?display=basic#basic")  # ScopusSignedIn
        # time.sleep(2)

        self.driver.get("https://www.sciencedirect.com/")  # ScienceDirect + auth
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="gh-institutionalsignin-btn"]')
        web_element.click()
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-email"]')
        web_element.send_keys("guillaume.genois@umontreal.ca")
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-els-searchBtn"]')
        web_element.click()
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-password"]')
        web_element.send_keys("Guigui-031!")
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]')
        web_element.click()
        time.sleep(2)
        self.driver.get("https://www.scopus.com/")
        time.sleep(2)


        if not ALREADY_CONNECTED:
            # input("Continue?")
            ALREADY_CONNECTED = True
        # web_element = self.driver.find_element(By.XPATH, '//*[@id="qs"]')
        # web_element.send_keys("systematic review")
        # web_element = self.driver.find_element(By.XPATH,
        #                                        '/html/body/div[1]/div/div[1]/div[2]/div[1]/div/div/form/div[2]/button')
        # web_element.click()
        # web_element = self.driver.find_element(By.XPATH,
        #                                        '//*[@id="bdd-email"]')
        # web_element.send_keys("guillaume.genois@umontreal.ca")
        # web_element = self.driver.find_element(By.XPATH,
        #                                        '//*[@id="bdd-email"]')
        # web_element.send_keys("guillaume.genois@umontreal.ca")
        # web_element = self.driver.find_element(By.XPATH,
        #                                        '//*[@id="bdd-els-searchBtn"]')
        # web_element.click()
        # prendre courriel et copier le lien dans le navigateur robot

        self.searcher = searchInSource.SearcherInSource(self.driver)

    def close(self):
        global ALREADY_CONNECTED
        ALREADY_CONNECTED = False
        self.driver.close()

    def get_source_from_doi_with_url(self, link):
        self.driver.get(link)
        time.sleep(5)
        current_url = self.driver.current_url
        if "sciencedirect.com" in current_url:
            return ScienceDirect
        elif "link.springer.com" in current_url:
            return SpringerLink
        elif "dl.acm.org" in current_url:
            return ACM
        elif "ieeexplore.ieee.org" in current_url:
            return IEEE
        elif "scopus.com" in current_url:
            return Scopus
        elif "arxiv.org" in current_url:
            return arXiv
        elif "pubmed.ncbi.nlm.nih.gov" in current_url:
            return PubMedCentral

    def get_html_from_link(self, link=None):
        if link:
            print(link)
            self.driver.get(link)
            time.sleep(2)
        html = self.driver.page_source
        return html

    def get_metadata_from_link(self, title, link, source=None):
        # TODO: éviter 2e requête lorsque source is None
        link_opened = False
        if source is None:  # is DOI
            source = self.get_source_from_doi_with_url(link)
            link_opened = True
            if source is None:
                source = htmlParser.get_source_from_doi_with_crossref(self.get_html_from_link("http://api.crossref.org/works/" + link[16:]))
        metadata = metadata_base.copy()
        metadata['Link'] = link

        if not source:
            print("searching in all options")
            for name in sources_name:
                new_metadata = self.get_metadata_from_title(title, None, name, None)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break
        if source == IEEE or source == 'ieee' or 'Institute of Electrical and Electronics Engineers' in source:
            if 'doi' in link:
                self.driver.get(link)
                link = self.driver.current_url

            html = self.get_html_from_link(link + "/keywords#keywords")
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "/keywords#keywords" + "_00", html)
            update_metadata(metadata, new_metadata)

            html = self.get_html_from_link(link + "/references#references")
            save_extracted_html(title + "/references#references" + "_00", html)
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            update_metadata(metadata, new_metadata)
            self.searcher.extract_bibtex_in_IEEE(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_00.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == ScienceDirect or source == 'sciencedirect' or 'Elsevier' in source:
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_sciencedirect(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "_02", html)
            update_metadata(metadata, new_metadata)
            self.searcher.extract_bibtex_in_ScienceDirect(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_02.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == ACM or source in ['acm', "Association for Computing Machinery (ACM)", "ACM Press",
                                       "Society for Computer Simulation International"] or "ACM" in source:
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_ACM(html)
            # if not check_if_right_link(new_metadata, title):
            #     return
            save_extracted_html(title + "_01", html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_ACM(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_01.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == SpringerLink or 'Springer' in source or source == 'springer':
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_springerlink(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "_03", html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_SpringerLink(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_03.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == Scopus or source == 'scopus':
            # i.e.: "https://www.scopus.com/record/display.uri?eid=2-s2.0-85083744459&doi=10.1089%2fg4h.2019.0067&origin=inward&txGid=0d477ca65acc675d5e5d53dc3edac470"
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_scopus(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "_07", html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_scopus_signed_in(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_07.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

            if all(new_metadata[k] is None for k in new_metadata.keys()):
                last_half = link[link.find("doi"):]
                doi_not_formated = last_half[:last_half.find("&")]
                doi = "https://" + doi_not_formated.replace("=", ".org/").replace("%2f", "/")
                html = self.get_html_from_link(doi)
                save_extracted_html(doi + "_06", html)
                new_source = htmlParser.get_source_from_doi_with_crossref(html)
                new_metadata = self.get_metadata_from_link(title, doi, new_source)
                metadata.update(new_metadata)

        elif source == WoS or source == 'wos':
            html = self.get_html_from_link(link if not link_opened else None)
            save_extracted_html(title + "_05", html)
            new_metadata = htmlParser.get_metadata_from_html_wos(html)
            if not check_if_right_link(new_metadata, title):
                return
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_WoS(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_05.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == PubMedCentral:
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "_08", html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_PubMedCentral(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_08.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == arXiv or source == 'arxiv':
            html = self.get_html_from_link(link if not link_opened else None)
            new_metadata = htmlParser.get_metadata_from_html_arxiv(html)
            if not check_if_right_link(new_metadata, title):
                return
            save_extracted_html(title + "_09", html)
            metadata.update(new_metadata)
        else:
            print(f'source "{source}" not valid')
            print("searching in all options")
            for name in sources_name:
                new_metadata = self.get_metadata_from_title(title, None, name, None)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break
        if metadata: metadata["Link"] = link
        return metadata

    def get_metadata_from_title(self, title, author=None, source=None, year=None):
        # TODO: mettre link website si pas doi
        global driver
        tries = 0
        # research to find link and get metadata
        print("source", source)
        if source not in all_sources_name and source is not None:
            for name in all_sources_name:
                if name in str(source):
                    source = name
        print("title", title)
        print("new source", source)
        print("author", author)
        print("year", year)

        metadata = metadata_base.copy()
        # driver.get("https://www.crossref.org/guestquery/")
        if source == IEEE or source == 'ieee':
            new_metadata = self.searcher.search_in_IEEE(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ScienceDirect or source in ['sciencedirect', 'ScienceDirect']:
            new_metadata = self.searcher.search_in_ScienceDirect(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ACM or source in ['acm', "Association for Computing Machinery (ACM)", "ACM Press"]:
            new_metadata = self.searcher.search_in_ACM(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == SpringerLink or source in ['springer', 'Springer', 'SpringerLink']:
            new_metadata = self.searcher.search_in_SpringerLink(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == Scopus:
            new_metadata = self.searcher.search_in_Scopus(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ScopusSignedIn or source == 'scopus':
            new_metadata = self.searcher.search_in_Scopus_signed_in(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == WoS or source == 'wos':
            new_metadata = self.searcher.search_in_WoS(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == PubMedCentral:
            new_metadata = self.searcher.search_in_PubMedCentral(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        else:
            print(f'Source "{source}" not valid')
            print("searching in all options")
            for name in sources_name:
                new_metadata = self.get_metadata_from_title(title, author, name, year)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break

        return metadata


class ManualWebScraper:
    def __init__(self):
        # ua = UserAgent()
        install_dir = "/snap/firefox/current/usr/lib/firefox"
        driver_loc = os.path.join(install_dir, "geckodriver")
        binary_loc = os.path.join(install_dir, "firefox")
        service = webdriver.FirefoxService(driver_loc)
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        options.binary_location = binary_loc
        options.set_preference('network.proxy.type', 0)
        # options.set_preference("general.useragent.override", ua.random)
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0)1 Firefox/130.0")
        # options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0")
        # options.add_argument("-headless")

        self.driver = webdriver.Firefox(options=options, service=service)
        self.driver.get("https://www.sciencedirect.com/")  # ScienceDirect + auth
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="gh-institutionalsignin-btn"]')
        web_element.click()
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-email"]')
        web_element.send_keys("guillaume.genois@umontreal.ca")
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-els-searchBtn"]')
        web_element.click()
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-password"]')
        web_element.send_keys("Guigui-031!")
        time.sleep(2)
        web_element = self.driver.find_element(By.XPATH, '//*[@id="bdd-elsPrimaryBtn"]')
        web_element.click()
        time.sleep(2)
        self.driver.get("https://www.scopus.com/")
        time.sleep(2)

        self.searcher = searchInSource.SearcherInSource(self.driver)

    def get_bibtex_from_already_extracted(self):
        links_already_searched = pd.read_csv(
            f'{MAIN_PATH}/Scripts/data/articles_source_links.tsv',
            sep='\t', encoding='windows-1252')
        already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
        for idx, row in links_already_searched.iterrows():
            try:
                title = row['Title']
                link = row['Link']
                print(title, link)
                for source in sources_name:
                    if source in link:
                        is_already_extracted = False
                        for file in already_extracted_bibtex:
                            if file[11:-7] == format_link(title):
                                print("bibtex déjà extrait")
                                is_already_extracted = True
                                break
                        if not is_already_extracted:
                            print('extraction...')
                            print(self.get_metadata_from_link(title, source, link))
            except Exception as e:
                print(e)
                pass

    def get_bibtex_from_source_link(self, sr_project):
        source_link = pd.read_csv(f"{MAIN_PATH}/Datasets/{sr_project}/tmp.tsv", sep='\t')
        # source_link = source_link.loc[pd.isna(source_link['bibtex']) & pd.notnull(source_link['doi'])]
        print(source_link)
        already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
        for idx, row in source_link.iterrows():
            print(row[['doi']])
            try:
                link = str(row['link'])
                title = row['meta_title']
                verification_link = link
                if 'doi' in link:
                    self.driver.get(link)
                    time.sleep(3)
                    verification_link = self.driver.current_url
                for source in sources_name:
                    if source in verification_link:
                        is_already_extracted = False
                        # for file in already_extracted_bibtex:
                        #     if file[11:-7] == format_link(link):
                        #         print("bibtex déjà extrait")
                        #         is_already_extracted = True
                        #         break
                        if not is_already_extracted:
                            print('extraction...')
                            print(self.get_metadata_from_link(title, source, link))
                            time.sleep(2)
            except Exception as e:
                print(e)
                pass

    def search_missing_links_for_articles(self):
        extracted_articles = pd.read_csv(f"{MAIN_PATH}/Datasets/GameSE/GameSE.tsv", sep='\t', encoding='utf-8')
        for idx, row in extracted_articles.iterrows():
            try:
                if (pd.isna(row['doi']) or pd.isna(row['link'])) and not pd.isna(row['meta_title']):
                    self.get_metadata_from_title(row['meta_title'], source=row['source'])
                elif pd.isna(row['meta_title']):
                    self.get_metadata_from_title(row['title'])
            except Exception as e:
                print(e. __traceback__)

    def add_articles_manually(self):
        while True:
            try:
                title = input('title:\n')
                link = input('link:\n')
                source = None
                for src in sources_name:
                    if src in link:
                        source = src
                source = input('source:\n') if not source else source
                print(self.get_metadata_from_link(title, source, link))
            except Exception as e:
                print(e, e.__traceback__)

    def get_metadata_from_title(self, title, author=None, source=None, year=None):
        # TODO: mettre link website si pas doi
        tries = 0
        # research to find link and get metadata
        print("source", source)
        if source not in all_sources_name and source is not None:
            for name in all_sources_name:
                if name in str(source):
                    source = name
        print("title", title)
        print("new source", source)
        print("author", author)
        print("year", year)

        metadata = metadata_base.copy()
        # driver.get("https://www.crossref.org/guestquery/")
        if source == IEEE or source == 'ieee':
            new_metadata = self.searcher.search_in_IEEE(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ScienceDirect or source in ['sciencedirect', 'ScienceDirect']:
            new_metadata = self.searcher.search_in_ScienceDirect(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ACM or source in ['acm', "Association for Computing Machinery (ACM)", "ACM Press"]:
            new_metadata = self.searcher.search_in_ACM(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == SpringerLink or source in ['springer', 'Springer', 'SpringerLink']:
            new_metadata = self.searcher.search_in_SpringerLink(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == Scopus or source == 'scopus':
            new_metadata = self.searcher.search_in_Scopus(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == ScopusSignedIn:
            new_metadata = self.searcher.search_in_Scopus_signed_in(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == WoS or source == 'wos':
            new_metadata = self.searcher.search_in_WoS(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        elif source == PubMedCentral:
            new_metadata = self.searcher.search_in_PubMedCentral(title)
            if not new_metadata: new_metadata = metadata_base.copy()
            update_metadata(metadata, new_metadata)

        else:
            print(f'Source "{source}" not valid')
            print("searching in all options")
            for name in sources_name:
                new_metadata = self.get_metadata_from_title(title, author, name)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break

        return metadata
        
    def get_metadata_from_link(self, title, source, link):
        # TODO: mettre link website si pas doi
        global driver
        tries = 0
        # research to find link and get metadata
        print("source", source)
        if source not in all_sources_name and source is not None:
            for name in all_sources_name:
                if name in str(source):
                    source = name
        print("title", title)
        print("new source", source)

        metadata = metadata_base.copy()
        # driver.get("https://www.crossref.org/guestquery/")
        if source == IEEE or source == 'ieee':
            html = self.get_html_from_link(link + "/keywords#keywords")
            save_extracted_html(title + "/keywords#keywords" + "_00", html)
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            update_metadata(metadata, new_metadata)

            html = self.get_html_from_link(link + "/references#references")
            save_extracted_html(title + "/references#references" + "_00", html)
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            update_metadata(metadata, new_metadata)
            save_link(title, link)
            self.searcher.extract_bibtex_in_IEEE(title)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_00.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == ScienceDirect or source == 'sciencedirect':
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_02", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_sciencedirect(html)
            update_metadata(metadata, new_metadata)
            self.searcher.extract_bibtex_in_ScienceDirect(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_02.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == ACM or source in ['acm', "Association for Computing Machinery (ACM)", "ACM Press",
                                       "Society for Computer Simulation International"] or "ACM" in source:
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_01", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_ACM(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_ACM(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_01.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == SpringerLink or source == 'springer':
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_03", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_springerlink(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_SpringerLink(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_03.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        # elif source == Scopus or source == 'scopus':
        #     # i.e.: "https://www.scopus.com/record/display.uri?eid=2-s2.0-85083744459&doi=10.1089%2fg4h.2019.0067&origin=inward&txGid=0d477ca65acc675d5e5d53dc3edac470"
        #     html = self.get_html_from_link(link)
        #     save_extracted_html(title + "_04", html)
        #     save_link(title, link)
        #     new_metadata = htmlParser.get_metadata_from_html_scopus(html)
        #     metadata.update(new_metadata)

        elif source == ScopusSignedIn or source == 'scopus':
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_07", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_scopus_signed_in(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_scopus_signed_in(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_07.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == WoS or source == 'wos':
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_05", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_wos(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_WoS(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_05.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == PubMedCentral:
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_08", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
            metadata.update(new_metadata)
            # TODO: extract bibtex

        elif source == arXiv or source == 'arxiv':
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_09", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_arxiv(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_arXiv(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}/Bibtex/{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_09.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        else:
            print(f'Source "{source}" not valid')

        return metadata

    def get_html_from_link(self, link):
        print(link)
        self.driver.get(link)
        html = self.driver.page_source
        return html

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    venues_name = ['ieee', 'springer', 'acm', 'sciencedirect', 'scopus', 'wos']
    # url = f"https://ieeexplore.ieee.org/document/8712362"
    # url = f"https://link.springer.com/article/10.1057/s41269-023-00314-6"
    # url = f"https://dl.acm.org/doi/10.1145/2364412.2364472"
    # url = f"https://www.sciencedirect.com/science/article/pii/S2090123221001491"
    # url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85083744459&doi=10.1089%2fg4h.2019.0067&origin=inward&txGid=0d477ca65acc675d5e5d53dc3edac470"
    # url = "https://doi.org/10.1145/1486508.1486516"
    # url = "https://doi.org/10.1145/2662253.2662286"
    # source = None
    # for name in sources_name:
    #     if name in url:
    #         source = name
    # results = get_metadata_from_link(url, ACM)
    # for key in results.keys():
    #     print(key, results[key])
    # title = "The task graph pattern"  # ACM
    # title = "Second generation systems and software product line engineering"  # IEEE
    # title = "Android Malware Detection Based On System Calls Analysis And Cnn Classification"  # IEEE au 2e
    # title = "The explanatory power of playability heuristics"  # WoS
    # title = 'Let’s Play: Exploring literacy practices in an emerging videogame paratext'
    # web_scraper = WebScraper()
    # print(web_scraper.get_metadata_from_title(title, None, ScopusSignedIn))
    # title = "ME3CA: A cognitive assistant for physical exercises that monitors emotions and the environment"
    # link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7039382/"
    for sr in ['CodeCompr']:
        web_scraper = ManualWebScraper()
        # print(web_scraper.get_metadata_from_title(title, PubMedCentral, link))
        # web_scraper.get_bibtex_from_already_extracted()
        web_scraper.get_bibtex_from_source_link(sr)
        # web_scraper.search_missing_links_for_articles()
        # web_scraper.add_articles_manually()
        web_scraper.close()
