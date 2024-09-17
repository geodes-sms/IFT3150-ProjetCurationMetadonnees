import os

# from fake_useragent import UserAgent
from selenium import webdriver
from pybtex.database.input import bibtex as bibtex_parser

import htmlParser
import searchInSource
from SRProject import *
from os_path import MAIN_PATH, FIREFOX_PROFILE_PATH


# TODO: ajouter filtre article title seulement sur scopus

class WebScraper:
    def __init__(self):
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
        # options.set_preference("general.useragent.override", ua.random)
        # options.add_argument("-headless")
        # self.driver = webdriver.Firefox(options=options)
        self.driver = webdriver.Firefox(options=options, service=service)
        self.driver.get("https://www.webofscience.com/wos/woscc/basic-search")  # WoS
        self.driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")  # IEEE
        self.driver.get("https://dl.acm.org/")  # ACM

        self.driver.get("https://www.sciencedirect.com/")  # ScienceDirect + auth
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
        self.driver.close()

    def get_html_from_link(self, link):
        print(link)
        driver.get(link)
        html = driver.page_source
        return html

    def get_metadata_from_link(self, link, source=None):
        if source is None:  # is DOI
            source = htmlParser.get_venue_from_doi(self.get_html_from_link("http://api.crossref.org/works/" + link[16:]))
        metadata = metadata_base.copy()
        metadata['Link'] = link

        if source == IEEE or source == 'ieee':
            html = self.get_html_from_link(link + "/keywords#keywords")
            save_extracted_html(link + "/keywords#keywords" + "_00", html)
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            update_metadata(metadata, new_metadata)

            html = self.get_html_from_link(link + "/references#references")
            save_extracted_html(link + "/references#references" + "_00", html)
            new_metadata = htmlParser.get_metadata_from_html_ieee(html)
            update_metadata(metadata, new_metadata)
            self.searcher.extract_bibtex_in_IEEE(link, link)

        elif source == ScienceDirect or source == 'sciencedirect':
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_02", html)
            new_metadata = htmlParser.get_metadata_from_html_sciencedirect(html)
            update_metadata(metadata, new_metadata)
            self.searcher.extract_bibtex_in_ScienceDirect(link, link)

        elif source == ACM or source in ['acm', "Association for Computing Machinery (ACM)", "ACM Press",
                                       "Society for Computer Simulation International"] or "ACM" in source:
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_01", html)
            new_metadata = htmlParser.get_metadata_from_html_ACM(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_ACM(link, link)

        elif source == SpringerLink or source == 'springer':
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_03", html)
            new_metadata = htmlParser.get_metadata_from_html_springerlink(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_SpringerLink(link, link)

        elif source == Scopus or source == 'scopus':
            # i.e.: "https://www.scopus.com/record/display.uri?eid=2-s2.0-85083744459&doi=10.1089%2fg4h.2019.0067&origin=inward&txGid=0d477ca65acc675d5e5d53dc3edac470"
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_04", html)
            new_metadata = htmlParser.get_metadata_from_html_scopus(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_scopus_signed_in(link, link)

            if all(new_metadata[k] is None for k in new_metadata.keys()):
                last_half = link[link.find("doi"):]
                doi_not_formated = last_half[:last_half.find("&")]
                doi = "https://" + doi_not_formated.replace("=", ".org/").replace("%2f", "/")
                html = self.get_html_from_link(doi)
                save_extracted_html(doi + "_06", html)
                new_source = htmlParser.get_venue_from_doi(html)
                new_metadata = self.get_metadata_from_link(doi, new_source)
                metadata.update(new_metadata)

        elif source == WoS or source == 'wos':
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_05", html)
            new_metadata = htmlParser.get_metadata_from_html_wos(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_WoS(link, link)

        elif source == PubMedCentral:
            html = self.get_html_from_link(link)
            save_extracted_html(link + "_08", html)
            new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_PubMedCentral(link, link)

        else:
            print(f'source "{source}" not valid')
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
                new_metadata = self.get_metadata_from_title(title, author, name, year)
                if check_if_right_link(new_metadata, title):
                    update_metadata(metadata, new_metadata)
                    break

        return metadata


class ManualWebScraper:
    def __init__(self):
        # ua = UserAgent()
        profile = webdriver.FirefoxProfile(FIREFOX_PROFILE_PATH)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        options.set_preference('network.proxy.type', 0)
        # options.set_preference("general.useragent.override", ua.random)
        # options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.searcher = searchInSource.SearcherInSource(self.driver)

    def get_bibtex_from_already_extracted(self):
        links_already_searched = pd.read_csv(
            f'{MAIN_PATH}/Scripts/articles_source_links.tsv',
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
                            print(self.get_metadata_from_title(title, source, link))
            except Exception as e:
                print(e)
                pass

    def get_bibtex_from_source_link(self):
        source_link = pd.read_excel(f"{MAIN_PATH}/Datasets/GameSE/GameSE_pre-extract.xlsx")
        already_extracted_bibtex = os.listdir(f"{EXTRACTED_PATH}/Bibtex")
        for idx, row in source_link.iterrows():
            try:
                link = row['doi']
                title = link
                verification_link = link
                if 'doi' in link:
                    self.driver.get(link)
                    verification_link = self.driver.current_url
                print(title, link)
                for source in sources_name:
                    if source in verification_link:
                        is_already_extracted = False
                        for file in already_extracted_bibtex:
                            if file[11:-7] == format_link(title):
                                print("bibtex déjà extrait")
                                is_already_extracted = True
                                break
                        if not is_already_extracted:
                            print('extraction...')
                            print(self.get_metadata_from_title(title, source, link))
            except Exception as e:
                print(e)
                pass
            
    def add_articles_manually(self):
        while True:
            try:
                title = input('title:\n')
                link = input('link:\n')
                source = input('source:\n')
                print(self.get_metadata_from_title(title, source, link))
            except Exception as e:
                print(e, e.__traceback__)
        
    def get_metadata_from_title(self, title, source, link):
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
            self.searcher.extract_bibtex_in_IEEE(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_00.bib')
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
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_02.bib')
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
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_01.bib')
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
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_03.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == Scopus or source == 'scopus':
            # i.e.: "https://www.scopus.com/record/display.uri?eid=2-s2.0-85083744459&doi=10.1089%2fg4h.2019.0067&origin=inward&txGid=0d477ca65acc675d5e5d53dc3edac470"
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_04", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_scopus(html)
            metadata.update(new_metadata)

        elif source == ScopusSignedIn:
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_07", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_scopus_signed_in(html)
            metadata.update(new_metadata)
            self.searcher.extract_bibtex_in_scopus_signed_in(title, link)
            parser = bibtex_parser.Parser()
            bib_data = parser.parse_file(
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_07.bib')
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
                f'{EXTRACTED_PATH}\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_05.bib')
            update_metadata(metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        elif source == PubMedCentral:
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_08", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
            metadata.update(new_metadata)
            # TODO: extract bibtex

        elif source == arXiv:
            html = self.get_html_from_link(link)
            save_extracted_html(title + "_09", html)
            save_link(title, link)
            new_metadata = htmlParser.get_metadata_from_html_arxiv(html)
            metadata.update(new_metadata)
            # TODO: extract bibtex

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
    title = 'Let’s Play: Exploring literacy practices in an emerging videogame paratext'
    # web_scraper = WebScraper()
    # print(web_scraper.get_metadata_from_title(title, None, ScopusSignedIn))
    # title = "ME3CA: A cognitive assistant for physical exercises that monitors emotions and the environment"
    # link = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7039382/"
    web_scraper = ManualWebScraper()
    # print(web_scraper.get_metadata_from_title(title, PubMedCentral, link))
    # web_scraper.get_bibtex_from_already_extracted()
    web_scraper.get_bibtex_from_source_link()
    web_scraper.close()
