"""
10mins after your script is done scraping the project data in a certain tab (and thus also 10mins after it added the identifier to column AZ in that same tab), it can start with scraping the location data in that same tab
"""
import logging
import json
import time
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml
import pygsheets
import yaml


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

# time.sleep(60*41)

SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = 'Thailand condominiums' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET1)

"""
Remember: before starting with scraping the location data, you would need to create a copy of the created URLs (in column BJ) and paste their text values in column BK.
TODO:
Instead of copying URLs in column BJ and pasting them in column BK, copy locations in column BI and past them in column BJ
"""

result = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_locations_1']), include_tailing_empty=False)[1:]
# file_object = open('data/provinces-cities-areas_urls_th_condo.json', 'w')
# json.dump(result, file_object, indent=4)


wks.update_col(int(config['googlesheets']['dt_sheets_copy_paste_location_urls']), result, row_offset=1)

time.sleep(30) # 30s ur safe I'd say

result_urls = wks.get_col(int(config['googlesheets']['dt_sheets_location_urls']), include_tailing_empty=False)[1:]
file_object = open('data/provinces-cities-areas_urls_th_condo.json', 'w')
json.dump(result_urls, file_object, indent=4)


def resolve_graph_link(url_str):
    provinces_cities_areas = url_str.split('condos-for-rent/')[1]
    url = 'https://www.dotproperty.co.th/en/market-stats/search-page/condo/?key={}&priceType=sqmSale&pageType=rent'.format(provinces_cities_areas)
    print(url)
    return url

def get_data_graph(url):
    r = requests.get(url, headers=headers_xml, timeout=30)
    if r.status_code != 200:
        print('status_code', r.status_code)
        return None
    data = r.json()['msg']
    # filname to save temp for dev
    """
    f_name = url.split('/')[-1]
    with open(f_name, 'w') as output:
        output.write(data)
    """
    
    try:
        median_rent_price_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        median_rent_price_sqm = ''
    try:
        median_sale_price_sqm = data.split("'sqmSale': {")[1].split("data: [")[1].split("],")[0].split(',')[-1]
    except:
        median_sale_price_sqm = ''
    try:
        earliest_median_sale_prices_sqm = data.split("'sqmSale': {")[1].split("data: [")[1].split("],")[0].split(',')
    except:
        earliest_median_sale_prices_sqm = ''
    try:
        earliest_median_rent_prices_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')
    except:
        earliest_median_rent_prices_sqm = ''

    try:
        earliest_median_sale_price_sqm = ''
        if earliest_median_sale_prices_sqm == '':
            raise Exception
        month_num=0
        for price in earliest_median_sale_prices_sqm:
            month_num+=1
            if price!='':
                earliest_median_sale_price_sqm = price
                break
        
        months = data.split("labels: [")[1].split("],")[0].split(",")
        earliest_month = months[month_num-1].replace('"','')
    except:
        earliest_month = ''

    try:
        earliest_median_rent_price_sqm = ''
        if earliest_median_rent_prices_sqm == '':
            raise Exception
        month_num=0
        for price in earliest_median_rent_prices_sqm:
            month_num+=1
            if price!='':
                earliest_median_rent_price_sqm = price
                break
        
        months = data.split("labels: [")[1].split("],")[0].split(",")
        if earliest_median_rent_price_sqm == '':
            earliest_month_1 = ''
        else:
            earliest_month_1 = months[month_num-1].replace('"','')
    except:
        earliest_month_1 = ''
    
    try:
        part_2_1 = data.split("htmlDecode('Median sale price")[1].split("data: [")[1].split("],")[0].split(',')[-1]
    except:
        part_2_1 = ''
    try:
        part_2_2 = data.split("htmlDecode('Median sale price'\n")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_2 = ''
    try:
        part_2_3 = data.split("htmlDecode('Median rent price")[1].split("type: 'bar'")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_3 = ''
    # print(data.split("htmlDecode('Median rent price'\n")[1].split("data:[")[1])
    try:
        part_2_4 = data.split("htmlDecode('Median rent price'\n")[1].split("data:[")[1].split("],")[0].split(',')[-1]
        
    except:
        part_2_4 = ''
    try:
        part_2_5 = data.split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_5 = ''


    # return median_rent_price_sqm, earliest_median_sale_price_sqm, earliest_month, median_sale_price_sqm, earliest_median_rent_price_sqm, earliest_month_1, '', part_2_1, part_2_2, part_2_3, part_2_4,'',part_2_5
    return part_2_4, median_rent_price_sqm, part_2_3, earliest_median_rent_price_sqm, earliest_month_1, part_2_5, part_2_2, median_sale_price_sqm, part_2_1, earliest_median_sale_price_sqm, earliest_month

if __name__ == "__main__":
    file_object = open('data/provinces-cities-areas_urls_th_condo.json', 'r')
    links = json.load(file_object)
    result = []

    j = 1
    for link in links:
        print(link, f"{j}/{len(links)}")
        result_project = get_data_graph(resolve_graph_link(link))
        result.append(result_project)
        
        j += 1
        # time.sleep(1)
    
    file_object = open('data/provinces-cities-areas_data_th_condo.json', 'w')
    json.dump(result, file_object, indent=4)

    # LOAD
    file_object = open('data/provinces-cities-areas_data_th_condo.json', 'r')
    provinces_data = json.load(file_object)

    wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_4'], values=provinces_data)