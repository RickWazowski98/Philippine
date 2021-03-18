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
logfile = os.path.join(basedir, "logs", f"{input_tab_name.replace(' ','_').lower()}_args_dt_dotproperty-2.log")
logger.add(logfile, rotation="10 MB")
logger.debug(f"Started {input_tab_name}")

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)
mapping_config = config['mappings_tabs'][input_tab_name]


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['mappings_tabs']['sheet_name']
SHEET1 = mapping_config['tab_name']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
# sh = gc.open(SHEET_NAME)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
wks = sh.worksheet_by_title(SHEET1)

"""
Remember: before starting with scraping the location data, you would need to create a copy of the created URLs (in column BJ) and paste their text values in column BK.
TODO:
Instead of copying URLs in column BJ and pasting them in column BK, copy locations in column BI and past them in column BJ
"""

result = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_locations_1']), include_tailing_empty=False)[1:]

#print(result)
wks.update_col(int(config['googlesheets']['dt_sheets_copy_paste_location_urls']), result, row_offset=1)

time.sleep(30) # 30s ur safe I'd say

result_urls = wks.get_col(int(config['googlesheets']['dt_sheets_location_urls']), include_tailing_empty=False)[1:]
file_object = open(f"data/{mapping_config['file_data_urls_provinces']}.json", 'w')
json.dump(result_urls, file_object, indent=4)


def resolve_graph_link(url_str):
    # TODO: all cases and try-except-None
    # TODO: add domain in config
    logger.debug(url_str)
    provinces_cities_areas = None
    if '/houses-for-rent/' in url_str:
        provinces_cities_areas = url_str.split('/houses-for-rent/')[1]
    if '/townhouses-for-rent/' in url_str:
        provinces_cities_areas = url_str.split('/townhouses-for-rent/')[1]
    if '/townhouses-for-sale/' in url_str:
        provinces_cities_areas = url_str.split('/townhouses-for-sale/')[1]
    if '/condos-for-rent/' in url_str:
        provinces_cities_areas = url_str.split('/condos-for-rent/')[1]
    if '/condos-for-sale/' in url_str:
        provinces_cities_areas = url_str.split('/condos-for-sale/')[1]
    if '/houses-for-sale/' in url_str:
        provinces_cities_areas = url_str.split('/houses-for-sale/')[1]
    if provinces_cities_areas != None:
        if input_tab_name == "Vietnam townhouses":
            url = f"https://www.{mapping_config['domain']}/market-stats/search-page/condo/?key={provinces_cities_areas}&priceType=sqmSale&pageType=rent"
            logger.debug(url)
            return url
        else:
            url = f"https://www.{mapping_config['domain']}/en/market-stats/search-page/condo/?key={provinces_cities_areas}&priceType=sqmSale&pageType=rent"
            logger.debug(url)
            return url
    logger.debug('WARNING: cant resolve graph_link')
    return ''


def get_data_graph(url):
    logger.debug(url)
    if url is None:
        logger.debug("url is NONE")
        return
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.proxies.update(get_proxy())
    r = session.get(url, headers=headers_xml, timeout=30)
    if r.status_code != 200:
        logger.debug('status_code {}'.format(r.status_code))
        return None
    data = r.json()['msg']
    # filname to save temp for dev
    """
    f_name = url.split('/')[-1]
    with open(f_name, 'w') as output:
        output.write(data)
    """
    #print(data)
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
    # logger.debug(data.split("htmlDecode('Median rent price'\n")[1].split("data:[")[1])
    try:
        part_2_4 = data.split("htmlDecode('Median rent price'\n")[1].split("data:[")[1].split("],")[0].split(',')[-1]
        
    except:
        part_2_4 = ''
    try:
        part_2_5 = data.split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_5 = ''


    # return median_rent_price_sqm, earliest_median_sale_price_sqm, earliest_month, median_sale_price_sqm, earliest_median_rent_price_sqm, earliest_month_1, '', part_2_1, part_2_2, part_2_3, part_2_4,'',part_2_5
    logger.debug(part_2_4, median_rent_price_sqm, part_2_3, earliest_median_rent_price_sqm, earliest_month_1, part_2_5, part_2_2, median_sale_price_sqm, part_2_1, earliest_median_sale_price_sqm, earliest_month)
    return part_2_4, median_rent_price_sqm, part_2_3, earliest_median_rent_price_sqm, earliest_month_1, part_2_5, part_2_2, median_sale_price_sqm, part_2_1, earliest_median_sale_price_sqm, earliest_month

if __name__ == "__main__":
    file_object = open(f"data/{mapping_config['file_data_urls_provinces']}.json", 'r')
    links = json.load(file_object)
    result = []

    j = 1
    resolved_links = []
    for link in links:
        if input_tab_name == "Vietnam townhouses":
            r = resolve_graph_link(link.replace('en/', ''))
        else:
            r = resolve_graph_link(link)
        resolved_links.append(r)
    for link in resolved_links:
        if link is not None and link != '':
            logger.debug(link, f"{j}/{len(resolved_links)}")
            result_project = get_data_graph(link)
            result.append(result_project)
        
            j += 1
        # time.sleep(1)
    #print(result)
    file_object = open(f"data/{mapping_config['file_data_provinces']}.json", 'w')
    json.dump(result, file_object, indent=4)

    # LOAD
    file_object = open(f"data/{mapping_config['file_data_provinces']}.json", 'r')
    provinces_data = json.load(file_object)
    #print(provinces_data)

    wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_4'], values=provinces_data)