import argparse
import random
import math
import time
import requests

import re
from bs4 import BeautifulSoup
import pandas as pd


proxies = {
 "http": "http://5.79.73.131:13010",
 "http": "https://5.79.73.131:13010",
}

URL_base = 'https://www.rumahku.com'

def make_request(url, method='get', proxies=proxies, timeout=15, t='rumahku'):
    host_str = url.replace('https://','')
    headers_rumahku = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data',
    'Host': 'www.rumahku.com',
    'Referer': 'https://www.rumahku.com/',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1{}_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.390{}.70 Safari/537.36'.format(random.randint(1,9), random.randint(1,9)),
    'X-Requested-With': 'XMLHttpRequest'
    }
    headers_agenproperti123 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # Cookie: _gcl_au=1.1.302680934.1578855319; _fbp=fb.1.1578855318763.1559311339; _hjid=3ddfa058-447c-4ab6-bbcc-b4bc87105854; _ga=GA1.2.1763266020.1578855385; _gid=GA1.2.666999625.1580058351; CAKEPHP=bjcv14aurhu03us2aegulm2e54; _ga=GA1.3.1763266020.1578855385; _gid=GA1.3.666999625.1580058351; _hjIncludedInSample=1; _gat_UA-85157164-4=1
    'Host': '{}'.format(host_str),
    # 'Referer': 'https://www.rumah123.com/en/property-agent/hg-jason-property/git-hua-276/',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    }


    if t == 'rumahku':
        headers = headers_rumahku
    else:
        headers = headers_agenproperti123

    i=0
    result = None
    while not result and i < 20:
        i+=1
        try:
            if method=='get':
                if proxies:
                    r = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
                else:
                    r = requests.get(url, headers=headers, timeout=timeout)
            else:
                if proxies:
                    r = requests.post(url, headers=headers, timeout=timeout, proxies=proxies)
                else:
                    r = requests.post(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                result = r.content
                return result
            else:
                print(url, r.status_code)
                time.sleep(1)
        except Exception as e:
            print(i, url, e)


def count_pages():
    res = make_request('https://www.rumahku.com/users/agencies/', proxies=None)
    soup = BeautifulSoup(res, 'html.parser')
    agency_names_raw = soup.find_all('h1', {'class': 'property-list-name'})
    print(agency_names_raw, len(agency_names_raw))

    """
    count_agents = int(''.join(re.findall(r'\d+', count_agents_str)))
    count_pages = math.ceil(count_agents / 10)
    print(f"count_pages, {count_pages}")
    """

    return agency_names_raw


def collect_agent_pages_links(count_pages, page_start, page_end):
    agency_pages_links = set()
    for i in range(page_start, page_end):
        res = make_request(f'https://www.rumahku.com/users/agencies/current_region_id:19/region_id:19/page:{i}/')
        soup = BeautifulSoup(res, 'html.parser')
        agency_names_raw = soup.find_all('h1', {'class': 'property-list-name'})
        for agency_raw in agency_names_raw:
            link = agency_raw.find('a')['href']
            print('collect_agency_pages_links:', link)
            agency_pages_links.add(link)
    
    return agency_pages_links


def scrape_agency_profile_URL(url):
    print('scrape_agency_profile_URL start:', url)
    res = make_request(f'{URL_base}{url}')
    soup = BeautifulSoup(res, 'html.parser')
    agency_name = soup.find('h1', {'class': 'head-title'}).text.strip()
    
    try:
        email_raw = soup.find('div', {'id': 'where-you-are'}).find_all('p')[-1].text.strip()
        if 'Email:' in email_raw:
            email = email_raw.replace('Email:','').strip()
        else:
            email = ''
    except:
        email = ''
    
    print(agency_name, email, url)
    return agency_name, email, url



if __name__ == "__main__":
    page_start, page_end = 1, 11 # 1 min, 53 max
    try:
        agency_profile_URLs = collect_agent_pages_links(count_pages, page_start, page_end)

        result_matrix = []
        
        for agency_profile_URL in agency_profile_URLs:
            agency_name, email, url = scrape_agency_profile_URL(agency_profile_URL)
            if agency_name:
                
                result_matrix.append({
                    'Agency name': agency_name,
                    'Agency profile URL': f'{URL_base}{url}',
                    'E-mail': email
                })

    finally:
        df_result = pd.DataFrame(result_matrix)
        df_result.to_csv('output_rumahku_region_id_19.csv'.format(page_start, page_end), index=False)