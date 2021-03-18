import bs4
import json
import pygsheets
import logging
import yaml
import time
import requests
import os

from multiprocessing.pool import ThreadPool



def get_proxies():
    http_proxy = "http://81ztb0hcg6er357:UlaniAt2YrbGYpbV_country-Thailand@hub.zenscrape.com:31112"
    proxyDict = {
            "http": http_proxy,
            "https": http_proxy
        }
    # print(proxyDict)
    return proxyDict


HEADERS = {
    "authority": "www.dotproperty.co.th",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5,en-US;q=0.4",
    "cookie": "__cfduid=d5ab83dc3d72ea34d45bd085e774b913b1613420556; dot_property_group_idu=eyJpdiI6ImVIMmdUaTF5eDZTZjZRMEptcWIwSHc9PSIsInZhbHVlIjoiQnVERUhGd3BqVFFcL2NZalNIMzVNekNYZmx0WlhQRHVBOEJBZGJ0a1pOK0xPNzl1bHhtQVRycElKcmdScWNMSVIiLCJtYWMiOiJkM2Y2MTc1NDkyZTg0ZjY5ZDg5NjhmNzViODM2ZGJiZmUxODQ5OGYyNDA5YzM3ODAzZDk1MDFkNWUyOWZlNzZkIn0%3D; user_language=eyJpdiI6IjczZGU2MkkwUm5JWU12akdBUWYwRmc9PSIsInZhbHVlIjoiczl6dmQ4SGt2YUlsTEhnZk0zTWlUZz09IiwibWFjIjoiYmNjMTNjZWEzNDBjNjQwNjc0NjUyZGIxZGI5Y2QxNGMwYTVkMjJmMjBmZGUxZDE0NmQzOTgzNTQ0ZDNhZmYzYiJ9; XSRF-TOKEN=eyJpdiI6IjVPVk9NekJyaWVxWUg1OW12NnpTckE9PSIsInZhbHVlIjoiV1pxbGJ0QnNVZXFtWHpSa2IrZ3FVYmhDVFowMEc2M2h3RTZpc29QdWxxT2krV1p2dkJCblFxWkNzVjR6YnA5WWNKeHk5UHg0eGF2WGtzTWZiWUdFamc9PSIsIm1hYyI6ImU2Yzg1ODlkYTNiNmQ3MWQ0NTdhMzk5ZWNiN2VkODFlZDFmZTFjNGFjM2IxM2JjODM2ZWUxMGFmN2JiM2E5NGIifQ%3D%3D; dot_property_group=eyJpdiI6IjNvMnFvUDdGeVFjV0hTQ21aVmlcL3FRPT0iLCJ2YWx1ZSI6IjRwSWJsNUJGYXhna1ZHdFJcL0FFeFljV1F5RHlscldFdERnWjJZRCswS1lFQW5KT2E1TG92Y1EycVlhUk5oTTRTQ1FBcUpnRFcyKzgrdDgwTStYT1NBZz09IiwibWFjIjoiODUyYTA4YTIzODM4NTc4MDBmZTRkMDdiNjU5ZmMxZGI5MTZmODhkNjI2NTI0MWExZDhiNTM0NzQ0MjFhZjVlNiJ9",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": '?0',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    "Content-type": 'text/plain; charset="utf-8"',
}


class ThBkCondosParser:
    def __init__(self):
        self.logger = self.create_logger()
        self.config = self.open_config()
        self.work_sheet = self.open_worksheet()
        self.source_links = self.get_source_links()
        self.pool = ThreadPool(5)

    def create_logger(self):
        logger = logging.getLogger('Thailand Condominums scraper')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s|%(levelname)s|%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def open_config(self):
        with open("config.yml", 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
            return config

    def open_worksheet(self):
        service_file = self.config['googlesheets']['file']
        # sheet_name = 'Copy of Dot Property Data - Real Estate Data (for purposes of solving scraping issues)'
        sheet_1 = 'Thailand condominiums'
        gc = pygsheets.authorize(service_file=service_file)
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
        # sh = gc.open(sheet_name)
        wks = sh.worksheet_by_title(sheet_1)
        return wks

    def get_source_links(self):
        with open('data/th_condos_source_link_result.json', 'r+') as th_jsonfile:
            json_th_data = json.load(th_jsonfile)
        with open('data/bk_condos_source_link_result.json', 'r+') as bk_jsonfile:
            json_bk_data = json.load(bk_jsonfile)
        links_list = json_th_data + json_bk_data
        self.logger.debug('data success compare')
        return links_list

    def save_source_links_to_sheet(self):
        self.work_sheet.update_col(1, [link["link"] for link in self.source_links if link["link"] != ""], row_offset=1)
        link_count = len([link["link"] for link in self.source_links if link["link"] != ""])
        self.logger.debug('{} links was add to sheet'.format(link_count))

    def parse_data(self, url):
        self.logger.info("Start parsing data from url: {}".format(url))
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        code = session.get(url, headers=HEADERS, proxies=get_proxies(), stream=True)
        time.sleep(0.5)
        soup = bs4.BeautifulSoup(code.text, 'html.parser')
        try:
            try:
                condo_name = soup.find('div', {'class': 'row top-navigation-bar add-padding'}).find('a').text.strip()
            except:
                return None
            try:
                developer_name = soup.find('div', {'class': 'col-sm-6 nav-top-btngroups text-right'}).find('li').find('p').text.strip()
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
                total_units_raw = soup.find('div', {'class': 'col-md-12 col-lg-8 project-content'}).find('section').text.strip().split(' total units')[0].split(' ')[-1]
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
            number_of_studios = self.scrape_room_types_prices(soup)
            start_from, sqm = self.scrape_rent_units_listing(soup)
            lowest_ask_price, sqm_ask = self.scrape_rent_sale_listing(soup)
            other_projects_nearby = self.scrape_other_projects_nearby(soup)
            popular_condos_in_area = self.scrape_popular_condos_in_area(soup)
            room_types_prices = self.scrape_room_types_prices_ext(soup)
            # print(number_of_studios, start_from, sqm, lowest_ask_price, sqm_ask, other_projects_nearby, popular_condos_in_area, room_types_prices)

            s_n_of_units_for_rent, s_av_rent, s_av_ask_price, bd1_n_of_units_for_rent,bd1_av_rent,bd1_av_ask_price,bd2_n_of_units_for_rent,bd2_av_rent,bd2_av_ask_price,bd3_n_of_units_for_rent,bd3_av_rent,bd3_av_ask_price,bd4_n_of_units_for_rent,bd4_av_rent,bd4_av_ask_price = '','','','','','','','','','','','','','',''
            s_n_of_units_for_sale, bd1_n_of_units_for_sale, bd2_n_of_units_for_sale, bd3_n_of_units_for_sale, bd4_n_of_units_for_sale = '', '', '', '', ''
            s_size, bd1_size, bd2_size, bd3_size, bd4_size = '','','','',''

            for t in room_types_prices:
                if t['type'] == 'Studio':
                    s_size = t['size']
                    s_n_of_units_for_rent = t['number of units for rent']
                    s_av_rent = t['average rent']
                    s_av_ask_price = t['average ask price']
                    s_n_of_units_for_sale = t['number of units for sale']
                if t['type'] == '1 Bedroom':
                    bd1_size = t['size']
                    bd1_n_of_units_for_rent = t['number of units for rent']
                    bd1_av_rent = t['average rent']
                    bd1_av_ask_price = t['average ask price']
                    bd1_n_of_units_for_sale = t['number of units for sale']
                if t['type'] == '2 Bedrooms':
                    bd2_size = t['size']
                    bd2_n_of_units_for_rent = t['number of units for rent']
                    bd2_av_rent = t['average rent']
                    bd2_av_ask_price = t['average ask price']
                    bd2_n_of_units_for_sale = t['number of units for sale']
                if t['type'] == '3 Bedrooms':
                    bd3_size = t['size']
                    bd3_n_of_units_for_rent = t['number of units for rent']
                    bd3_av_rent = t['average rent']
                    bd3_av_ask_price = t['average ask price']
                    bd3_n_of_units_for_sale = t['number of units for sale']
                if t['type'] == '4 Bedrooms':
                    bd4_size = t['size']
                    bd4_n_of_units_for_rent = t['number of units for rent']
                    bd4_av_rent = t['average rent']
                    bd4_av_ask_price = t['average ask price']
                    bd4_n_of_units_for_sale = t['number of units for sale']

            median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, earliest_median_rent_price_sqm, earliest_month_1, project_median_sale_price_sqm_1_year_ago, project_median_sale_price_sqm_8_month_ago, median_sale_price = self.get_data_graph(soup)
            # print('DEBUG s_n_of_units_for_rent:', s_n_of_units_for_rent)

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
            result_bulk_2 = {
                'area': area,
            }
            result_bulk_3 = {
                'median_rent_price_sqm': median_rent_price_sqm, # L
                's_size': s_size, #
                'bd1_size': bd1_size,
                'bd2_size': bd2_size,
                'bd3_size': bd3_size,
                'bd4_size': bd4_size, # Q
                'median_sale_price_sqm': median_sale_price_sqm,
                's_n_of_units_for_sale': s_n_of_units_for_sale,
                'bd1_n_of_units_for_sale': bd1_n_of_units_for_sale,
                'bd2_n_of_units_for_sale': bd2_n_of_units_for_sale,
                'bd3_n_of_units_for_sale': bd3_n_of_units_for_sale,
                'bd4_n_of_units_for_sale': bd4_n_of_units_for_sale, # W
                'earliest_median_rent_price_sqm': earliest_median_rent_price_sqm, # X
                'earliest_month_1': earliest_month_1,
                'earliest_median_sale_price_sqm': earliest_median_sale_price_sqm, # Z
                'earliest_month': earliest_month,
                'total_units': total_units, # AB col
                'part2_28_09-1': s_n_of_units_for_rent,
                'part2_28_09-2': self.check_outlier(s_av_rent,0),
                'part2_28_09-3': self.check_outlier(s_av_ask_price,0),
                'part2_28_09-4': bd1_n_of_units_for_rent,
                'part2_28_09-5': self.check_outlier(bd1_av_rent,0),
                'part2_28_09-6': self.check_outlier(bd1_av_ask_price,0),
                'part2_28_09-7': bd2_n_of_units_for_rent,
                'part2_28_09-8': self.check_outlier(bd2_av_rent,0),
                'part2_28_09-9': self.check_outlier(bd2_av_ask_price,0),
                'part2_28_09-10': bd3_n_of_units_for_rent,
                'part2_28_09-11': self.check_outlier(bd3_av_rent,0),
                'part2_28_09-12': self.check_outlier(bd3_av_ask_price,0),
                'part2_28_09-13': bd4_n_of_units_for_rent,
                'part2_28_09-14': self.check_outlier(bd4_av_rent,0),
                'part2_28_09-15': self.check_outlier(bd4_av_ask_price,0),
                'start_from': start_from, # Lowest rent # AR col
                'sqm': sqm,
                'lowest_ask_price': lowest_ask_price, # AT col
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
            url_list = [link["link"] for link in self.source_links if link["link"] != ""]
            row_idx = url_list.index(url) + 2
            location = result_bulk_1['province'] + '/' + result_bulk_1['city'] + '/' + result_bulk_2['area']
            if result_bulk_1:
                self.work_sheet.update_value(addr=(row_idx, 2), val=result_bulk_1['condo_name']) #project name
                self.work_sheet.update_value(addr=(row_idx, 3), val=result_bulk_1['developer_name'])
                self.work_sheet.update_value(addr=(row_idx, 4), val=result_bulk_1['province'])
                self.work_sheet.update_value(addr=(row_idx, 5), val=result_bulk_1['city'])
                self.work_sheet.update_value(addr=(row_idx, 7), val=result_bulk_1['city'])# city final (column G)

            if result_bulk_2:
                # self.write_to_json('data/file_b2.json', b2)
                self.work_sheet.update_value(addr=(row_idx, 8), val=result_bulk_2['area'])
                self.work_sheet.update_value(addr=(row_idx, 10), val=result_bulk_2['area'])
                self.work_sheet.update_value(addr=(row_idx, 11), val=location)# Location (column K)
            if result_bulk_3:
                # self.write_to_json('data/file_b3.json', b3)
                self.work_sheet.update_row(
                    index=row_idx,
                    values=[
                        result_bulk_3['median_rent_price_sqm'],
                        result_bulk_3['s_size'],
                        result_bulk_3['bd1_size'],
                        result_bulk_3['bd2_size'],
                        result_bulk_3['bd3_size'],
                        result_bulk_3['bd4_size'],
                        result_bulk_3['median_sale_price_sqm'],
                        result_bulk_3['s_n_of_units_for_sale'],
                        result_bulk_3['bd1_n_of_units_for_sale'],
                        result_bulk_3['bd2_n_of_units_for_sale'],
                        result_bulk_3['bd3_n_of_units_for_sale'],
                        result_bulk_3['bd4_n_of_units_for_sale'],
                        result_bulk_3['earliest_median_rent_price_sqm'],
                        result_bulk_3['earliest_month_1'],
                        result_bulk_3['earliest_median_sale_price_sqm'],
                        result_bulk_3['earliest_month'],
                        result_bulk_3['total_units'],
                        result_bulk_3['part2_28_09-1'],
                        result_bulk_3['part2_28_09-2'],
                        result_bulk_3['part2_28_09-3'],
                        result_bulk_3['part2_28_09-4'],
                        result_bulk_3['part2_28_09-5'],
                        result_bulk_3['part2_28_09-6'],
                        result_bulk_3['part2_28_09-7'],
                        result_bulk_3['part2_28_09-8'],
                        result_bulk_3['part2_28_09-9'],
                        result_bulk_3['part2_28_09-10'],
                        result_bulk_3['part2_28_09-11'],
                        result_bulk_3['part2_28_09-12'],
                        result_bulk_3['part2_28_09-13'],
                        result_bulk_3['part2_28_09-14'],
                        result_bulk_3['part2_28_09-15'],
                        result_bulk_3['start_from'],
                        result_bulk_3['sqm'],
                        result_bulk_3['lowest_ask_price'],
                        result_bulk_3['sqm_ask'],
                        result_bulk_3['number_of_studios'],
                        result_bulk_3['lat'],
                        result_bulk_3['long'],
                        result_bulk_3['other_projects_nearby']
                    ],
                    col_offset=11
                )
            self.work_sheet.update_value(addr=(row_idx, 53), val=location)
            base_url = 'https://www.dotproperty.co.th/en/condos-for-sale/'
            self.work_sheet.update_value(addr=(row_idx, 63), val=str(base_url + location).replace(' ', '-')) # BK - column
            # return result_bulk_1, result_bulk_2, result_bulk_3, result_bulk_4, result_bulk_5
        except Exception as e:
            print(e)
            return None, None, None, None, None
        # print(soup)
    # --------------------------------------------------------

    def scrape_room_types_prices(self, soup):
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

    def scrape_room_types_prices_ext(self, soup):
        result = []
        table_0 = soup.find('div', {'class':'container-table'})
        if table_0:
            table = table_0.find_all('div',{'class':'column text-center'})
            for row in table:
                row_dict = {}
                row_data_raw = row.find_all('div',{'class':'cell'})
                try:
                    size = [int(s) for s in row_data_raw[1].text.split('m')[0].split() if s.isdigit()][0]
                except:
                    size = ''
                try:
                    number_of_units_for_rent = [int(s) for s in row_data_raw[2].text.split('For rent')[1].split('(')[1].split(')')[0].split() if s.isdigit()][0]
                except:
                    number_of_units_for_rent = 0
                try:
                    number_of_units_for_sale = [int(s) for s in row_data_raw[2].text.split('For sale')[1].split('(')[1].split(')')[0].split() if s.isdigit()][0]
                except:
                    number_of_units_for_sale = 0
                try:
                    average_rent = [int(s) for s in row_data_raw[2].text.replace(',','').split('For rent')[1].split('(')[0].split() if s.isdigit()][0]
                except:
                    average_rent = ''
                try:
                    average_ask_price = [int(s) for s in row_data_raw[2].text.replace(',','').split('For sale')[1].split('(')[0].split() if s.isdigit()][0]
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

        # print('---DEBUG---')
        # print(result, len(result))
        return result

    def scrape_rent_units_listing(self, soup):
        try:
            table = soup.find_all('tr', {'data-tenure': 'rent'})
            # temporarily turn off this filter 
            min_price = 10000000000
            num_check_for_outlier = 9999

            for row in table:
                price_row_text = row.find('span', {'class': 'price'}).text
                price_str = price_row_text.split()[1]
                # if ',000' not in price_str:
                #     price_str = '{},000'.format(price_str)
                if any(char.isdigit() for char in price_str):# and '.' not in price_str:
                    if ' - ' in price_row_text:
                        price_str_multiplied = '{}000'.format(price_str)
                        price_int = int(price_str_multiplied.replace('.' , ''))
                       # print('MULTIPLIED', price_int)
                    else:
                       # print('YES', price_str)
                        price_int = int(price_str.replace(',' , ''))
                       # print(price_int)

                    if price_int < min_price: # and price_int >= 7000: # 26.10 filter >=7000
                    # if price_int < min_price and price_int > num_check_for_outlier: -- # temporarily turn off this filter
                        sqm = row.find_all('td')[1].text.split()[0].strip()
                        min_price = price_int
            # print(min_price, sqm)
            return min_price, sqm

        except:
            return '', ''

    def scrape_rent_sale_listing(self, soup):
        try:
            table = soup.find_all('tr', {'data-tenure': 'sale'})
            # temporarily turn off this filter 
            min_price = 10000000000
            num_check_for_outlier = 999999

            for row in table:
                price_str = row.find('span', {'class': 'price'}).text.split()[1]
                if ',' in price_str:
                    price_int = int(price_str.replace(',' , ''))

                    if price_int < min_price: # and price_int >= 919500: # 26.10 filter >=919500
                    # if price_int < min_price and price_int > num_check_for_outlier: - # temporarily turn off this filter
                        sqm = row.find_all('td')[1].text.split()[0].strip()
                        min_price = price_int

            return min_price, sqm

        except:
            return '',''

    def scrape_other_projects_nearby(self, soup):
        other_projects_nearby = None
        result = ''
        sections = soup.find_all('section')
        for section in sections:
            if section.find('h2', string='Other projects nearby'):
                other_projects_nearby = section.find('div', {'class': 'col-md-8'}).find_all('span')
                break

        if other_projects_nearby:
            for entry in other_projects_nearby:
                result += '{}; '.format(entry.text)
            result = result[:-2]

        return result

    def scrape_popular_condos_in_area(self, soup):
        try:
            popular_condos_in_area = []
            popular_condos_in_area_block = soup.find('div', {'class': 'panel-body'}).find_all('div', {'class':'detail-block col-lg-8 left-block'})
            for condo in popular_condos_in_area_block:
                popular_condos_in_area.append(condo.find('h3').text.strip())
            result_str = ", ".join(popular_condos_in_area)
            return result_str
        except:
            return ''

    def get_data_graph(self, soup):
        try:
            """r = requests.get(url, headers=headers_xml, timeout=30)
            print(r.text)
            if r.status_code != 200:
                print('status_code', r.status_code)
                return None"""
            # r = self.selenium_get_source_code(url)
            for script in soup.find_all('script'):
                if 'sqmRent' in script.text:
                    data = script.text
            try:
                median_rent_price_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[0].split(',')[
                    -1]
            except:
                median_rent_price_sqm = ''
            try:
                earliest_median_rent_prices_sqm = data.split("'sqmRent': {")[1].split("data:[")[1].split("],")[
                    0].split(',')
            except:
                earliest_median_rent_price_sqm = ''
            try:
                median_sale_price_sqm = data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[
                    -1]
            except:
                median_sale_price_sqm = ''
            try:
                earliest_median_sale_prices_sqm = data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[
                    0].split(',')
            except:
                earliest_median_sale_prices_sqm = ''

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
                earliest_month = ''

            try:
                # TODO soup find
                earliest_median_rent_price_sqm = ''
                if earliest_median_rent_prices_sqm == '':
                    raise Exception
                month_num = 0
                for price in earliest_median_rent_prices_sqm:
                    month_num += 1
                    if price != '':
                        earliest_median_rent_price_sqm = price
                        break

                months = data.split("labels: [")[1].split("],")[0].split(",")
                earliest_month_1 = months[month_num - 1].replace('"', '')
            except:
                earliest_month_1 = ''

            try:
                project_median_sale_price_sqm_1_year_ago = \
                    data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[-13:-12][0]
            except:
                project_median_sale_price_sqm_1_year_ago = ''
            try:
                project_median_sale_price_sqm_8_month_ago = \
                    data.split("'sqmSale': {")[1].split("data:[")[1].split("],")[0].split(',')[-9:-8][0]
            except:
                project_median_sale_price_sqm_8_month_ago = ''
            try:
                median_sale_price = data.split("'sale': {")[1].split("data:[")[1].split("],")[0].split(',')[-1]
            except:
                median_sale_price = ''

                # logger.debug("get_data_graph:" ,median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, earliest_median_rent_price_sqm, earliest_month_1)
            return median_rent_price_sqm, median_sale_price_sqm, earliest_median_sale_price_sqm, earliest_month, earliest_median_rent_price_sqm, earliest_month_1, project_median_sale_price_sqm_1_year_ago, project_median_sale_price_sqm_8_month_ago, median_sale_price
        except requests.exceptions.RequestException as e:
            self.logger.debug(e)
        return '', '', '', '', '', '', '', '', ''

    def check_outlier(self, num_or_spare, number_less, number_more=None):
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

    def write_to_json(self, file_name, data):
        # with self.global_lock:
        if os.path.exists(file_name):
            # func update data
            with open(file_name, 'r+') as jsonfile:
                j_data = json.load(jsonfile)
            j_data.append(data)
            with open(file_name, 'w+') as jsonfile:
                json.dump(j_data, jsonfile, indent=4)
            self.logger.debug('links in json was update')
        else:
            with open(file_name, 'w+') as jsonfile:
                to_write = []
                to_write.append(data)
                json.dump(to_write, jsonfile, indent=4)
                self.logger.debug('link was insert to json')

    def main(self):
        self.work_sheet.clear(start='B2', end='ZZ9999')
        self.save_source_links_to_sheet()
        url_list = [link["link"] for link in self.source_links if link["link"] != ""]
        for url in url_list:
            self.parse_data(url)
        # self.pool.map(self.parse_data, sorted(url_list))
        # self.pool.close()
        # self.pool.join()

        self.logger.debug('Script complite!!!!')


if __name__ == "__main__":
    parser = ThBkCondosParser()
    parser.main()
