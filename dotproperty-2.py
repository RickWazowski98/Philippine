import logging
import json
import time
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml


def resolve_graph_link(url_str):
    provinces_cities_areas = url_str.split('condos-for-rent/')[1]
    url = 'https://www.dotproperty.com.ph/market-stats/search-page/condo/?key={}&priceType=sqmSale&pageType=rent'.format(provinces_cities_areas)
    print(url)
    return url

def get_data_graph(url):
    r = requests.get(url, headers=headers_xml, timeout=30)
    if r.status_code != 200:
        print('status_code', r.status_code)
        return None
    data = r.json()['msg']
    
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
        part_2_3 = data.split("htmlDecode('Median rent price")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_3 = ''
    try:
        part_2_4 = data.split("htmlDecode('Median rent price'\n")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_4 = ''
    try:
        part_2_5 = data.split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
    except:
        part_2_5 = ''


    return median_rent_price_sqm, earliest_median_sale_price_sqm, earliest_month, median_sale_price_sqm, earliest_median_rent_price_sqm, earliest_month_1, '', part_2_1, part_2_2, part_2_3, part_2_4,'',part_2_5


if __name__ == "__main__":
    file_object = open('data/provinces-cities-areas.json', 'r')
    links = json.load(file_object)
    result = []

    for link in links:
        print(link)
        result_project = get_data_graph(resolve_graph_link(link))
        result.append(result_project)

        # time.sleep(1)
    
    file_object = open('data/provinces-cities-areas_data.json', 'w')
    json.dump(result, file_object, indent=4)