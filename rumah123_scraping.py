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

URL_base = 'https://www.rumah123.com/'

def make_request(url, method='get', proxies=proxies, timeout=15, t='rumah123'):
    host_str = url.replace('https://','')
    headers_rumah123 = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data',
    'Host': 'www.rumah123.com',
    'Referer': 'https://www.rumah123.com/en/property-agent/',
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


    if t == 'rumah123':
        headers = headers_rumah123
    else:
        headers = headers_agenproperti123

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
                result = r.content
                return result
            else:
                print(url, r.status_code)
                time.sleep(1)
        except Exception as e:
            print(i, url, e)


def count_pages():
    res = make_request('https://www.rumah123.com/en/property-agent/?search_key=city&search_value=jawa+barat&language=')
    soup = BeautifulSoup(res, 'html.parser')
    count_agents_str = soup.find('div', {'class': 'serp-listing agent-listing list-view'}).find('h1').find('small').text
    count_agents = int(''.join(re.findall(r'\d+', count_agents_str)))
    count_pages = math.ceil(count_agents / 10)
    print(f"count_pages, {count_pages}")

    return count_pages


def collect_agent_pages_links(count_pages, page_start, page_end):
    agent_pages_links = set()
    for i in range(page_start, page_end): # TODO: start position to argparse
        res = make_request(f'{URL_base}/en/property-agent/?search_key=city&search_value=jawa+barat&language=&page={i}')
        soup = BeautifulSoup(res, 'html.parser')
        listing_titles = soup.find_all('h2', {'class': 'listing-title'})
        for title in listing_titles:
            link = title.find('a')['href']
            print('collect_agent_pages_links:', link)
            agent_pages_links.add(link)
    
    return agent_pages_links


def scrape_agent_profile_URL(url):
    print('scrape_agent_profile_URL start:', url)
    res = make_request(url)
    soup = BeautifulSoup(res, 'html.parser')
    full_name = soup.find('div', {'class': 'cover-info'}).find('h1').text.strip()
    try:
        website_hrefs = soup.find('div', {'class': 'widget agent-info-widget'}).find_all('a')
        website = website_hrefs[-1]['href']
    except:
        website = ''
    
    if website != '' and ' ' not in website and '@' not in website and '_' not in website:
        print('start fetching email/phone from website:', website)
        res1 = make_request(website, t='agenproperti123')
        # save_html_file = open('response_agenproperti123.html', 'wb')
        # save_html_file.write(res1)
        if res1:
            soup = BeautifulSoup(res1, 'html.parser')
            
            p_classes_text = soup.find('div', {'class': 'home-cover'}).find_all('p', {'class': 'text-center'})
            # print(p_classes_text)
            try:
                email = p_classes_text[-1].find('a').text.strip()
            except:
                email = ''
            try:
                phone = p_classes_text[0].find('a').text.strip()
            except:
                phone = ''

            print('scrape_agent_profile_URL finished:', full_name, website, email, phone)
            return full_name, website, url, email, phone
        
        else:
            return None, None, None, None, None
    
    else:
        print('scrape_agent_profile_URL cancelled:', full_name, website)
        return full_name, website, url, '', ''



if __name__ == "__main__":
    page_start, page_end = 1, 80 # 1 min, 1185 max
    print('range_pages:', page_start, page_end)

    count_pages = count_pages()
    agent_profile_URLs = collect_agent_pages_links(count_pages, page_start, page_end)

    result_matrix = []

    for agent_profile_URL in agent_profile_URLs:
        full_name, website, url, email, phone = scrape_agent_profile_URL(agent_profile_URL)
        if full_name:
            
            result_matrix.append({
                'Full name': full_name,
                'Website': website,
                'Agent profile URL': url,
                'E-mail': email,
                'Phone': phone
            })
    

    df_result = pd.DataFrame(result_matrix)
    df_result.to_csv('output_rumah123_search_value_jawa_barat.csv'.format(page_start, page_end), index=False)