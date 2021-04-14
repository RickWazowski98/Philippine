import logging
import json
import time
import requests
import pygsheets
import yaml
from bs4 import BeautifulSoup
from helpers import headers, headers_xml
import argparse
from loguru import logger
import os
import sys
from multiprocessing.pool import ThreadPool
from proxy_config import get_proxy


"""
Read column 'Area  URL' in 'Projects tab for Sergei'
and scrape 'Area's median sale price/sqm at earliest project's month'
month = 'Earliest month' (Q column)

STORE IT IN FILE ONCE AND THEN ONLY LOAD THEM
"""

my_parser = argparse.ArgumentParser()
my_parser.add_argument('-tn')
args = my_parser.parse_args()
input_tab_name = args.tn

basedir = os.path.dirname(__file__)
logfile = os.path.join(basedir, "logs", "{}_args_dt_dotproperty-mix.log".format(input_tab_name.replace(' ','_').lower()))
logger.add(logfile, rotation="10 MB")
logger.debug("Started {}".format(input_tab_name))

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)
mapping_config = config['mappings_tabs'][input_tab_name]


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['mappings_tabs']['sheet_name']
SHEET1 = mapping_config['tab_name']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
# sh = gc.open(SHEET_NAME)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1BECEt_FXEofM-HvKM00R660PIbbaYEN5uCRPp73QI3I/edit?ts=6065beee#gid=589501000')
wks = sh.worksheet_by_title(SHEET1)

def resolve_graph_link(url_str):
    # TODO: all cases and try-except-None
    # TODO: add domain in config
    if input_tab_name == "Vietnam townhouses":
        try:
            print(url_str)
            print(url_str.split('/townhouses-for-sale/')[1])
            if '/townhouses-for-rent/' in url_str:
                provinces_cities_areas = url_str.split('/townhouses-for-rent/')[1]
                url = "https://www.{}/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/townhouses-for-sale/' in url_str:
                provinces_cities_areas = url_str.split('/townhouses-for-sale/')[1]
                url = "https://www.{}/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            logger.debug("Resolve url: {} - > \n\t {}".format(url_str, url))
            return url
        except:
            logger.debug('logging error in resolve_graph_link()')
            return ''
    else:
        try:
            #print(url_str)
            if '/houses-for-rent/' in url_str:
                provinces_cities_areas = url_str.split('/houses-for-rent/')[1]
                url = "https://www.{}/en/market-stats/search-page/house/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/houses-for-sale/' in url_str:
                provinces_cities_areas = url_str.split('/houses-for-sale/')[1]
                url = "https://www.{}/en/market-stats/search-page/house/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/townhouses-for-rent/' in url_str:
                provinces_cities_areas = url_str.split('/townhouses-for-rent/')[1]
                url = "https://www.{}/en/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/townhouses-for-sale/' in url_str:
                provinces_cities_areas = url_str.split('/townhouses-for-sale/')[1]
                url = "https://www.{}/en/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/condos-for-rent/' in url_str:
                provinces_cities_areas = url_str.split('/condos-for-rent/')[1]
                url = "https://www.{}/en/market-stats/search-page/condo/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if 'condos-for-sale/' in url_str:
                provinces_cities_areas = url_str.split('/condos-for-sale/')[1]
                url = "https://www.{}/en/market-stats/search-page/condo/?key={}&priceType=sqmRent&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/townhouse-for-rent/' in url_str:
                provinces_cities_areas = url_str.split('/townhouse-for-rent/')[1]
                url = "https://www.{}/en/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            if '/townhouse-for-sale/' in url_str:
                provinces_cities_areas = url_str.split('/townhouse-for-sale/')[1]
                url = "https://www.{}/en/market-stats/search-page/townhouse/?key={}&priceType=sqmSale&pageType=rent".format(mapping_config['domain'], provinces_cities_areas)
            logger.debug("Resolve url: {} - > \n\t {}".format(url_str, url))
            return url
        except Exception as err:
            logger.debug(err)
            logger.debug('logging error in resolve_graph_link()')
            return ''


def get_data_graph(url, month_target_1, month_target_2):
    """
    13.07 add:
    Area's median sale price/sqm 1 year ago, Area's median sale price/sqm 8 months ago
    """
    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.proxies.update(get_proxy())
        # r = session.get(url, headers=headers_xml, timeout=30)
        # print(url)
        r = session.get(url, headers=headers_xml, timeout=35)
        if r.status_code != 200:
            logger.debug('status_code', r.status_code)
            return None
        data = r.json()['msg']
        # print(r.text)
        
        try:
            median_sale_prices_sqm = data.split("'sqmSale': {")[1].split("data: [")[1].split("],")[0].split(',')
        except:
            median_sale_prices_sqm = []

        try:
            months = data.split("labels: [")[1].split("],")[0].split(",")
            months = [x.replace('"','') for x in months]
            logger.debug("months {}".format(len(months)))

            target_month_position = months.index(month_target_1)
            logger.debug(target_month_position)

            result1 = median_sale_prices_sqm[target_month_position]
            
        except:
            result1 = ''
        
        try:
            median_rent_prices_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')
            target_month_position_2 = months.index(month_target_2)

            result2 = median_rent_prices_sqm[target_month_position_2]
        except:
            result2 = ''
        
        try:
            area_median_sale_price_sqm_1_year_ago = median_sale_prices_sqm[-13:-12][0]
            #print(area_median_sale_price_sqm_1_year_ago)
        except:
            area_median_sale_price_sqm_1_year_ago = ''
        try:
            area_median_sale_price_sqm_8_month_ago = median_sale_prices_sqm[-9:-8][0]
            #print(area_median_sale_price_sqm_8_month_ago)
        except:
            area_median_sale_price_sqm_8_month_ago = ''

        #try:
        #    proj_media_sale_price = \
        #        data.split('borderColor: "rgb(215, 219, 221)",')[1].split("label: htmlDecode('Average enquiry sale price/sqm.'")[0].replace("data: [", "").replace("],", "").replace("\n", "").replace("\t", "").split(',')
        #    proj_media_sale_price = [d.strip(" ") for d in proj_media_sale_price]
        #    # print(proj_media_sale_price)
        #except:
        #    proj_media_sale_price = []
#
        #try:
        #    proj_media_sale_price_sqm_1_year_ago = proj_media_sale_price[-12]
        #except:
        #    proj_media_sale_price_sqm_1_year_ago = ''
#
        #try:
        #    proj_media_sale_price_sqm_8_month_ago = proj_media_sale_price[-8]
        #except:
        #    proj_media_sale_price_sqm_8_month_ago = ''
        
        logger.debug(f'{r.url}:\n\t Result: {result1}; {result2}; {area_median_sale_price_sqm_1_year_ago}; {area_median_sale_price_sqm_8_month_ago};')  # {proj_media_sale_price_sqm_1_year_ago}; {proj_media_sale_price_sqm_8_month_ago}')
        """
        The data in these columns should be interchanged, so the 3 digit numbers in here and the more than 5 -6 digit numbers in column CC
        """
        return result2, result1, area_median_sale_price_sqm_1_year_ago, area_median_sale_price_sqm_8_month_ago, # proj_media_sale_price_sqm_1_year_ago, proj_media_sale_price_sqm_8_month_ago
    
    except:
        return '', '', '', ''

if __name__ == "__main__":
    months_target_1 = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_month_1']), include_tailing_empty=False)[1:]
    logger.debug("months_target_1 {}".format(len(months_target_1)))
    months_target_2 = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_month_2']), include_tailing_empty=False)[1:]
    logger.debug("months_target_2 {}".format(len(months_target_2)))
    URLs_targets = wks.get_col(int(config['googlesheets']['dt_sheets_col_target_URLs_2']), include_tailing_empty=False)[1:]
    logger.debug("URLs_targets {}".format(len(URLs_targets)))
    data_for_column_AO = []
    data_for_column_CJ = []
    graph_urls = []

    for url in URLs_targets:
        r = resolve_graph_link(url)
        graph_urls.append(r)
    source_data = zip(graph_urls, months_target_1, months_target_2)
    pool = ThreadPool(20)
    result = pool.starmap(get_data_graph, source_data)
    # print(result)
    for data in result:
        if data == '' or data is None:
            data_for_column_AO.append(['', ''])
            data_for_column_CJ.append(['', ''])
        else:
            data_for_column_AO.append([data[0], data[1]])
            data_for_column_CJ.append([data[2], data[3]])

    if len(data_for_column_AO):
        wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_5'], values=data_for_column_AO)
    else:
        logger.debug('Nothing to load')
    if len(data_for_column_CJ):
        wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_6'], values=data_for_column_CJ)
    else:
        logger.debug('Nothing to load')