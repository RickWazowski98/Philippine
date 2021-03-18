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

URL_base = 'https://www.rumah.com/'

def make_request(url, method='get', proxies=proxies, timeout=15, t='rumah'):
    host_str = url.replace('https://','')
    headers_rumah = {
    'authority': 'www.rumah.com',
    'method': 'GET',
    'path': '/agen-properti/search/2',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '__cfduid=d7186f0ddf5442467a00769d932b3a5861580058319; PHPSESSID=0f0g0co0qq6kofj1b9fhs9o0k4; sixpack_client_id=2681EC0B-1389-4BEC-739B-432F17FBF413; Visitor=3b2eefcd-f424-4855-8519-d19016ebcb4a; _ga=GA1.2.138683465.1580058322; welcomeBackModalVisited=true; ajs_group_id=null; D_IID=B9E9DD59-A762-3AEA-960A-5C1E6B682334; D_UID=5D5EE519-E818-3B00-9641-78559279DD60; D_ZID=4A5B3226-9C8F-3684-9D90-570A164C58FA; D_ZUID=BC9AD84B-849F-30CC-9284-39D5140A8C8B; D_HID=1F23FD97-4FD8-3002-809E-622592701C6B; D_SID=178.65.241.157:JT4hqiFv6Me61THMIioo4GsQkHFFez8FzeRuPAYp5Zc; _fbp=fb.1.1580058325046.88390555; ajs_user_id=%227b299e14-ff97-4188-8a70-06667e86daae%22; ajs_anonymous_id=%22b8d93a46-5b7d-4520-b617-20becd235e63%22; _gid=GA1.2.303445303.1580758549; _gat=1; _gat_regionalTracker=1',
    'referer': 'https://www.rumah.com/agen-properti/search/1',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1{}_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.390{}.70 Safari/537.36'.format(random.randint(1,9), random.randint(1,9)),
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


    if t == 'rumah':
        headers = headers_rumah
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
                print(result)
                return result
            else:
                print(url, r.status_code)
                time.sleep(1)
        except Exception as e:
            print(i, url, e)


def count_pages():
    res = make_request('https://www.rumah.com/agen-properti/search/2')
    soup = BeautifulSoup(res, 'html.parser')
    count_agents_str = soup.find('div', {'class': 'agent-results-title'})
    # count_agents = int(''.join(re.findall(r'\d+', count_agents_str)))
    # count_pages = math.ceil(count_agents / 10)
    # print(f"count_pages, {count_pages}")

    print(count_agents_str)

    return count_agents_str


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
    """
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
    """