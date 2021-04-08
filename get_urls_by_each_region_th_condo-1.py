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
from proxy_config import get_proxy


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = 'Thai province URLs (condominums)' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1BECEt_FXEofM-HvKM00R660PIbbaYEN5uCRPp73QI3I/edit?ts=6065beee#gid=589501000')
# sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET1)

# TODO: Backup save?
wks.clear(start='B3', end='ZZ9999')
url_input_list = wks.get_row(2, include_tailing_empty=False)[1:]
# print(url_input_list)



def get_data_projects(urls):
    links_to_save = []
    column_i = 2
    # result = []
    for url in urls:
        result = []
        print(url)
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.proxies.update(get_proxy())
        #r = session.get(url, headers=headers_xml, timeout=30)
        r = session.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        soup = BeautifulSoup(r.content, 'html.parser')
        
        try:
            number_of_projects = int(soup.find('span', {'id': 'properties_total'}).text)
        except:
            number_of_projects = 0
        print('number_of_projects', number_of_projects)
        result.append(number_of_projects)
        
        if number_of_projects > 0:
            try:
                count_pages = math.ceil(number_of_projects/20)
            except:
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
                    r = session.get(url_n_page, headers=headers, timeout=20)
                    if r.status_code != 200:
                        print('status_code', r.status_code)
                        return None
                        # TODO: add attempts here and everywhere in project
                    soup = BeautifulSoup(r.content, 'html.parser')

                    project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
                    for link in project_links:
                        if link['href'] and link['href'] not in result:
                            result.append(link['href'])
                            links_to_save.append(link['href'])
    
        print(result, len(result))
        # post here
        wks.update_col(column_i, result, row_offset=2)

        column_i += 1
    # return result

    # TODO: Save to file cont 
    file_object = open('data/links_th_condo_thai_prov.json', 'w') # Thai province URLs (condominums)
    json.dump(links_to_save, file_object, indent=4)
    print(len(links_to_save))


if __name__ == "__main__":
    result = get_data_projects(url_input_list)