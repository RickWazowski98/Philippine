import json
import math
import yaml
import requests
import os
import psutil
import pygsheets
import time
import logging
import threading
# from multiprocessing.pool import ThreadPool
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class ThCondosScraper:
    def __init__(self):
        # self.pool = Pool(3)
        self.logger = self.create_logger()
        self.config = self.open_config()
        self.work_sheet = self.open_worksheet()
        self.source_links = self.work_sheet.get_row(2, include_tailing_empty=False)[1:]
        self.global_lock = threading.Lock()

    def create_logger(self):
        logger = logging.getLogger('Thailand Condominums scraper')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s|%(levelname)s|%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def create_driver(self):
        option = Options()
        option.add_argument('--no-sandbox')
        option.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
        return driver

    def selenium_get_source_code(self, page_url):
        self.driver = self.create_driver()
        time.sleep(1)
        self.driver.get(page_url)
        time.sleep(5)
        code = self.driver.page_source
        self.kill_driver(self.driver)
        return code

    def open_config(self):
        with open("config.yml", 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
            return config

    def open_worksheet(self):
        service_file = self.config['googlesheets']['file']
        # sheet_name = 'Copy of Dot Property Data - Real Estate Data (for purposes of solving scraping issues)'
        sheet_1 = 'Thai province URLs (condominums)'
        gc = pygsheets.authorize(service_file=service_file)
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
        # sh = gc.open(sheet_name)
        wks = sh.worksheet_by_title(sheet_1)
        return wks

    def kill_driver(self, driver):
        PROCNAME = "chromedriver"
        driver.quit()
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                self.logger.info('proc by name: {} was kill'.format(proc.name()))
                proc.kill()
            # self.logger.info('Selenium has been killed')

    def parse_data(self, url):
        # self.driver = self.create_driver()
        self.logger.info('Start parsing data from url: {}'.format(url))
        result = []
        code = self.selenium_get_source_code(url)
        soup = BeautifulSoup(code, 'html.parser')
        try:
            number_of_projects = int(soup.find('span', {'id': 'properties_total'}).text)
            self.logger.info(f'Has been found {number_of_projects} projects')
        except (AttributeError, ValueError) as exc:
            self.logger.error(exc)
            number_of_projects = 0
        result.append(number_of_projects)

        if number_of_projects > 0:
            try:
                count_pages = math.ceil(number_of_projects/20)
                self.logger.info(f'Pages count: {count_pages}')
            except Exception as exc:
                self.logger.error(exc)
                count_pages = 0

            project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
            for link in project_links:
                if link['href'] and link['href'] not in result:
                    result.append(link['href'])
            if count_pages > 1:
                for i in range(2, count_pages+1):
                    url_n_page = f'{url}?page={i}'
                    self.logger.info('Parsing data from url: {}'.format(url_n_page))
                    code = self.selenium_get_source_code(url_n_page)
                    soup = BeautifulSoup(code, 'html.parser')
                    project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
                    for link in project_links:
                        if link['href'] and link['href'] not in result:
                            result.append(link['href'])

        self.work_sheet.update_col(self.source_links.index(url)+2, result, row_offset=2)
        self.logger.info('Add {} links'.format(len(result)-1))

    def write_to_json(self, file_name, data):
        with self.global_lock:
            if os.path.exists(file_name):
                # func update data
                with open(file_name, 'r+') as jsonfile:
                    j_data = json.load(jsonfile)
                j_data.append(data)
                with open(file_name, 'w+') as jsonfile:
                    json.dump(j_data, jsonfile, indent=4)
                self.logger.debug('links in json was update')
            else:
                with open(file_name, 'w+') as jsonfile:
                    to_write = []
                    to_write.append(data)
                    json.dump(to_write, jsonfile, indent=4)
                    self.logger.debug('link was insert to json')

    def dump_data_to_json(self, file_name):
        threads = []
        wk_data = self.work_sheet.get_row(3, include_tailing_empty=False)[1:]
        for i in range(len(wk_data)):
            get_total_search_results = self.work_sheet.cell((3, i+2)).value
            for j in range(int(get_total_search_results)):
                cell_data = self.work_sheet.cell((4+j, i+2)).value
                data = {"link": cell_data}
                t = threading.Thread(target=self.write_to_json, args=(file_name, data, ))
                threads.append(t)
                t.start()
                [thread.join() for thread in threads]
                # self.write_to_json(file_name, data)

    def main(self):
        # self.work_sheet.clear(start='B3', end='ZZ9999')
        # for url in self.source_links:
        #     self.parse_data(url)
        self.dump_data_to_json('data/th_condos_source_link_result.json')


if __name__ == "__main__":
    scraper = ThCondosScraper()
    scraper.main()
