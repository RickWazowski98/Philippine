import json
import logging
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml
import pygsheets
import yaml

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = 'Thai province URLs (condominums)' # config['googlesheets']['sheet1']
SHEET2 = 'Bangkok district URLs (condominiums)'


gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks1 = sh.worksheet_by_title(SHEET1)
wks2 = sh.worksheet_by_title(SHEET2)


def get_data_projects(urls):
    result = []
    for url in urls:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        soup = BeautifulSoup(r.content, 'html.parser')

        project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
        
        for link in project_links:
            if link['href'] and link['href'] not in result:
                result.append(link['href'])
    
    return result


if __name__ == "__main__":
    """
    DEPRECATED: 5 Apr, now we will read it from 2 tabs: Thai province URLs (condominums), Bangkok district URLs (condominiums)
    urls = []
    for i in range(1, 51):
        urls.append(f"https://www.dotproperty.co.th/en/condos/all?page={i}")
    print(urls)

    result = get_data_projects(urls)


    # TODO: other pages
    """

    links1 = wks1.get_values(start='B4', end='ZZ1000', include_tailing_empty=False,returnas='matrix')
    links2 = wks2.get_values(start='B4', end='ZZ1000', include_tailing_empty=False,returnas='matrix')

    links1_l = [item for sublist in links1 for item in sublist if item != '']
    links2_l = [item for sublist in links2 for item in sublist if item != '']

    print(len(links1_l), len(links2_l))
    result = links1_l + links2_l
    print(len(result))

    
    file_object = open('data/links_th_condo.json', 'w')
    json.dump(result, file_object, indent=4)