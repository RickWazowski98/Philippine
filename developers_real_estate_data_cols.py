import json
import time
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml
import pygsheets
import yaml
import argparse


my_parser = argparse.ArgumentParser()
my_parser.add_argument('-tn')
args = my_parser.parse_args()
input_tab_name = args.tn

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Developers - Real Estate Data - Thailand'

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(input_tab_name)

# wks.update_col(1, [['']*999], row_offset=1)


def clear_columns(tab):
    n_cols = wks.cols
    for n in range(n_cols):
        n_adj = n-2
        n_adj_1 = n-3
        if n in (1,2) or (n>5 and n_adj % 5 == 0) or ((n>5 and n_adj_1 % 5 == 0)):
            wks.update_col(n, [['']*999], row_offset=1)


def scrape_developers_country(tab):
    row_count = 2
    try:
        # start_url = 'https://www.dotproperty.co.th/en/developers'
        start_url = wks.get_value('A1')
        base_url = start_url.replace('developers', '')
        print(f'start main URL: {start_url}')
        r = requests.get(start_url, headers=headers, timeout=20)
        if r.status_code != 200:
            print('status_code', r.status_code, start_url)
            return None
        soup = BeautifulSoup(r.content, 'html.parser')

        alphabets_links_raw = soup.find('div', {'class': 'center alpha-link'}).find_all('a')
        alphabets_links = [x['href'] for x in alphabets_links_raw]
        pos_p = alphabets_links.index('https://www.dotproperty.co.th/en/developers/p#directory')
        alphabets_links_after_p = alphabets_links[pos_p:]
        print(f'alphabets_links_after_p: {alphabets_links_after_p}')

        for alphabets_link in alphabets_links_after_p:
            print(f'-- alphabets_link: {alphabets_link}')
            next_page_url = alphabets_link
            
            while next_page_url != None:
                print(f'ready to request next_page_url {next_page_url}')
                r = requests.get(next_page_url, headers=headers, timeout=20)
                soup = BeautifulSoup(r.content, 'html.parser')

                try:
                    next_page = soup.find('ul', {'class': 'pagination'}).find_all('li')[-1].find('a')['href']
                    next_page_url = f'{alphabets_link.split("#")[0]}{next_page}'
                except:
                    next_page_url = None
                print(f'next_page_url {next_page_url}')
                
                try:
                    developers_raw = soup.find('div', {'class': 'developer-listing'}).find_all('li')
                except:
                    developers_raw = None
                if developers_raw:
                    developers_lst = [{'url': x.find('a')['href'], 'name': x.find('a')['title']} for x in developers_raw]
                    # print(f'developers_lst {developers_lst}')
                    
                    for developer in developers_lst:

                        row_values = []
                        column_count = 7

                        # wks.update_value((row_count, 1), developer.get('url'))
                        # wks.update_value((row_count, 2), developer.get('name'))
                        row_values.append(developer.get('url'))
                        row_values.append(developer.get('name'))
                        row_values += ['','','','']
                        next_page_proj_url = developer.get('url')
                        while next_page_proj_url != None:
                            r = requests.get(next_page_proj_url, headers=headers, timeout=20)
                            soup = BeautifulSoup(r.content, 'html.parser')
                            
                            try:
                                projects_raw = soup.find('div', {'id': 'search-results'}).find_all('article')
                            except:
                                projects_raw = None
                            # print(f'----projects_raw {projects_raw}')
                            if projects_raw:
                                projects_lst = []

                                for project_raw in projects_raw:
                                    name = project_raw.find('h4').text.strip() if project_raw.find('h4') else project_raw.find('a')['title']
                                    try:
                                        type_proj = project_raw.find('a')['href'].split(f'{base_url}')[1].split('/')[0]
                                    except:
                                        type_proj = ''
                                    projects_lst.append({
                                        'name': name,
                                        'type': type_proj,
                                    })
                                # print(f'projects_lst {projects_lst}')

                                
                                for proj in projects_lst:
                                    # res.append({
                                    #     'developer URL': developer.get('url'),
                                    #     'developer name': developer.get('name'),
                                    #     'project name': proj.get('name'),
                                    #     'property type': proj.get('type'),
                                    # })
                                    print({
                                        'developer URL': developer.get('url'),
                                        'developer name': developer.get('name'),
                                        'project name': proj.get('name'),
                                        'property type': proj.get('type'),
                                    })
                                    # wks.update_value((row_count, column_count), proj.get('name'))
                                    # wks.update_value((row_count, column_count+1), proj.get('type'))
                                    row_values.append(proj.get('name'))
                                    row_values.append(proj.get('type'))

                                    row_values += ['','','']

                                    column_count+=5

                            
                                try:
                                    next_page_proj = soup.find('ul', {'class': 'pagination'}).find_all('li')[-1].find('a')['href']
                                    next_page_proj_url = f"{developer.get('url')}{next_page_proj}"
                                except:
                                    next_page_proj_url = None

                        wks.update_row(row_count, row_values)
                        row_count+=1
                

                
        
    
    except Exception as e:
        print(f'scrape_developers_country: {tab} {e}')
        return None


if __name__ == "__main__":
    # clear_columns(input_tab_name)
    wks.clear(start='A2')

    scrape_developers_country(input_tab_name)
    # print(wks.cols)