"""
Task 1
Can you write a script that scrapes - on a daily basis - the total number of projects found at the top when visiting the links in column A? Values need to be returned in column C. Only return a value in column C if there is a link in column A. This because there are also formulas in column C and they may not get erased by your script. Please note that this and all other scripts that will run on a daily basis would eventually need to be moved to my server.


Task 2
Same here... Can you write a script that scrapes - on a daily basis - the median price found above the chart when visiting the links in column G? Values need to be returned in column H. Only return a value in column C if there is a link in column G. Please return values WITHOUT currency symbols.

"""

import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pygsheets
import yaml

from helpers import headers, headers_xml


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['googlesheets']['name_sheet_pricing_real_estate']
TEST_TAB_NAME = config['googlesheets']['test_tab_pricing_real_estate']
TAB_NAME = config['googlesheets']['tab_pricing_real_estate']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(TAB_NAME)
wks_tab = sh.worksheet_by_title(TAB_NAME)

column_A = wks.get_col(1, include_tailing_empty=False)[1:]
column_G = wks.get_col(7, include_tailing_empty=False)[1:]
# print('column_G', column_G)

test_column_A = [
    'https://www.dotproperty.co.th/en/condos/all',
    'https://www.dotproperty.co.th/en/condos/all/bangkok',
    'https://www.dotproperty.co.th/en/houses/all',
    'https://www.dotproperty.co.th/en/townhouses/all/chonburi',
    'https://www.dotproperty.com.sg/townhouses/all',
    'https://www.dotproperty.id/en/houses/all/jakarta'
]

test_column_G = [
    'https://www.dotproperty.co.th/en/houses-for-rent/bangkok',
    'https://www.dotproperty.co.th/en/townhouses-for-rent/bangkok',
    'https://www.dotproperty.com.vn/en/condos-for-rent',
    'https://www.dotproperty.com.my/condos-for-rent',
    'https://www.dotproperty.co.th/en/houses-for-rent/nonthaburi',
    'https://www.dotproperty.co.th/en/condos-for-rent/phuket',
]



proxies = {
 "http": "http://5.79.73.131:13010",
 "http": "https://5.79.73.131:13010",
}


def make_request(url, headers, method='get', proxies=proxies, timeout=30, t='content'):
    i=0
    result = None
    while not result and i < 20:
        i+=1
        try:
            if method=='get':
                r = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
            else:
                r = requests.post(url, headers=headers, timeout=timeout, proxies=proxies)
            if r.status_code == 200:
                if t=='content':
                    result = r.content
                if t=='json':
                    result = r.json()
                return result
            else:
                print(url, r.status_code)
                time.sleep(1)
        except Exception as e:
            print(i, url, e)
    # TODO: add loguru for multiple attempts


def scrape_task_1(url):
    res = make_request(url, headers)
    soup = BeautifulSoup(res, 'html.parser')
    try:
        result_amount_found_str = soup.find('span', {'id': 'properties_total'}).text.strip()
    except:
        # TODO: loguru
        print('Error in result_amount_found_str', url)
        return None

    result_amount = int(result_amount_found_str.replace(',','').replace('.',''))
    print(result_amount, url)

    return result_amount


def resolve_url_market_stats(url):
    print('INPUT URL:', url)
    try:
        splitted_parts = url.split('/')
        i = 0
        for part in splitted_parts:
            if 'houses' in part or 'condos' in part:
                position_type_estate = i
                base_url = '/'.join(splitted_parts[0:i])
            i += 1
        if '/houses' in url:
            type_estate = 'house'
        if '/condos' in url:
            type_estate = 'condo'
        if '/townhouses' in url:
            type_estate = 'townhouse'
        
        # print('type_esate:', type_estate)

        if len(splitted_parts) == position_type_estate+1:
            geo = ''
        else:
            geo = splitted_parts[-1]
        # print('geo:', geo)

        result_url = '{}/market-stats/search-page/{}/?key={}&priceType=sqmSale&pageType=rent'.format(
            base_url,
            type_estate,
            geo
        )
        
        print(result_url)
        return result_url
    
    except:
        print('Cannot resolve url market stats for', url)
        return ''


def scrape_task_2(url):
    # TODO: RESOLVE LINKS EXAMPLES:
    # input URL: https://www.dotproperty.co.th/en/houses-for-rent/bangkok
    # needed URL: https://www.dotproperty.co.th/en/market-stats/search-page/house/?key=bangkok&priceType=sqmSale&pageType=rent

    # https://www.dotproperty.co.th/en/condos-for-rent/bangkok
    # https://www.dotproperty.co.th/en/market-stats/search-page/condo/?key=bangkok&priceType=sqmSale&pageType=rent

    # https://www.dotproperty.com.vn/en/townhouses-for-rent
    # https://www.dotproperty.com.vn/en/market-stats/search-page/townhouse/?key=&priceType=sqmSale&pageType=rent

    # https://www.dotproperty.com.sg/condos-for-rent
    # https://www.dotproperty.com.sg/market-stats/search-page/condo/?key=&priceType=sqmSale&pageType=rent

    try:
        res = make_request(url, headers_xml, t='json')
        # print(res)
        result = res['msg'].split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]

        """
        soup = BeautifulSoup(res, 'html.parser')
        try:
            result_str = soup.find().text.strip()
        except:
            # TODO: loguru
            print('Error in ', url)
            return None
        """

        # result_amount = int(result_amount_found_str.replace(',','').replace('.',''))
        print(result, url)

        return result
    
    except:
        print('Cannot get market stats from', url)
        return ''



if __name__ == "__main__":
    print('Script have been started at {}'.format(datetime.now()))
    # for url in test_column_A:
    #     scrape_task_1(url)

    # for url in [
    #     'https://www.dotproperty.co.th/en/market-stats/search-page/house/?key=bangkok&priceType=sqmSale&pageType=rent',
    #     'https://www.dotproperty.co.th/en/market-stats/search-page/condo/?key=bangkok&priceType=sqmSale&pageType=rent',
    #     'https://www.dotproperty.com.vn/en/market-stats/search-page/townhouse/?key=&priceType=sqmSale&pageType=rent',
    #     'https://www.dotproperty.com.sg/market-stats/search-page/condo/?key=&priceType=sqmSale&pageType=rent'
    # ]:
    #     scrape_task_2(url)

    
    # for url in [
    #     'https://www.dotproperty.co.th/en/houses-for-rent/bangkok',
    #     'https://www.dotproperty.co.th/en/condos-for-rent/bangkok',
    #     'https://www.dotproperty.com.vn/en/townhouses-for-rent',
    #     'https://www.dotproperty.com.sg/condos-for-rent'
    # ]:
    #     resolve_url_market_stats(url)

    # wks_tab.clear(start='C2', end='C999') # not clear for preventing delete formulas
    # wks_tab.clear(start='H2', end='H999')

    column_C_position = 2
    for row in column_A:
        if row.strip() != '':
            value = scrape_task_1(row)
            # print(row, value)
            wks_tab.update_value('C{}'.format(column_C_position), value)
            # clear H{} value here
        
        column_C_position += 1


    
    # READY code for part 2

    median_sale_price_list = []

    column_G_position = 2
    for row in column_G:
        if row.strip() != '':
            # median_sale_price_list.append(scrape_task_2(resolve_url_market_stats(row)))
            value = scrape_task_2(resolve_url_market_stats(row))
            wks_tab.update_value('H{}'.format(column_G_position), value)
        
        column_G_position += 1

    # print(median_sale_price_list, len(median_sale_price_list))

    # wks_tab.clear(start='H2', end='H999')
    # wks_tab.update_col(8, median_sale_price_list, row_offset=1)

    print('Script have been finished at {}'.format(datetime.now()))