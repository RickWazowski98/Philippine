import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

headers_ind_brokers = {
    'Cookie': 'SERVERID=A; __cfduid=df67f42c8989d66be673b0792c315049f1581269983; _gcl_au=1.1.1597115442.1581269986; _ga=GA1.3.502199446.1581269986; _gid=GA1.3.1434534760.1581269986; _ym_uid=1581269987994501000; _ym_d=1581269987; _ym_visorc_56443120=w; _ym_isad=1; sidtb=OvO2SgDId1KyybB06iuuFXhh9h8XYpgL; usidtb=jxQJm65jXVqeyDh17nDiE7Hq5v8yMjAc; ASP.NET_SessionId=onwjvlbkue1pctlfxdclb4gg; ins-gaSSId=53e229a3-d452-90e6-1bfe-9a25df9af66f_1581269990; __zlcmid=wfituhJq0MXQ9w; ins-product-id=eb2778; BROKER_TYPE=%7B%22BrokerType%22%3A0%7D; _gat_UA-3729099-1=1; insdrSV=13'
}

def get_links_agency(page_start=1, page_end=180): # SET page_end
    links = set()
    for i in range(page_start, page_end):
        url = f"https://batdongsan.com.vn/nha-moi-gioi-tp-hcm/p{i}"
        print(url)
        r = requests.get(url, timeout = 10, headers=headers_ind_brokers)
        soup = BeautifulSoup(r.content, 'html.parser')
        agency_blocks = soup.find_all('div', {'class': 'ttmgl'})
        for block in agency_blocks:
            link = block.find('h3').find('a')['href']
            links.add(link)
            print(link)

        time.sleep(1)
    
    return links


def get_info_from_profile_url(profile_url):
    url = f"https://batdongsan.com.vn{profile_url}"
    print(url)
    r = requests.get(url, timeout = 20, headers=headers_ind_brokers)
    # print(r.status_code)
    soup = BeautifulSoup(r.content, 'html.parser')
    try:
        full_name = soup.find('div', {'class': 'ttmg'}).find('h1').text.strip()
    except:
        full_name = ''
    try:
        email = soup.find('div', {'class': 'broker-link'}).find('a')['data-email'].strip()
    except:
        email = ''
    
    return full_name, url, email




if __name__ == "__main__":
    
    links_agencies = get_links_agency()
    # print(links_agencies, len(links_agencies))



    result_matrix = []
    for link in links_agencies:
        time.sleep(1)
        full_name, url, email = get_info_from_profile_url(link)
        result_matrix.append({
            'Full name': full_name,
            'profile URL': url,
            'E-mail': email
        })
        
    df_result = pd.DataFrame(result_matrix)
    df_result.to_csv('output_batdongsan-brokers-nha-moi-gioi-tp-hcm.csv', index=False)

    
    # JUST TEST
    # print(get_info_from_profile_url('/ban-dat-nen-du-an/cong-ty-cp-nguoi-cong-su-chuyen-nghiep-eb904'))
    # print(get_info_from_profile_url('/ban-dat-nen-du-an/cong-ty-co-eb1246'))