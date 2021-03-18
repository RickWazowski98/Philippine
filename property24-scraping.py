import argparse
import random
import math
import time
import requests
# import yaml
from bs4 import BeautifulSoup
import pandas as pd

proxies = {
 "http": "5.79.73.131:13010",
 "https": "5.79.73.131:13010",
}

URL_base = 'https://www.property24.com.ph'

headers_default = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'www.property24.com.ph',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
}

def make_request(url, method='get', proxies=proxies, timeout=15):
    headers_property24 = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data',
    'Host': 'www.property24.com.ph',
    'Origin': 'https://www.property24.com.ph',
    'Referer': '{}{}'.format(URL_base, url),
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1{}_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.390{}.70 Safari/537.36'.format(random.randint(1,9), random.randint(1,9)),
    'X-Requested-With': 'XMLHttpRequest'
    }
    i=0
    result = None
    while not result:
        i+=1
        try:
            if method=='get':
                r = requests.get(url, headers=headers_default, timeout=timeout, proxies=proxies)
            else:
                r = requests.post(url, headers=headers_property24, timeout=timeout, proxies=proxies)
            if r.status_code == 200:
                result = r.content
                return result
        except Exception as e:
            print(i, url, e)


def scrape_email_by_id(): #id later
    try:
        url = 'https://www.property24.com.ph/Agencies/AgencyFullContact?id=395414&ContactType=Email'
        r = requests.post(url, headers=headers_property24, timeout=35, proxies=proxies)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        return r.content
    except Exception as e:
        print('Error - {}'.format(e))


def scrape_area_links():
    url = '{}/Agencies/Suggestions'.format(URL_base)
    try:
        """
        r = requests.get(url, headers=headers_default, timeout=10, proxies=proxies)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        """
        result = make_request(url)
        soup = BeautifulSoup(result, 'html.parser')
        raw_links = soup.find('ul', {'class': 'sc_areasList'}).find_all('a')
        links = []
        for raw_link in raw_links:
            links.append([raw_link['href'], raw_link.text])
        return links

    except Exception as e:
        print('Error - {}'.format(e))


def scrape_links_agencies(soup, area):
    try:
        links = []
        blocks = soup.find_all('div', {'class': 'sc_panel sc_panelHighlight sc_franchiseTile'})
        for block in blocks:
            link = block.find('div', {'class': 'col-xs-8'}).find('a')['href']
            agency_name = block.find('div', {'class': 'col-xs-8'}).find('a').text.strip()
            links.append([link, area, agency_name])
        return links

    except Exception as e:
        print('Error - {}'.format(e))


def get_links_agencies(start_page, area):
    """
    e.g. /brokers-in-metro-manila-p265
    """
    url = '{}{}'.format(URL_base, start_page)
    try:
        links_agencies = []
        """
        r = requests.get(url, headers=headers_default, timeout=20, proxies=proxies)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        """
        result = make_request(url)
        soup = BeautifulSoup(result, 'html.parser')
        count_agencies = int(soup.find('div', {'class': 'sc_pageText pull-right'}).find_all('span')[-1].text.split()[-1].replace(',',''))
        count_pages = math.ceil(count_agencies/20)

        # first page
        links_agencies.extend(scrape_links_agencies(soup, area))
        
        
        for num_page in range(2, count_pages+1):
            # time.sleep(random.randint(1,3))
            attempts = 0
            while attempts < 3:
                url = '{}{}?Page={}'.format(URL_base, start_page, num_page)
                print(url)
                # r = requests.get(url, headers=headers_default, timeout=10, proxies=proxies)
                result = make_request(url)
                """
                if r.status_code != 200:
                    attempts += 1
                    print('attempts:', attempts)
                    # time.sleep(3)
                else:
                """
                soup = BeautifulSoup(result, 'html.parser')
                links = scrape_links_agencies(soup, area)
                print('links agencies to append:', links)
                links_agencies.extend(links)
                break
        
        return links_agencies

    except Exception as e:
        print('Error - {}'.format(e))  
        return []  


def scrape_agency_page(links_brokers, province, agency, url):
    try:
        # r = requests.get('{}{}'.format(URL_base, url), headers=headers_default, timeout=10, proxies=proxies)
        response_agency_page = make_request('{}{}'.format(URL_base, url))
        soup = BeautifulSoup(response_agency_page, 'html.parser')
        # links_brokers = []
        try:
            featured_brokers_raw = soup.find_all('div', {'class': 'sc_profileDetails sc_profileFeaturedAgents'})[-1].find_all('a')
            for broker_raw in featured_brokers_raw:
                broker_name = broker_raw.text
                broker_url = broker_raw['href']
                links_brokers.append([province, agency, broker_url, broker_name])
                print(f'--appending broker links: {broker_url}, name broker: {broker_name}')
            
        except:
            print(f'there are no brokers on {url}')


        # time.sleep(random.randint(1,3))
        id_agency = url.split('/')[-1]
        url_email = 'https://www.property24.com.ph/Agencies/AgencyFullContact?id={}&ContactType=Email'.format(id_agency)
        # r = requests.post(url_email, headers=headers_property24, timeout=15, proxies=proxies)
        res = make_request(url_email, method='post')
        soup = BeautifulSoup(res, 'html.parser')
        # print(soup)
        try:
            email = soup.find('a').text.strip()
            print(email)
        except:
            email = 'Captcha'
            print('email - Captcha')
            # time.sleep(59)
        broker = ''
        url_link = '{}{}'.format(URL_base, url)

        return province, agency, broker, email, url_link

    except Exception as e:
        print('Error - {}'.format(e))

def scrape_broker_page(province, agency, broker, url):
    try:
        response_broker_page = make_request('{}{}'.format(URL_base, url))

        # time.sleep(random.randint(1,3))
        id_broker = url.split('/')[-1]
        url_email = 'https://www.property24.com.ph/Agencies/AgentFullContact?id={}&ContactType=Email'.format(id_broker)
        # r = requests.post(url_email, headers=headers_property24, timeout=15, proxies=proxies)
        res = make_request(url_email, method='post')
        soup = BeautifulSoup(res, 'html.parser')
        # print(soup)
        try:
            email = soup.find('a').text.strip()
            print(email)
        except:
            email = 'Captcha'
            print('email - Captcha')
            # time.sleep(59)
        url_link = '{}{}'.format(URL_base, url)

        return province, agency, broker, email, url_link

    except Exception as e:
        print('Error - {}'.format(e))


if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--area', nargs='+')
    args = parser.parse_args()
    target_area = ' '.join(args.area)
    print(f'target_area = {target_area}')
    """

    # print(scrape_email_by_id())
    # target_areas = ['Metro Manila', 'Cebu', 'Cavite', 'Batangas', 'Laguna', 'Bulacan', 'Rizal']
    try:
        rows_list = []
        links_brokers = []
        # target_areas = [target_area]
        target_areas = ['Masbate', 'Maguindanao', 'Abra', 'Agusan del Sur', 'Batanes', 'Ifugao',
        'Quirino', 'Surigao del Sur', 'Pagadian']
        
        already_scraped_areas = ['Metro Manila', 'Cebu', 'Cavite', 'Batangas', 'Laguna', 'Bulacan', 'Rizal',
        'Misamis Oriental', 'Palawan', 'Negros Occidental', 'Leyte', 'Nueva Ecija',
        'La Union, Zamboanga del Sur', 'Cotabato', 'Sarangani', 'Ilocos Sur', 'Compostela Valley',
        'Capiz', 'Marinduque']
        
        target_areas = [x for x in target_areas if x not in already_scraped_areas]
        print(target_areas)
        # Metro Manila, Cebu, Cavite, Batangas, Laguna, Bulacan and Rizal
        
        # df_result = pd.DataFrame(columns=['Area', 'Agency', 'Broker', 'E-mail', 'URL'])
        
        area_links = scrape_area_links()
        # print(area_links)
        for link, area in area_links:
            print(link, area)
            if area in target_areas:
                links_agencies = get_links_agencies(link, area)
                for link, area, agency in links_agencies:
                    print(link, area, agency)
                    province, agency, broker, email, url_link = scrape_agency_page(links_brokers, area, agency, link)
                    # # time.sleep(random.randint(5,9))
                    print(province, agency, broker, email, url_link)
                    rows_list.append({
                        'Area': province,
                        'Agency': agency,
                        'Broker': broker,
                        'E-mail': email,
                        'URL': url_link
                    })
                print('===START BROKERS===')
                print(links_brokers)
                for area, agency, broker_url, broker_name in links_brokers:
                    province, agency, broker, email, url_link = scrape_broker_page(area, agency, broker_name, broker_url)
                    print(province, agency, broker, email, url_link)
                    rows_list.append({
                        'Area': province,
                        'Agency': agency,
                        'Broker': broker,
                        'E-mail': email,
                        'URL': url_link
                    })

    except Exception as e:
        print('Error - {}'.format(e))
    
    finally:
        # area_str = target_area.replace(' ','_')
        df_result = pd.DataFrame(rows_list)
        # df_result.to_csv(f'output_property24_{area_str}.csv', index=False)
        df_result.to_csv('output_property24_rest_7.csv', index=False)
    

    # print(get_links_agencies('/brokers-in-metro-manila-p265', 'Metro Manila'))
    # print(scrape_agency_page('/broker-agency/joan-silvano/396241'))