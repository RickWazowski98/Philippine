import logging
import json
import time
import requests
import pygsheets
import yaml
from bs4 import BeautifulSoup
from helpers import headers, headers_xml


"""
Read column 'Area  URL' in 'Projects tab for Sergei'
and scrape 'Area's median sale price/sqm at earliest project's month'
month = 'Earliest month' (Q column)

STORE IT IN FILE ONCE AND THEN ONLY LOAD THEM
"""


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = 'Thailand houses' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET1)

def resolve_graph_link(url_str):
    try:
        provinces_cities_areas = url_str.split('houses-for-rent/')[1]
        url = 'https://www.dotproperty.co.th/en/market-stats/search-page/condo/?key={}&priceType=sqmSale&pageType=rent'.format(provinces_cities_areas)
        print(url)
        return url
    except:
        print('logging error in resolve_graph_link()')
        return None

def get_data_graph(url, month_target_1, month_target_2):
    try:
        r = requests.get(url, headers=headers_xml, timeout=35)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        data = r.json()['msg']
        
        try:
            median_sale_prices_sqm = data.split("'sqmSale': {")[1].split("data: [")[1].split("],")[0].split(',')
            months = data.split("labels: [")[1].split("],")[0].split(",")
            months = [x.replace('"','') for x in months]
            print(months)

            target_month_position = months.index(month_target_1)
            print(target_month_position)

            result1 = median_sale_prices_sqm[target_month_position]
            
        except:
            result1 = ''
        
        try:
            median_rent_prices_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')
            target_month_position_2 = months.index(month_target_2)

            result2 = median_rent_prices_sqm[target_month_position_2]
        except:
            result2 = ''
        
        print('RETURN: {}; {}'.format(result1, result2))
        """
        The data in these columns should be interchanged, so the 3 digit numbers in here and the more than 5 -6 digit numbers in column CC
        """
        return [result2, result1]
    
    except:
        return ['', '']

if __name__ == "__main__":

    months_target_1 = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_month_1']), include_tailing_empty=False)[1:]
    print(months_target_1)
    months_target_2 = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_month_2']), include_tailing_empty=False)[1:]
    print(months_target_2)
    URLs_targets = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_URLs_2']), include_tailing_empty=False)[1:]
    print(URLs_targets)
    data_for_column_AO = []

    j = 1
    for month_1, month_2, url in zip(months_target_1, months_target_2, URLs_targets):
        print(f"{j}/{len(URLs_targets)}")
        print('-- {} -- {} -- {}'.format(month_1, month_2, url))
        if month_1 != '' or month_2 != '':
            url_graph = resolve_graph_link(url)
            if url_graph:
                data_for_column_AO.append(get_data_graph(url_graph, month_1, month_2))
            else:
                data_for_column_AO.append(['', ''])
        else:
            data_for_column_AO.append(['', ''])
        
        j += 1
        # time.sleep(1)
    print('========')
    print(data_for_column_AO)

    if len(data_for_column_AO) != 0:
        wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_5'], values=data_for_column_AO)
    else:
        print('Nothing to load')