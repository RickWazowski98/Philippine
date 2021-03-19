import logging
import json
import time
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml, clear_ph_peso
import argparse
import yaml
import pygsheets
from loguru import logger
import os
import sys

from multiprocessing.pool import ThreadPool
from proxy_config import get_proxy

my_parser = argparse.ArgumentParser()
my_parser.add_argument('-tn')
args = my_parser.parse_args()
input_tab_name = args.tn

basedir = os.path.dirname(__file__)
logfile = os.path.join(basedir, "logs", f"{input_tab_name.replace(' ', '_').lower()}_args_dt_dotproperty-1.log")
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
wks = sh.worksheet_by_title('Filters')

try:
    filter_values = wks.get_values(f"B{int(mapping_config['filter_row'])}", f"AC{int(mapping_config['filter_row'])}",
                                   include_tailing_empty=True)[0]
    # logger.debug(filter_values)
    filter_values_int = []
    for v in filter_values:
        try:
            filter_values_int.append(int(v))
        except Exception as e:
            # logger.debug(e)
            filter_values_int.append(None)
except Exception as e:
    logger.debug(e)
    filter_values_int = [[] for x in range(30)]

logger.debug(f'filter_values: {filter_values_int}, len:{len(filter_values_int)}')


def get_data_condo(url):
    if url == '/cdn-cgi/l/email-protection':
        return "", "", "", "", ""
    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.proxies.update(get_proxy())
        # r = session.get(url, headers=headers_xml, timeout=30)
        r = session.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            logger.debug('status_code', r.status_code, url)
            return ["", "", "", "", ""]
        soup = BeautifulSoup(r.content, 'html.parser')
        # print(soup)
        if input_tab_name.split(" ")[0] == "Vietnam":
            # print("vi")
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=20)
            session.mount('https://', adapter)
            session.mount('http://', adapter)
            session.proxies.update(get_proxy())
            vi_url = url.replace("/en", "")
            vi_r = session.get(vi_url, headers=headers, timeout=20)
            # print(vi_url)
            vi_soup = BeautifulSoup(vi_r.content, 'html.parser')
            try:
                condo_name = vi_soup.find('div', {'class': 'row top-navigation-bar add-padding'}).find('a').text.strip()
            except:
                condo_name = ''
            try:
                developer_name = vi_soup.find('div', {'class': 'col-sm-6 nav-top-btngroups text-right'}).find('li').find(
                    'p').text.strip()
            except:
                developer_name = ''
            """
            locations = vi_soup.find('div', {'class': 'locations'}).find('small').text.strip()
            try:
                city, province = locations.split(', ')
            except ValueError:
                province = locations
                city = ''
            area = " ".join(vi_soup.find('ol', {'class': 'breadcrumb'}).find_all('li')[-2].text.split())
            """
            breadcrumbs = vi_soup.find('ol', {'class': 'breadcrumb'}).find_all('li')
            province = breadcrumbs[3].text.strip()
            if len(breadcrumbs) > 5:
                city = breadcrumbs[4].text.strip()
                # print(city)
            else:
                city = ''
            if len(breadcrumbs) > 6:
                area = breadcrumbs[5].text.strip()
            else:
                area = ''
        else:
            try:
                condo_name = soup.find('div', {'class': 'row top-navigation-bar add-padding'}).find('a').text.strip()
            except:
                condo_name = ''
            try:
                developer_name = soup.find('div', {'class': 'col-sm-6 nav-top-btngroups text-right'}).find('li').find(
                    'p').text.strip()
            except:
                developer_name = ''
            """
            locations = soup.find('div', {'class': 'locations'}).find('small').text.strip()
            try:
                city, province = locations.split(', ')
            except ValueError:
                province = locations
                city = ''
            area = " ".join(soup.find('ol', {'class': 'breadcrumb'}).find_all('li')[-2].text.split())
            """
            breadcrumbs = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')
            province = breadcrumbs[3].text.strip()
            if len(breadcrumbs) > 5:
                city = breadcrumbs[4].text.strip()
            else:
                city = ''
            if len(breadcrumbs) > 6:
                area = breadcrumbs[5].text.strip()
            else:
                area = ''

        try:
            # total_units = soup.find('div', {'class': 'col-md-12 col-lg-8 project-content'}).find('section').text.strip().split('contains ')[1].split(' total')[0]
            total_units_raw = \
            soup.find('div', {'class': 'col-md-12 col-lg-8 project-content'}).find('section').text.strip().split(
                ' total units')[0].split(' ')[-1]
            if any(char.isdigit() for char in total_units_raw):
                total_units = total_units_raw
            else:
                total_units = ''
        except:
            total_units = ''
        try:
            units_for_rent = soup.find('a', {'id': 'open-tab-rent'}).text.strip().split(' ')[0]
        except:
            units_for_rent = ''
        """
        try:
            start_from_block = soup.find('div', {'class': 'header-line-3'})
            if start_from_block.find('a', {'id':'open-tab-rent'}):
                start_from_str = start_from_block.find_all('span', {'class': 'txt-orange'})[-1].text.strip()
                start_from = start_from_str.split('from ')[1]
                start_from = clear_ph_peso(start_from)
            else:
                start_from = ''
        except:
            start_from = ''
        """
        number_of_studios = scrape_room_types_prices(soup)
        start_from, sqm = scrape_rent_units_listing(soup)
        lowest_ask_price, sqm_ask = scrape_rent_sale_listing(soup)
        other_projects_nearby = scrape_other_projects_nearby(soup)
        popular_condos_in_area = scrape_popular_condos_in_area(soup)
        room_types_prices = scrape_room_types_prices_ext(soup)
        # print("other_projects_nearby", other_projects_nearby)

        s_n_of_units_for_rent, s_av_rent, s_av_ask_price, bd1_n_of_units_for_rent, bd1_av_rent, bd1_av_ask_price, bd2_n_of_units_for_rent, bd2_av_rent, bd2_av_ask_price, bd3_n_of_units_for_rent, bd3_av_rent, bd3_av_ask_price, bd4_n_of_units_for_rent, bd4_av_rent, bd4_av_ask_price = '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
        s_n_of_units_for_sale, bd1_n_of_units_for_sale, bd2_n_of_units_for_sale, bd3_n_of_units_for_sale, bd4_n_of_units_for_sale = '', '', '', '', ''
        s_size, bd1_size, bd2_size, bd3_size, bd4_size = '', '', '', '', ''

        for t in room_types_prices:
            if t['type'] == 'Studio':
                s_size = t['size']
                s_n_of_units_for_rent = t['number of units for rent']
                s_av_rent = t['average rent']
                s_av_ask_price = t['average ask price']
                s_n_of_units_for_sale = t['number of units for sale']
            if t['type'] == '1 Bedroom' or t['type'] == '1 Phòng Ngủ':
                bd1_size = t['size']
                bd1_n_of_units_for_rent = t['number of units for rent']
                bd1_av_rent = t['average rent']
                bd1_av_ask_price = t['average ask price']
                bd1_n_of_units_for_sale = t['number of units for sale']
            if t['type'] == '2 Bedrooms' or t['type'] == '2 Phòng Ngủ':   
                bd2_size = t['size']
                bd2_n_of_units_for_rent = t['number of units for rent']
                bd2_av_rent = t['average rent']
                bd2_av_ask_price = t['average ask price']
                bd2_n_of_units_for_sale = t['number of units for sale']
            if t['type'] == '3 Bedrooms' or t['type'] == '3 Phòng Ngủ':
                bd3_size = t['size']
                bd3_n_of_units_for_rent = t['number of units for rent']
                bd3_av_rent = t['average rent']
                bd3_av_ask_price = t['average ask price']
                bd3_n_of_units_for_sale = t['number of units for sale']
            if t['type'] == '4 Bedrooms' or t['type'] == '4 Phòng Ngủ':
                bd4_size = t['size']
                bd4_n_of_units_for_rent = t['number of units for rent']
                bd4_av_rent = t['average rent']
                bd4_av_ask_price = t['average ask price']
                bd4_n_of_units_for_sale = t['number of units for sale']

        # logger.debug(condo_name, developer_name, city, province, area, total_units, units_for_rent, number_of_studios, start_from, sqm)
        # logger.debug(lowest_ask_price, sqm_ask)
        # logger.debug(other_projects_nearby)
        # logger.debug(popular_condos_in_area)

        graph_link = resolve_graph_link(url)
        # logger.debug(graph_link)
        try:
            median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, \
            earliest_median_rent_price_sqm, earliest_month_1, project_median_sale_price_sqm_1_year_ago, \
            project_median_sale_price_sqm_8_month_ago, median_sale_price = get_data_graph(graph_link)
        except TypeError as err:
            median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, \
            earliest_median_rent_price_sqm, earliest_month_1, project_median_sale_price_sqm_1_year_ago, \
            project_median_sale_price_sqm_8_month_ago, median_sale_price = '', '', '', '', '', '', '', '', ''
            logger.debug(err)
            logger.debug("get data graph err")
        # logger.debug('DEBUG s_n_of_units_for_rent:', s_n_of_units_for_rent)

        try:
            gps_str = soup.find('a', {'id': 'go-to-map-mobile'}).find('img')['src'].split('map_')[1].split('.jpg')[0]
            gps_lat, gps_long = gps_str.split('_')
        except:
            gps_lat, gps_long = '', ''

        result_bulk_1 = {
            'url': url,
            'condo_name': condo_name,
            'developer_name': developer_name,
            'province': province,
            'city': city
        }
        # print(result_bulk_1)
        result_bulk_2 = {
            'area': area,
        }
        result_bulk_3 = {
            'median_rent_price_sqm': median_rent_price_sqm,  # L
            's_size': s_size,  #
            'bd1_size': bd1_size,
            'bd2_size': bd2_size,
            'bd3_size': bd3_size,
            'bd4_size': bd4_size,  # Q
            'median_sale_price_sqm': median_sale_price_sqm,
            's_n_of_units_for_sale': s_n_of_units_for_sale,
            'bd1_n_of_units_for_sale': bd1_n_of_units_for_sale,
            'bd2_n_of_units_for_sale': bd2_n_of_units_for_sale,
            'bd3_n_of_units_for_sale': bd3_n_of_units_for_sale,
            'bd4_n_of_units_for_sale': bd4_n_of_units_for_sale,  # W
            'earliest_median_rent_price_sqm': earliest_median_rent_price_sqm,  # X
            'earliest_month_1': earliest_month_1,
            'earliest_median_sale_price_sqm': earliest_median_sale_price_sqm,  # Z
            'earliest_month': earliest_month,
            'total_units': total_units,  # AB col
            'part2_28_09-1': s_n_of_units_for_rent,
            'part2_28_09-2': check_outlier(s_av_rent, filter_values_int[0], filter_values_int[1]),
            'part2_28_09-3': check_outlier(s_av_ask_price, filter_values_int[2], filter_values_int[3]),
            'part2_28_09-4': bd1_n_of_units_for_rent,
            'part2_28_09-5': check_outlier(bd1_av_rent, filter_values_int[4], filter_values_int[5]),
            'part2_28_09-6': check_outlier(bd1_av_ask_price, filter_values_int[6], filter_values_int[7]),
            'part2_28_09-7': bd2_n_of_units_for_rent,
            'part2_28_09-8': check_outlier(bd2_av_rent, filter_values_int[8], filter_values_int[9]),
            'part2_28_09-9': check_outlier(bd2_av_ask_price, filter_values_int[10], filter_values_int[11]),
            'part2_28_09-10': bd3_n_of_units_for_rent,
            'part2_28_09-11': check_outlier(bd3_av_rent, filter_values_int[12], filter_values_int[13]),
            'part2_28_09-12': check_outlier(bd3_av_ask_price, filter_values_int[14], filter_values_int[15]),
            'part2_28_09-13': bd4_n_of_units_for_rent,
            'part2_28_09-14': check_outlier(bd4_av_rent, filter_values_int[16], filter_values_int[17]),
            'part2_28_09-15': check_outlier(bd4_av_ask_price, filter_values_int[18], filter_values_int[19]),
            'start_from': start_from,  # Lowest rent # AR col
            'sqm': sqm,
            'lowest_ask_price': lowest_ask_price,  # AT col
            'sqm_ask': sqm_ask,
            'number_of_studios': number_of_studios,
            'lat': gps_lat,
            'long': gps_long,
            'other_projects_nearby': other_projects_nearby,
        }
        result_bulk_4 = {
            'project_median_sale_price_sqm_1_year_ago': project_median_sale_price_sqm_1_year_ago,
            'project_median_sale_price_sqm_8_month_ago': project_median_sale_price_sqm_8_month_ago,
        }
        result_bulk_5 = {
            'median_sale_price': median_sale_price
        }
        """result = []
        result.append(result_bulk_1)
        result.append(result_bulk_2)
        result.append(result_bulk_3)
        result.append(result_bulk_4)
        result.append(result_bulk_5)"""
        return result_bulk_1, result_bulk_2, result_bulk_3, result_bulk_4, result_bulk_5
    except requests.exceptions.RequestException as e:
        # return {}, {}, {}, {}, {}
        logger.debug(e)
        # return "None", "None", "None", "None", "None"


def scrape_room_types_prices(soup):
    # 23 Oct: Can you do this one too? Please return "Studio" if there is a studio unit for sale. If not, please return "1BR" if there is a 1BR unit for sale. If also not, please return nothing.
    """
    try:
        table = soup.find('div', {'class': 'container-table'}).find_all('div', {'class': 'column text-center'})
        for row in table:
            type_name = row.find('div', {'class': 'cell'}).text.strip()
            if type_name == 'Studio' or '1 Bedroom':
                return row.find_all('div', {'class': 'cell'})[-1].text.strip().split('For rent:')[1].split('(')[1].split('unit')[0].strip()

        return 0
    
    except:
        return ''
    """
    try:
        table = soup.find('div', {'class': 'container-table'}).find_all('div', {'class': 'column text-center'})
        for row in table:
            type_name = row.find('div', {'class': 'cell'}).text.strip()
            if type_name == 'Studio':
                return 'Studio'
            if type_name == '1 Bedroom':
                return '1BR'

        return ''

    except:
        return ''


def scrape_rent_units_listing(soup):
    try:
        table = soup.find_all('tr', {'data-tenure': 'rent'})
        # temporarily turn off this filter 
        min_price = filter_values_int[21] if filter_values_int[21] else 10000000000000
        num_check_for_outlier = filter_values_int[20] if filter_values_int[20] else 0

        for row in table:
            price_row_text = row.find('span', {'class': 'price'}).text
            price_str = price_row_text.split()[1]
            # if ',000' not in price_str:
            #     price_str = '{},000'.format(price_str)
            if any(char.isdigit() for char in price_str):  # and '.' not in price_str:
                if ' - ' in price_row_text:
                    price_str_multiplied = '{}000'.format(price_str)
                    price_int = int(price_str_multiplied.replace('.', ''))
                    # logger.debug('MULTIPLIED', price_int)
                else:
                    # logger.debug('YES', price_str)
                    price_int = int(price_str.replace(',', ''))
                    # logger.debug(price_int)

                # if price_int < min_price: # and price_int >= 7000: # 26.10 filter >=7000
                if price_int < min_price and price_int > num_check_for_outlier:  # temporarily turn off this filter
                    sqm = row.find_all('td')[1].text.split()[0].strip()
                    min_price = price_int
        # logger.debug(min_price, sqm)
        return min_price, sqm

    except:
        return '', ''


def scrape_rent_sale_listing(soup):
    try:
        price_int = None
        table = soup.find_all('tr', {'data-tenure': 'sale'})
        # temporarily turn off this filter 
        min_price = filter_values_int[25] if filter_values_int[25] else 10000000000000
        num_check_for_outlier = filter_values_int[24] if filter_values_int[24] else 0

        for row in table:
            price_str = row.find('span', {'class': 'price'}).text.split()[1]
            # logger.debug(price_str)
            if ',' in price_str:
                price_int = int(price_str.replace(',', ''))

            elif '.' in price_str:
                price_int = int(float(price_str.replace('.', '')) * 100000000)

            elif price_str.isdigit():
                price_int = int(price_str) * 1000000000

            if price_int:
                # if price_int < min_price: # and price_int >= 919500: # 26.10 filter >=919500
                if price_int < min_price and price_int > num_check_for_outlier:  # temporarily turn off this filter
                    sqm = row.find_all('td')[1].text.split()[0].strip()
                    min_price = price_int

        logger.debug(f'<><> scrape_rent_sale_listing: {min_price}, {sqm} <><>')
        return min_price, sqm

    except:
        return '', ''


def scrape_other_projects_nearby(soup):
    other_projects_nearby = None
    result = ''
    sections = soup.find_all('section')
    for section in sections:
        if section.find('h2', string='Other projects nearby') or section.find('h2', string='Các dự án lân cận'):
            other_projects_nearby = section.find('div', {'class': 'col-md-8'}).find_all('span')
            break
    # print("other_projects_nearby", other_projects_nearby)
    if other_projects_nearby:
        for entry in other_projects_nearby:
            result += '{}; '.format(entry.text)
        result = result[:-2]

    return result


def scrape_popular_condos_in_area(soup):
    try:
        popular_condos_in_area = []
        popular_condos_in_area_block = soup.find('div', {'class': 'panel-body'}).find_all('div', {
            'class': 'detail-block col-lg-8 left-block'})
        for condo in popular_condos_in_area_block:
            popular_condos_in_area.append(condo.find('h3').text.strip())
        result_str = ", ".join(popular_condos_in_area)
        return result_str
    except:
        return ''


def scrape_room_types_prices_ext(soup):
    result = []
    table_0 = soup.find('div', {'class': 'container-table'})
    if table_0:
        table = table_0.find_all('div', {'class': 'column text-center'})
        # print(table)
        for row in table:
            # print(row)
            row_dict = {}
            row_data_raw = row.find_all('div', {'class': 'cell'})
            try:
                size = [int(s) for s in row_data_raw[1].text.split('m')[0].split() if s.isdigit()][0]
            except:
                size = ''
            try:
                number_of_units_for_rent = \
                [int(s) for s in row_data_raw[2].text.split('For rent')[1].split('(')[1].split(')')[0].split() if
                 s.isdigit()][0]
            except:
                number_of_units_for_rent = 0
            try:
                number_of_units_for_sale = \
                [int(s) for s in row_data_raw[2].text.split('For sale')[1].split('(')[1].split(')')[0].split() if
                 s.isdigit()][0]
            except:
                number_of_units_for_sale = 0
            try:
                average_rent = \
                [int(s) for s in row_data_raw[2].text.replace(',', '').split('For rent')[1].split('(')[0].split() if
                 s.isdigit()][0]
            except:
                average_rent = ''
            try:
                average_ask_price = \
                    [int(s) for s in row_data_raw[2].text.replace(',', '').split('For sale')[1].split('(')[0].split() if
                        s.isdigit()][0]
            except:
                average_ask_price = ''

            row_dict.update({
                'size': size,
                'type': row_data_raw[0].text.strip(),
                'number of units for rent': number_of_units_for_rent,
                'number of units for sale': number_of_units_for_sale,
                'average rent': average_rent,
                'average ask price': average_ask_price
            })
            result.append(row_dict)

    # logger.debug('---DEBUG---')
    # logger.debug(result, len(result))
    return result


def get_data_graph(url):
    """
    13.07: add Project's median sale price/sqm 1 year ago,
    Project's median sale price/sqm 8 months ago,
    Median sale price
    """
    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.proxies.update(get_proxy())
        # r = session.get(url, headers=headers_xml, timeout=30)
        r = session.get(url, headers=headers_xml, timeout=30)
        if r.status_code != 200:
            # logger.debug('status_code', r.status_code)
            return None
        data = r.json()['msg']
        #print(r.text)
        if r.url == "https://www.dotproperty.co.th/en":
            return '', '', '', '', '', '', '', '', ''
        # logger.debug(data)

        try:
            median_rent_price_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
            if median_rent_price_sqm is None:
                median_rent_price_sqm = ''
        except:
            median_rent_price_sqm = ''
        try:
            earliest_median_rent_prices_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')
            if earliest_median_rent_prices_sqm is None:
                earliest_median_rent_prices_sqm = ''
        except:
            earliest_median_rent_price_sqm = ''
        try:
            median_sale_price_sqm = data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
            if median_sale_price_sqm is None:
                median_sale_price_sqm = ''
        except:
            median_sale_price_sqm = ''
        try:
            earliest_median_sale_prices_sqm = data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')
            if earliest_median_sale_prices_sqm is None:
                earliest_median_sale_prices_sqm = ''
        except:
            earliest_median_sale_prices_sqm = ''

        # earliest_median_sale_price_sqm = ''
        try:

            # TODO soup find earliest_median_sale_price_sqm
            earliest_median_sale_price_sqm = ''
            if earliest_median_sale_prices_sqm == '':
                raise Exception
            month_num = 0
            for price in earliest_median_sale_prices_sqm:
                month_num += 1
                if price != '':
                    earliest_median_sale_price_sqm = price
                    break

            months = data.split("labels: [")[1].split("],")[0].split(",")
            earliest_month = months[month_num - 1].replace('"', '')
        except:
            earliest_median_sale_price_sqm = ''
            earliest_month = ''

        earliest_median_rent_price_sqm = ''
        try:
            # TODO soup find
            earliest_median_rent_price_sqm = ''
            if earliest_median_rent_prices_sqm == '':
                raise Exception
            month_num = 0
            for price in earliest_median_rent_prices_sqm:
                month_num += 1
                if price != '' and price is not None:
                    earliest_median_rent_price_sqm = price
                    break

            months = data.split("labels: [")[1].split("],")[0].split(",")
            earliest_month_1 = months[month_num - 1].replace('"', '')
            if earliest_month_1 is None:
                earliest_month_1 = ''
        except:
            earliest_median_rent_price_sqm = ''
            earliest_month_1 = ''

        try:
            project_median_sale_price_sqm_1_year_ago = \
            data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[-12]  #[0]
            # print("1-{}".format(project_median_sale_price_sqm_1_year_ago))
            if project_median_sale_price_sqm_1_year_ago is None:
                project_median_sale_price_sqm_1_year_ago = ''
        except:
            project_median_sale_price_sqm_1_year_ago = ''
        try:
            project_median_sale_price_sqm_8_month_ago = \
            data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[-8]  #[0]
            # print("8-{}".format(project_median_sale_price_sqm_8_month_ago))
            if project_median_sale_price_sqm_8_month_ago is None:
                project_median_sale_price_sqm_8_month_ago = ''
        except:
            project_median_sale_price_sqm_8_month_ago = ''
        try:
            median_sale_price = data.split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
            # print("median sale price-{}".format(median_sale_price))
            if median_sale_price is None:
                median_sale_price = ''
        except:
            median_sale_price = ''

        # logger.debug("get_data_graph:" ,median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, earliest_median_rent_price_sqm, earliest_month_1)
        return median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, earliest_median_rent_price_sqm, earliest_month_1, project_median_sale_price_sqm_1_year_ago, project_median_sale_price_sqm_8_month_ago, median_sale_price
    except requests.exceptions.RequestException as e:
        logger.debug(e)
        return '', '', '', '', '', '', '', '', ''


def get_data_projects(url):
    try:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.proxies.update(get_proxy())
        # r = session.get(url, headers=headers_xml, timeout=30)
        r = session.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            # logger.debug('status_code', r.status_code)
            return None
        soup = BeautifulSoup(r.content, 'html.parser')

        project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
        result = set()
        for link in project_links:
            if link['href']:
                result.add(link['href'])
        # logger.debug(result, len(result))
    except requests.exceptions.RequestException as e:
        # logger.debug(e)
        return None


def resolve_graph_link(url_project):
    id = None
    if '/condo/' in url_project:
        id = url_project.split('/condo/')[1].split('/')[0]
    if '/showcase/' in url_project:
        id = url_project.split('/showcase/')[1].split('/')[0]
    if '/house/' in url_project:
        id = url_project.split('/house/')[1].split('/')[0]
    if '/townhouse/' in url_project:
        id = url_project.split('/townhouse/')[1].split('/')[0]
    if '/townhouses/' in url_project:
        id = url_project.split('/townhouses/')[1].split('/')[0]
    if id != None:
        if input_tab_name == "Vietnam townhouses":
            url = f"https://www.{mapping_config['domain']}/market-stats/project-page/condo/?key={id}"
            logger.debug(url)
            return url
        else:
            url = f"https://www.{mapping_config['domain']}/en/market-stats/project-page/condo/?key={id}"
            return url
    logger.debug('WARNING: cant resolve graph_link for market stats')
    return ''


def check_outlier(num_or_spare, number_less, number_more=None):
    # (num_or_spare, digits_less, digits_more=None):
    # temporarily turn off the filter
    """
    if num_or_spare != '':
        if len(str(num_or_spare)) < digits_less:
            return ''
        if digits_more:
            if len(str(num_or_spare)) > digits_more:
                return ''
    """
    try:
        if num_or_spare == '':
            return num_or_spare
        if number_less == None and number_more == None:
            return num_or_spare
        if number_less == None and number_more != None:
            if int(num_or_spare) > number_more:
                return ''
        if number_less != None and number_more == None:
            if int(num_or_spare) < number_less:
                return ''

        # logger.debug(num_or_spare, number_less, number_more)
        if int(num_or_spare) < number_less:
            return ''
        if number_more:
            if int(num_or_spare) > number_more:
                return ''
        return num_or_spare
    except:
        return num_or_spare


if __name__ == "__main__":
    # get_data_condo('https://www.dotproperty.co.th/en/condo/16601/modiz-rhyme')
    file_object = open(f"data/{mapping_config['file_proj_urls']}.json", 'r')
    links = json.load(file_object)
    pool = ThreadPool(20)
    result = pool.map(get_data_condo, links)
    pool.close()
    pool.join()
    time.sleep(5)
    #result = []
    #var = get_data_condo(links[0])
    #result.append(var)
    #print(result[0][0])
    bulk1, bulk2, bulk3, bulk4, bulk5 = [], [], [], [], []
    for data in result:
        
        if data is not None:
            if data[0] is not None and data[0] != '':
                bulk1.append(data[0])
            else:
                bulk1.append({})
            if data[1] is not None and data[1] != '':
                bulk2.append(data[1])
            else:
                bulk2.append({})
            if data[2] is not None and data[2] != '':
                bulk3.append(data[2])
            else:
                bulk3.append({})
            if data[3] is not None and data[3] != '':
                #print(f"{data[3]}")
                bulk4.append(data[3])
            else:
                bulk4.append({})
            if data[4] is not None and data[4] != '':
                bulk5.append(data[4])
            else:
                bulk5.append({})
        else:
            bulk1.append({})
            bulk2.append({})
            bulk3.append({})
            bulk4.append({})
            bulk5.append({})

    with open(f"data/{mapping_config['file_data_bulk_1']}.json", "w+") as file_obj:
        json.dump(bulk1, file_obj, indent=4)
    # time.sleep(1)
    with open(f"data/{mapping_config['file_data_bulk_2']}.json", "w+") as file_obj:
        json.dump(bulk2, file_obj, indent=4)
    # time.sleep(1)
    with open(f"data/{mapping_config['file_data_bulk_3']}.json", "w+") as file_obj:
        json.dump(bulk3, file_obj, indent=4)
    # time.sleep(1)
    with open(f"data/{mapping_config['file_data_bulk_3']}_4.json", "w+") as file_obj:
        json.dump(bulk4, file_obj, indent=4)
    # time.sleep(1)
    with open(f"data/{mapping_config['file_data_bulk_3']}_5.json", "w+") as file_obj:
        json.dump(bulk5, file_obj, indent=4)

        # graph_link = resolve_graph_link(link)
        # logger.debug(graph_link)
        # get_data_graph(graph_link)

        # time.sleep(1)

    # move it upper for write after each iteration
    # file_object = open('data/projects_data.json', 'w')
    # json.dump(result, file_object, indent=4)
