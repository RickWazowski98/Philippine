"""
list: Thai province URLs (condominums)
and similar
Get URLs from Row 2 and return Number of project
plus all projects urls in each column
"""

import json
import math
import yaml
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml
import pygsheets
from multiprocessing import Pool
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import os
import psutil

HEADERS = {
    "authority": "www.dotproperty.co.th",
    "method": "GET",
    "path": "/en/condos/all/Chiang-Mai",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br, utf-8",
    "accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5,en-US;q=0.4",
    "cache-control": "max-age=0",
    "cookie": '__cfduid=ddf72a44bcf4e7435aef723f195082cef1611242242; user_language=eyJpdiI6Ik4ySkh4a05TKzZod2NyYUtIcHgzb0E9PSIsInZhbHVlIjoiMktxMHFaXC9BUTBCQ0lGZnZCM0p3ZkE9PSIsIm1hYyI6IjEyYzg5NGI4ZTk1NmU5NjQxNGNkMDAxMjZmNjQ1OTgyZjNkZjkxMWIyODYyODM4ODE3YjFjNTM4ZjI1MDBkMWUifQ%3D%3D; dot_property_group_idu=eyJpdiI6IjBFTm5wajdUaThTd0lCQWFmRzJTQVE9PSIsInZhbHVlIjoiV1BpWnRmdGVWTm84ZitXXC82VVhlUzZOYTFWUGxVYmVZbytIaG9hdTJ4cnpRV0djNG9abEFlUGlOVjg4bzkyZ1AiLCJtYWMiOiJiYTc4ZWIwNGQ0YmFiNjYyYmU1MzU3YmZiOWI3YjcyZGNiZDVhNTMxNzE4YWUwMjEzYjI5NGZkODE1YjdmYTRlIn0%3D; _ga=GA1.3.1597338887.1611242251; _gid=GA1.3.1484661411.1611242251; _fbp=fb.2.1611242252081.1818976429; _hjid=69916b82-dc49-49cb-8ff4-d607906187b9; XSRF-TOKEN=eyJpdiI6ImxDUlI3cUFTYWx6VXRQOHZiY3hmSmc9PSIsInZhbHVlIjoielpIZWd1bndsOXB2OFY0TExiRUhnaXJhNlJyZXpLdDUySEtqOGRJVlZYd3UyNzA0RTFwajRQRWRTYTdtVklTcTFhUE53QkxvTTJVTnU5akpTUzZOeVE9PSIsIm1hYyI6ImVmMmZlZTVkNjllMDRmOGY5YjVkZTljMjk1NjAxZTg5Y2ZkY2RkNTdiNGM5YzdlYjU0YjA4NGNkMWY3NjQ4NDYifQ%3D%3D; dot_property_group=eyJpdiI6Ijd4NG1GUXBmMkRYc3ltQkZRcWNjNmc9PSIsInZhbHVlIjoiWHUyUnBuYUpwUjFiR1hiUE1sVFhLYUtjMkl2VUhkWTYwYTI5a2t3WEcxQTlKdkErMEdBdXhwWUN0SlJsNnkxcTJkZkttZXIxME1PWkxIR1JKMFM4emc9PSIsIm1hYyI6ImI3NDA4NTE3MDQ1ZDM0Y2IzNWUwMTJlMGQ4ZGNjM2VmODI5MTU2M2E5YWJjMDU0MzY2MjNlODc5ODYwNmRmNjcifQ%3D%3D; _gali=content',
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": '?0',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Copy of Dot Property Data - Real Estate Data (for purposes of solving scraping issues)' # config['googlesheets']['name']
SHEET1 = 'Thai province URLs (condominums)' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
# sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET1)

# TODO: Backup save?
wks.clear(start='B3', end='ZZ9999')
url_input_list = wks.get_row(2, include_tailing_empty=False)[1:]
links_to_save = []
column_i = 2
# print(url_input_list)

option = Options()
option.add_argument('--no-sandbox')
option.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)


def stop_selenium():
    PROCNAME = "chromedriver"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()


def get_data_projects(url):
    global column_i
    global driver
    global links_to_save
    """links_to_save = []
    # result = []
    for url in urls:"""
    result = []
    print(url)
    HEADERS["path"] = url.split('/')[-4] + '/' + url.split('/')[-3] + '/' + url.split('/')[-2] + '/' + url.split('/')[-1]
    time.sleep(0.05)
    driver.get(url)
    time.sleep(5)
    code = driver.page_source
    """print(code)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        print('status_code', r.status_code)
        return None"""
    soup = BeautifulSoup(code, 'html.parser')
    # print(soup)

    """number_of_projects = soup
    print(number_of_projects)
    # except:
    #     number_of_projects = 0
    # print('number_of_projects', number_of_projects)
    result.append(number_of_projects)"""
    try:
        number_of_projects = int(soup.find('span', {'id': 'properties_total'}).text)
    except Exception:
        number_of_projects = 0
    print('number_of_projects', number_of_projects)
    result.append(number_of_projects)

    if number_of_projects > 0:
        try:
            count_pages = math.ceil(number_of_projects/20)
        except Exception:
            count_pages = 0
        print('count_pages', count_pages)
        project_links = soup.find('div', {'id': 'search-results'}).find_all('a')

        for link in project_links:
            if link['href'] and link['href'] not in result:
                result.append(link['href'])
                links_to_save.append(link['href'])
        if count_pages > 1:
            for i in range(2, count_pages+1):
                url_n_page = f"{url}?page={i}"
                print(url_n_page)
                # https://www.dotproperty.co.th/en/condos/all/Chiang-Mai?page=2
                time.sleep(5)
                driver.get(url_n_page)
                """if r.status_code != 200:
                    print('status_code', r.status_code)
                    return None"""
                    # TODO: add attempts here and everywhere in project
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
                for link in project_links:
                    if link['href'] and link['href'] not in result:
                        result.append(link['href'])
                        links_to_save.append(link['href'])

    # print(result, len(result))
    # post here
    wks.update_col(column_i, result, row_offset=2)
    column_i += 1
    # rturn result
    # TODO: Save to file cont 


file_object = open('data/links_th_condo_thai_prov.json', 'w') # Thai province URLs (condominums)
json.dump(links_to_save, file_object, indent=4)
print(len(links_to_save))


if __name__ == "__main__":
    # get_data_projects('https://www.dotproperty.co.th/en/condos/all/Chiang-Mai')
    pool = Pool(4)
    result = pool.map(get_data_projects, url_input_list)
    pool.terminate()
    pool.join()
    driver.quit()
    stop_selenium()
