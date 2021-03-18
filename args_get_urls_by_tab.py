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
import argparse
from loguru import logger
import os
import sys
from proxy_config import get_proxy


my_parser = argparse.ArgumentParser()
my_parser.add_argument('-tn')
args = my_parser.parse_args()
input_tab_name = args.tn

basedir = os.path.dirname(__file__)
logfile = os.path.join(basedir, "logs", f"{input_tab_name.replace(' ','_').lower()}_args_get_urls_by_tab.log")
logger.add(logfile, rotation="10 MB")
logger.debug(f"Started {input_tab_name}")

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

mapping_config = config['mappings_tabs'][input_tab_name]

SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['mappings_tabs']['sheet_name'] # 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = mapping_config['tab_name'] # 'Thai province URLs (houses)' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
# sh = gc.open(SHEET_NAME)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
wks = sh.worksheet_by_title(SHEET1)

# TODO: Backup save?

url_main_A1 = wks.get_value('A1')
logger.debug(SHEET1, url_main_A1)
logger.debug(f"data/{mapping_config['file_proj_urls']}.json")
links_to_save = []


def get_data_projects(url):
    # links_to_save = []
    # result = []
    result = []
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.proxies.update(get_proxy())
    r = session.get(url, headers=headers, timeout=20, allow_redirects=True)
    if r.status_code == 503:
        s = BeautifulSoup(r.text, 'html.parser')
        form = s.find('form', {'class': 'challenge-form'})
        action = form.get('action')
        r_d = form.find('input', {'name': 'r'})
        jschl_vc = form.find('input', {'name': 'jschl_vc'})
        pass_v = form.find('input', {'name': 'pass'})
        print(s)
        # r = session.post('https://www.dotproperty.id' + action, data={'action': action, 'r': r_d, 'jschl_vc': jschl_vc, 'pass': pass_v})
        #print(r.text)
    if r.status_code != 200:
        logger.debug('status_code {}'.format(r.status_code))
        return None
    soup = BeautifulSoup(r.content, 'html.parser')
    try:
        number_of_projects = int(soup.find('span', {'id': 'properties_total'}).text.replace(',', ''))
        print(number_of_projects)
    except:
        number_of_projects = 0
    logger.debug('number_of_projects {}'.format(number_of_projects))
    result.append(number_of_projects)
    
    if number_of_projects > 0:
        try:
            count_pages = math.ceil(number_of_projects/20)
        except:
            count_pages = 0
        logger.debug('count_pages {}'.format(count_pages))

        project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
        
        for link in project_links:
            if link['href'] and link['href'] not in result:
                result.append(link['href'])
                links_to_save.append(link['href'])

        if count_pages > 1:
            for i in range(2, count_pages+1):
                logger.debug('page {}'.format(i))
                url_n_page = f"{url}?page={i}"
                logger.debug(url_n_page)
                r = requests.get(url_n_page, headers=headers, timeout=20)
                if r.status_code != 200:
                    logger.debug('status_code', r.status_code)
                    return None
                    # TODO: add attempts here and everywhere in project
                soup = BeautifulSoup(r.content, 'html.parser')

                project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
                for link in project_links:
                    if link['href'] and link['href'] not in result:
                        result.append(link['href'])
                        links_to_save.append(link['href'])
    
        # logger.debug(result, len(result))
        # post here
        # wks.update_col(column_i, result, row_offset=2)

    # return result

    # TODO: Save to file cont 
    # if input_tab_name == "Vietnam townhouses":
    #     formated_links = []
    #     for link in links_to_save:
    #         format_link = str(link).replace('en/','')
    #         formated_links.append(format_link)
    #     file_object = open(f"data/{mapping_config['file_proj_urls']}.json", 'w')
    #     json.dump(formated_links, file_object, indent=4)
    #     logger.debug(len(formated_links))
    # else:


#file_object = open(f"data/{mapping_config['file_proj_urls']}.json", 'w')
#json.dump(links_to_save, file_object, indent=4)
#logger.debug(len(links_to_save))


if __name__ == "__main__":
    result = get_data_projects(url_main_A1)
    file_object = open(f"data/{mapping_config['file_proj_urls']}.json", 'w')
    json.dump(links_to_save, file_object, indent=4)
    logger.debug(len(links_to_save))
    