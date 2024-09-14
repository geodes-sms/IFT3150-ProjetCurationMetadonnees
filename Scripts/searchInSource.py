import glob
import os
import shutil

import htmlParser
from SRProject import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from pybtex.database.input import bibtex as bibtex_parser
import random
from datetime import datetime
import time


class SearcherInSource:
    def __init__(self, driver):
        self.driver = driver

    def wait_to_load(self, timeout, XPath):
        # s'assurer que fini de load
        wrapper = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, XPath))
        )
        
    def save_bibtex(self, title, source_id):
        # https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder
        list_of_files = glob.glob('C:\\Users\\guill\\Downloads\\*.bib') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)

        shutil.move(latest_file,
                    f'D:\\Projet Curation des métadonnées\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_{source_id}.bib')

        if os.path.isfile(latest_file):
            os.remove(latest_file)
            
    def extract_bibtex_in_IEEE(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/div/div[2]/xpl-cite-this-modal/div/button')
        # Cite
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="xplMainContentLandmark"]/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/div/div[2]/xpl-cite-this-modal/div/button')
        web_element.click()

        # BibTeX
        web_element = self.driver.find_element(By.XPATH,
                                               '/html/body/ngb-modal-window/div/div/div/div[2]/nav/div[2]/a')
        web_element.click()
        time.sleep(1)
        
        # Citation and Abstract
        web_element = self.driver.find_element(By.XPATH,
                                               '/html/body/ngb-modal-window/div/div/div/div[3]/div[1]/div[1]/input')
        web_element.click()
        time.sleep(1)

        # Download
        web_element = self.driver.find_element(By.XPATH,
                                               '/html/body/ngb-modal-window/div/div/div/div[3]/div[1]/div[2]/a[2]')
        web_element.click()
        time.sleep(2)
        
        self.save_bibtex(title, '00')

    def search_in_IEEE(self, title):
        tries = 0
        try:
            # simuler un utilisateur normal ouvrant la page principale puis allant sur le advanced search
            # self.driver.get("https://ieeexplore.ieee.org/Xplore/home.jsp")
            # wait_to_load(30, "/html/body/div[5]/div/div/div[3]/div/xpl-root/header/xpl-header/div/div[2]/div[2]/xpl-search-bar-migr/div/div/div/div[1]/a")
            # # web_element = self.driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[3]/div/xpl-root/header/xpl-header/div/div[2]/div[2]/xpl-search-bar-migr/div/div/div/div[1]/a")
            # # web_element.click()
            # self.driver.implicitly_wait(random.randint(2, 5))
    
            # aller sur advanced search
            self.driver.get("https://ieeexplore.ieee.org/search/advanced")
            self.wait_to_load(30,
                         "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-advanced-search/div[2]/div[1]/xpl-advanced-search-advanced/div/div[2]/form/div[1]/div[1]/div[1]/div/div/input")
            time.sleep(random.randint(2, 5))
            
            # Sélectionne la recherche seulement pour le titre de l'article
            web_element = self.driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-advanced-search/div[2]/div[1]/xpl-advanced-search-advanced/div/div[2]/form/div[1]/div[1]/div[2]/div/select')
            select_element = Select(web_element)
            select_element.select_by_value('3: Document Title')
    
            # Insère dans la boîte de texte appropriée le titre de l'article
            web_element = self.driver.find_element(By.XPATH,
                                              "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-advanced-search/div[2]/div[1]/xpl-advanced-search-advanced/div/div[2]/form/div[1]/div[1]/div[1]/div/div/input")
            # web_element = self.driver.find_element(By.CSS_SELECTOR, "div.has-float-label:nth-child(1) > input:nth-child(1)")
    
            # self.driver.implicitly_wait(random.randint(2, 5))
            web_element.clear()
            print("clean_title", clean_title(title))
            web_element.send_keys(clean_title(title))  # entre "" signifie que trouve valeur exacte
    
            # Clique pour lancer la recherche
            web_element = self.driver.find_element(By.XPATH,
                                              "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-advanced-search/div[2]/div[1]/xpl-advanced-search-advanced/div/div[2]/form/div[4]/button[2]")
            time.sleep(random.randint(2, 5))
            # self.driver.implicitly_wait(random.randint(2, 5))
            web_element.click()

            # self.driver.get("https://ieeexplore.ieee.org/document/5230801")
            while tries < 5:
                self.wait_to_load(30,
                                  "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-search-results/div/div[2]/div[2]/xpl-results-list/div[3]/xpl-results-item/div[1]/div[1]/div[2]/h3/a")
                # Clique pour ouvrir le premier document
                # web_element = self.driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-search-results/div/div[2]/div[2]/xpl-results-list/div[3]/xpl-results-item/div[1]/div[1]/div[2]/h3/a")
                web_element = self.driver.find_element(By.XPATH,
                                                  "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-search-results/div/div[2]/div[2]/xpl-results-list/div[" + str(
                                                      tries + 3) + "]/xpl-results-item/div[1]/div[1]/div[2]/h3/a")
                time.sleep(random.randint(2, 5))
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()
    
                # Attend que le document ouvre
                self.wait_to_load(30,
                             "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-document-details/div/div[1]/section[2]/div/xpl-document-header/section/div[2]/div/div/div[1]/div/div[1]/h1/span")
                time.sleep(random.randint(2, 5))
                self.driver.implicitly_wait(random.randint(2, 5))
    
                # Parse la page web pour extraire le metadata
                html = self.driver.page_source
                new_metadata = htmlParser.get_metadata_from_html_ieee(html)
                if not check_if_right_link(new_metadata, title):
                    tries += 1
                    self.driver.back()
                    print("retour")
                    continue
                break
        except:
            try:
                # didn't find
                if self.driver.find_element(By.XPATH,
                                       "/html/body/div[5]/div/div/div[3]/div/xpl-root/main/div/xpl-search-results/div/div[1]/div/xpl-search-dashboard/section/div/h1/span[1]"):
                    print("no results found")
                    return  # no results found
            except:
                return
                # signigie que roule dans le vide
                self.driver.close()
                self.driver = webself.driver.Firefox(options=options)
                tries += 1
    
        # a fonctionne
        link = self.driver.current_url
        save_link(title, link)
        self.driver.get(link + "/keywords#keywords")
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_ieee(html)
        print(new_metadata)
        if not check_if_right_link(new_metadata, title):
            return
        save_extracted_html(title + "/keywords#keywords_00", html)
        new_metadata['Link'] = link

        self.driver.get(link + "/references#references")
        html = self.driver.page_source
        tmp_metadata = htmlParser.get_metadata_from_html_ieee(html)
        update_metadata(new_metadata, tmp_metadata)
        # if not check_if_right_link(new_metadata, title):
        #     return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + "/references#references_00", html)
        self.extract_bibtex_in_IEEE
        return new_metadata
    
    def extract_bibtex_in_ACM(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="skip-to-main-content"]/main/article/header/div/div[7]/div[2]/div[3]/button')
            time.sleep(3)
        # scroll to see cite
        # self.driver.move_to_element(self.driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/article/header/div/div[7]/div[2]/div[3]/button'))
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Cite
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="skip-to-main-content"]/main/article/header/div/div[7]/div[2]/div[3]/button')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", web_element)
        time.sleep(2)
        web_element.click()
        time.sleep(1)

        # download
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="selectedTab"]/div/div[2]/ul/li[1]/a')
        web_element.click()
        
        time.sleep(2)
        
        self.save_bibtex(title, '01')

    def search_in_ACM(self, title):
        tries = 0
        try:
            # ouvrir la page principale avec la barre de recherche
            self.driver.get("https://dl.acm.org/")
            self.wait_to_load(30,
                              "/html/body/div[2]/div/div[1]/main/section[1]/div/div[1]/div/div[1]/div/form/div/div/div/input")

            # écrire le titre de l'article
            web_element = self.driver.find_element(By.XPATH,
                                                   "/html/body/div[2]/div/div[1]/main/section[1]/div/div[1]/div/div[1]/div/form/div/div/div/input")
            # web_element.clear()
            web_element.send_keys(clean_title(title))

            # lancer la recherche
            web_element = self.driver.find_element(By.XPATH,
                                                   "/html/body/div[2]/div/div[1]/main/section[1]/div/div[1]/div/div[1]/div/form/div/div/button")
            web_element.click()
            # self.wait_to_load(30,
            #              "/html/body/div[2]/div/div[1]/main/div[1]/div/div[1]/div/div[1]/div/form/div/div/div/input")
            # web_element = self.driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[3]/div/xpl-root/header/xpl-header/div/div[2]/div[2]/xpl-search-bar-migr/div/div/div/div[1]/a")
            # web_element.click()

            # aller sur advanced search
            # self.driver.get("https://dl.acm.org/search/advanced")
            # self.wait_to_load(30, '//*[@id="text1"]')
            # self.driver.implicitly_wait(10)

            # Insère dans la boîte de texte appropriée le titre de l'article
            # web_element = self.driver.find_element(By.XPATH, '//*[@id="text1"]')
            # web_element.send_keys(title)  # entre "" signifie que trouve valeur exacte
            # self.driver.implicitly_wait(10)

            # Clique pour lancer la recherche
            # web_element = self.driver.find_element(By.XPATH, '//*[@id="advanced-search-btn"]')
            # web_element.click()

            while tries < 5:
                self.wait_to_load(30,
                                  "/html/body/div[2]/div/div[1]/main/div[1]/div/div[2]/div/ul/li[1]/div[2]/div[2]/div/h5/span/a")

                # Clique pour ouvrir le premier document
                web_element = self.driver.find_element(By.XPATH,
                                                       "/html/body/div[2]/div/div[1]/main/div[1]/div/div[2]/div/ul/li[" + str(
                                                           tries + 1) + "]/div[2]/div[2]/div/h5/span/a")
                web_element.click()
                self.wait_to_load(30, "/html/body/div[1]/div/div[1]/main/article/header/div/h1")

                # Parse la page web pour extraire le metadata
                html = self.driver.page_source
                new_metadata = htmlParser.get_metadata_from_html_ACM(html)
                if not check_if_right_link(new_metadata, title):
                    tries += 1
                    self.driver.back()
                    print("retour")
                    continue
                break
        except Exception as e:
            print("error", e)
            try:
                # didn't find
                if self.driver.find_element(By.XPATH,
                                            "/html/body/div[2]/div/div[1]/main/div/div/div[2]/div/div[3]"):
                    print("no results found")
                    return  # no results found
            except:
                # self.driver.close()
                # self.driver = webself.driver.Firefox(options=options)
                return

        # Parse la page web pour extraire le metadata
        link = self.driver.current_url
        save_link(title, link)
        self.driver.get(link)
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_ACM(html)
        if not check_if_right_link(new_metadata, title):
            return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + '_01', html)
        new_metadata['Link'] = link
        self.extract_bibtex_in_ACM
        return new_metadata
    
    def extract_bibtex_in_WoS(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="FullRecSnRecListtop"]/app-export-menu/div/button')
        # Export
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="FullRecSnRecListtop"]/app-export-menu/div/button')
        web_element.click()

        # to bibtex
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="exportToBibtexButton"]')
        web_element.click()

        # open dropdown menu
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="FullRecordExportToEnwOptionContentover"]/button')
        web_element.click()
        
        # choose "Full Record and Cited References"
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="global-select"]/div/div/div[4]')
        web_element.click()
        
        # Export
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="FullRecordExportToEnwBtnover"]')
        web_element.click()
        
        time.sleep(2)
        
        self.save_bibtex(title, '05')

    def search_in_WoS(self, title):
        tries = 0
        while tries < 5:
            try:
                # aller sur basic search
                self.driver.get("https://www.webofscience.com/wos/woscc/basic-search")
                self.wait_to_load(30, '//*[@id="search-option"]')
                self.driver.implicitly_wait(random.randint(2, 5))

                # print(self.driver.page_source)

                # appuie sur le x pour effacer la recherche précédente
                try:
                    # self.wait_to_load(30, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]/app-search-row/div/div[2]/mat-form-field/div/div[1]/div[4]/div/button')
                    web_element = self.driver.find_element(By.CSS_SELECTOR, '.clear-row-button')
                    web_element.click()
                except:
                    pass
                
                # Sélectionne de rechercher seulement sur les titres d'articles
                web_element = self.driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div[2]/app-input-route/app-search-basic/app-search-form/form/div[1]/app-search-row/div/div[1]/app-select-search-field/wos-select/button')
                web_element.click()
                web_element = self.driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div[2]/app-input-route/app-search-basic/app-search-form/form/div[1]/app-search-row/div/div[1]/app-select-search-field/wos-select/div/div[1]/div/div[3]')
                web_element.click()

                # Insère dans la boîte de texte appropriée le titre de l'article
                web_element = self.driver.find_element(By.XPATH, '//*[@id="search-option"]')
                self.driver.implicitly_wait(random.randint(2, 5))
                time.sleep(random.randint(2, 5))
                web_element.send_keys(clean_title(title))

                # Clique pour lancer la recherche
                web_element = self.driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[3]/button[2]')
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()
                self.wait_to_load(30, "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-base-summary-component/div/div[2]/app-records-list/app-record/div/div/div[2]/div[1]/app-summary-title/h3/a")

                # Clique pour ouvrir le premier document
                web_element = self.driver.find_element(By.XPATH, "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-base-summary-component/div/div[2]/app-records-list/app-record/div/div/div[2]/div[1]/app-summary-title/h3/a")
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()

                # Attend que le document ouvre
                self.wait_to_load(30, '//*[@id="FullRTa-fullRecordtitle-0"]')
                self.driver.implicitly_wait(random.randint(2, 5))
                break
            except TimeoutException:
                try:
                    # didn't find
                    if self.driver.find_element(By.XPATH,
                                           "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]"):
                        print("no results found")
                        return  # no results found
                except:
                    # self.driver.close()
                    # self.driver = webself.driver.Firefox(options=options)
                    return
            html = self.driver.page_source
            new_metadata = htmlParser.get_metadata_from_html_wos(html)
            print("new_metadata", new_metadata)
            if not check_if_right_link(new_metadata, title):
                return  # TODO: ajouter plutôt avant le break et changer d'article
            save_extracted_html(title + '_05', html)
            save_link(title, self.driver.current_url)
            new_metadata['Link'] = self.driver.current_url
            self.extract_bibtex_in_WoS
            return new_metadata

    def search_in_Scopus(self, title):
        return

    def extract_bibtex_in_scopus_signed_in(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, "/html/body/div/div/div[1]/div[2]/div/div[3]/div[3]/div/div[1]/div[2]/micro-ui/scopus-document-details-page/div/article/div[2]/div[3]/div/div[2]/section/div/div/div/div/span/button")
        web_element = self.driver.find_element(By.XPATH,
                                               "/html/body/div/div/div[1]/div[2]/div/div[3]/div[3]/div/div[1]/div[2]/micro-ui/scopus-document-details-page/div/article/div[2]/div[3]/div/div[2]/section/div/div/div/div/span/button")
        web_element.click()

        web_element = self.driver.find_element(By.XPATH,
                                               "/html/body/div/div/div[1]/div[2]/div/div[3]/div[3]/div/div[1]/div[2]/micro-ui/scopus-document-details-page/div/article/div[2]/div[3]/div/div[2]/section/div/div/div/div/span/div/div[1]/button")
        web_element.click()

        web_element = self.driver.find_element(By.XPATH,
                                               "/html/body/div/div/div[1]/div[2]/div/div[3]/div[3]/div/div[1]/div[2]/micro-ui/scopus-document-details-page/div/article/div[2]/div[3]/div/div[2]/section/div/div/div/div[2]/div/div/section/div[2]/div/div/span[2]/div/div/button")
        web_element.click()
        time.sleep(2)
        
        self.save_bibtex(title, '07')

        # shutil.move('C:\\Users\\guill\\Downloads\\scopus.bib',
        #             f'D:\\Projet Curation des métadonnées\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{format_link(title)}_07.bib')
        # time.sleep(2)

        # if os.path.isfile('C:\\Users\\guill\\Downloads\\scopus.bib'):
        #     os.remove('C:\\Users\\guill\\Downloads\\scopus.bib')


    def search_in_Scopus_signed_in(self, title):
        tries = 0
        while tries < 5:
            try:
                # aller sur basic search
                self.driver.get("https://www.scopus.com/home.uri?zone=header&origin=searchbasic")
                self.wait_to_load(30, '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[2]/div/div[1]/div/label/input')
                self.driver.implicitly_wait(random.randint(2, 5))

                # appuie sur le x pour effacer la recherche précédente
                try:
                    web_element = self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[2]/div[2]/button[1]')
                    web_element.click()
                    print("reset")
                    time.sleep(2)
                except:
                    pass
                
                # Sélectionne la recherche seulement pour le titre de l'article
                web_element = self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[1]/label/select')
                select_element = Select(web_element)
                select_element.select_by_value('TITLE')

                # Insère dans la boîte de texte appropriée le titre de l'article
                web_element = self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[2]/div/div/label/input')
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.send_keys(clean_title(title))
                print("title")
                time.sleep(random.randint(2, 5))

                # try:
                #     # Insère dans la boîte de texte appropriée le titre de l'article
                #     web_element = self.driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[1]/div/div/div[2]/div/div[1]/div/label/input')
                #     self.driver.implicitly_wait(random.randint(2, 5))
                #     time.sleep(random.randint(2, 5))
                #     web_element.send_keys(clean_title(title))
                # except:
                #     pass

                # Clique pour lancer la recherche
                for i in range(3).__reversed__():
                    try:
                        web_element = self.driver.find_element(By.XPATH,
                                                           '/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[2]/div[2]/micro-ui/scopus-homepage/div/div[2]/div/div/div[1]/div[3]/div/div/form/div/div[2]/div[2]/button[' + str(i) + ']')
                        self.driver.implicitly_wait(random.randint(2, 5))
                        web_element.click()
                        print("click")
                        break
                    except:
                        pass

                self.wait_to_load(30, "/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/div/h3/a")
                # Clique pour ouvrir le premier document
                # web_element = self.driver.find_element(By.XPATH,
                #                                        "/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[5]/td[2]/div/div/h3/a")
                #                                        "/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[12]/td[2]/div/div/h3/a")
                # web_element = self.driver.find_element(By.XPATH,
                #                                        "/html/body/div[4]/div/div[2]/div/div[2]/div[2]/ol/li[" + str(
                #                                            tries + 1) + "]/div[1]/div/h3/a")
                web_element = self.driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[2]/td[2]/div/div/h3/a")
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()

                # Attend que le document ouvre
                self.wait_to_load(30, '/html/body/div/div/div[1]/div[2]/div/div[3]/div[3]/div/div[1]/div[2]/micro-ui/scopus-document-details-page/div/article/div[2]/div[2]/section/div[1]/div[1]/div/h2/span')
                self.driver.implicitly_wait(random.randint(2, 5))
                break
            except TimeoutException:
                try:
                    # didn't find
                    if self.driver.find_element(By.XPATH,
                                                "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]"):
                        print("no results found")
                        return  # no results found
                except:
                    # self.driver.close()
                    # self.driver = webself.driver.Firefox(options=options)
                    return
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_scopus_signed_in(html)
        print("new_metadata", new_metadata)
        if not check_if_right_link(new_metadata, title):
            return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + '_07', html)
        save_link(title, self.driver.current_url)
        new_metadata['Link'] = self.driver.current_url

        self.extract_bibtex_in_scopus_signed_in(title)

        parser = bibtex_parser.Parser()
        bib_data = parser.parse_file(f'D:\\Projet Curation des métadonnées\\Bibtex\\{datetime.today().strftime("%Y-%m-%d")}_{title}_07.bib')

        new_metadata = update_metadata(new_metadata, htmlParser.get_metadata_from_bibtex(bib_data))

        return new_metadata
    
    def extract_bibtex_in_SpringerLink(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="chapter-info-content"]/div/div/ul[1]/li[3]/a')
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="chapter-info-content"]/div/div/ul[1]/li[3]/a')
        web_element.click()

        time.sleep(2)
        self.save_bibtex(title, '03')
        

    def search_in_SpringerLink(self, title):
        # self.driver.get("https://link.springer.com/advanced-search")
        tries = 0
        try:
            # aller sur basic search
            self.driver.get("https://link.springer.com/")
            self.wait_to_load(30, '//*[@id="homepage-search"]')
            self.driver.implicitly_wait(random.randint(2, 5))

            # Insère dans la boîte de texte appropriée le titre de l'article
            web_element = self.driver.find_element(By.XPATH, '//*[@id="homepage-search"]')
            self.driver.implicitly_wait(random.randint(2, 5))
            time.sleep(random.randint(2, 5))
            web_element.send_keys(clean_title(title))

            # Clique pour lancer la recherche
            web_element = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div/div/div[2]/search/form/div/button')
            self.driver.implicitly_wait(random.randint(2, 5))
            web_element.click()

            while tries < 5:
                self.wait_to_load(30, "/html/body/div[4]/div/div[2]/div/div[2]/div[2]/ol/li[1]/div[1]/div/h3/a")
                # Clique pour ouvrir le premier document
                web_element = self.driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/div/div[2]/div[2]/ol/li[" + str(tries+1) + "]/div[1]/div/h3/a")
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()

                # Attend que le document ouvre
                self.wait_to_load(30, '/html/body/div[2]/div[3]/section/div/div/div[5]/h1')
                self.driver.implicitly_wait(random.randint(2, 5))
                break
        except TimeoutException:
            try:
                # didn't find
                if self.driver.find_element(By.XPATH,
                                            "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]"):
                    print("no results found")
                    return  # no results found
            except:
                # self.driver.close()
                # self.driver = webself.driver.Firefox(options=options)
                return
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_springerlink(html)
        print("new_metadata", new_metadata)
        if not check_if_right_link(new_metadata, title):
            return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + '_03', html)
        save_link(title, self.driver.current_url)
        new_metadata['Link'] = self.driver.current_url
        self.extract_bibtex_in_SpringerLink(title)
        return new_metadata
    
    def extract_bibtex_in_ScienceDirect(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="popover-trigger-export-citation-popover"]/button')
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="popover-trigger-export-citation-popover"]/button')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", web_element)
        time.sleep(1)
        web_element.click()
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="popover-content-export-citation-popover"]/div/div/ul/li[3]/form/button')
        web_element.click()

        time.sleep(2)
        self.save_bibtex(title, '02')

    def search_in_ScienceDirect(self, title):
        print("in the searcher")
        # self.driver.get("https://www.sciencedirect.com/search/entry")
        time.sleep(360)
        tries = 0
        try:
            # aller sur basic search
            self.driver.get("https://www.sciencedirect.com/")
            self.wait_to_load(30, '//*[@id="qs"]')
            self.driver.implicitly_wait(random.randint(2, 5))

            # Insère dans la boîte de texte appropriée le titre de l'article
            web_element = self.driver.find_element(By.XPATH, '//*[@id="qs"]')
            self.driver.implicitly_wait(random.randint(2, 5))
            time.sleep(random.randint(2, 5))
            web_element.send_keys(clean_title(title))

            # Clique pour lancer la recherche
            web_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[1]/div/div/form/div[2]/button')
            self.driver.implicitly_wait(random.randint(2, 5))
            web_element.click()

            while tries < 5:
                # self.wait_to_load(30,
                                  # '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2')
                self.wait_to_load(30,
                                  '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2/span/a')
                # Clique pour ouvrir le premier document
                # web_element = self.driver.find_element(By.XPATH,
                #                         '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2')
                web_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2/span/a')
                # web_element = web_element.find_element(By.CLASS_NAME, 'result-list-title-link')
                self.driver.implicitly_wait(random.randint(2, 5))
                web_element.click()

                # Attend que le document ouvre
                self.wait_to_load(30, '/html/body/div[3]/div/div/div/div/div/div[2]/article/h1/span')
                self.driver.implicitly_wait(random.randint(2, 5))
                break
        except TimeoutException:
            try:
                # didn't find
                if self.driver.find_element(By.XPATH,
                                            "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]"):
                    print("no results found")

                    return  # no results found
            except:
                # self.driver.close()
                # self.driver = webself.driver.Firefox(options=options)
                return
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_sciencedirect(html)
        print("new_metadata", new_metadata)
        if not check_if_right_link(new_metadata, title):
            return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + '_02', html)
        save_link(title, self.driver.current_url)
        new_metadata['Link'] = self.driver.current_url
        self.extract_bibtex_in_ScienceDirect(title)
        return new_metadata
    
    
    def extract_bibtex_in_PubMedCentral(self, title, link=None):
        if link:
            self.driver.get(link)
            self.wait_to_load(30, '//*[@id="main-content"]/aside/div/section[2]/ul/li[1]/button')
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="main-content"]/aside/div/section[2]/ul/li[1]/button')
        web_element.click()
        web_element = self.driver.find_element(By.XPATH,
                                               '//*[@id="ui-ncbiexternallink-3"]/div[4]/div/div[2]/div[2]/a')
        web_element.click()

        time.sleep(2)
        self.save_bibtex(title, '08')  # TODO: ici extrait .nbib

    def search_in_PubMedCentral(self, title):
        print("in the searcher")
        # self.driver.get("https://www.sciencedirect.com/search/entry")
        tries = 0
        try:
            # aller sur basic search
            self.driver.get("https://www.ncbi.nlm.nih.gov/pmc")
            self.wait_to_load(30, '//*[@id="pmc-search"]')
            self.driver.implicitly_wait(random.randint(2, 5))

            # Insère dans la boîte de texte appropriée le titre de l'article
            web_element = self.driver.find_element(By.XPATH, '//*[@id="pmc-search"]')
            self.driver.implicitly_wait(random.randint(2, 5))
            time.sleep(random.randint(2, 5))
            web_element.send_keys(clean_title(title))

            # Clique pour lancer la recherche
            web_element = self.driver.find_element(By.XPATH, '/html/body/main/section/div/div[1]/form/div/button')
            self.driver.implicitly_wait(random.randint(2, 5))
            web_element.click()

            while tries < 5:
                # self.wait_to_load(30,
                                  # '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2')
                self.wait_to_load(30,
                                  '/html/body/div[1]/div[1]/form/div[1]/div[5]/div/div[5]/div[1]/div[2]/div[1]/a')
                # Clique pour ouvrir le premier document
                # web_element = self.driver.find_element(By.XPATH,
                #                         '/html/body/div[1]/div/div/div/div/div/div/section/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/ol/li[1]/div/div[2]/h2')
                web_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/form/div[1]/div[5]/div/div[5]/div[' + str(tries+1) + ']/div[2]/div[1]/a')
                # web_element = web_element.find_element(By.CLASS_NAME, 'result-list-title-link')
                self.driver.implicitly_wait(random.randint(2, 5))
                time.sleep(random.randint(2, 5))
                web_element.click()

                # Attend que le document ouvre
                self.wait_to_load(30, '/html/body/main/article/section[3]/div/div[1]/div[1]/h1')
                self.driver.implicitly_wait(random.randint(2, 5))
                time.sleep(random.randint(2, 5))
                html = self.driver.page_source
                new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
                print("new_metadata", new_metadata)
                if check_if_right_link(new_metadata, title):
                    break
                else:
                    tries += 1
                    self.driver.back()
        except TimeoutException:
            try:
                # didn't find
                if self.driver.find_element(By.XPATH,
                                            "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]"):
                    print("no results found")

                    return  # no results found
            except:
                # self.driver.close()
                # self.driver = webself.driver.Firefox(options=options)
                return
        html = self.driver.page_source
        new_metadata = htmlParser.get_metadata_from_html_pub_med_central(html)
        print("new_metadata", new_metadata)
        if not check_if_right_link(new_metadata, title):
            return  # TODO: ajouter plutôt avant le break et changer d'article
        save_extracted_html(title + '_08', html)
        save_link(title, self.driver.current_url)
        new_metadata['Link'] = self.driver.current_url
        return new_metadata


