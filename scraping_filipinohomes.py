"""
https://filipinohomes.com/agents

Can u select all locations, then scrape all names and e-mail addresses of all agents of each location? Site seems to be slow though.
"""

import requests
# import time
from bs4 import BeautifulSoup
import pandas as pd
import json
import csv


# https://filipinohomes.com/agents?2//2
# all provinces: 79
base_url = 'https://filipinohomes.com/'

"""
all_provinces_range = range(1,81)
for i in all_provinces_range:
    print(i)
"""

def make_request(url, timeout=120, attempts=10):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Host': 'filipinohomes.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    res = None
    count_attempts = 0
    while res == None and count_attempts < attempts:
        try:
            count_attempts+=1
            r = requests.get(url, timeout=timeout, headers=headers)
            print(r.status_code, count_attempts, url)
            res = r.content
            soup = BeautifulSoup(r.content, 'html.parser')

            return soup
    
        except Exception as e:
            print(e)
            return None


def scrape_prov_page(url, count_location):
    reluts_lst = []
    current_page = 1
    s = make_request(f'{url}{str(current_page)}')
    if s:
        location = s.find('select', {'name': 'province'}).find_all('option')[count_location].text
        print('location', location)

        prov_list_raw = s.find('select', {'class': 'form-control'})
        list_prov = []
        for prov in prov_list_raw:
            list_prov.append(prov.text)
        
        last_page_num_block = s.find('ul', {'class': 'pagination'})
        last_page_num_raw = last_page_num_block.find("a", text="Last")['href']
        print(last_page_num_raw)
        
        rr = procces_prov_page(s)
        print(rr)
        for en in rr:
            # reluts_lst.append({
            #     'Location': location,
            #     'Name': en[0],
            #     'Email': en[1]
            # })
            entry = {
                'Location': location,
                'Name': en[0],
                'Email': en[1]
            }
            line = [location, en[0], en[1]]
            # file_object = open(f"filipinohomes_result.json", 'a')
            # json.dump(entry, file_object, indent=4)
            with open('filipinohomes_result.csv', "a") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    writer.writerow(line)

        try:
            last_page_num = int(last_page_num_raw.split('//')[-1])
        except:
            last_page_num = 1
        
        # current_page = url.split('//')[-1]
        while current_page < last_page_num:
            current_page+=1
            s = make_request(f'{url}{str(current_page)}')
            rr = procces_prov_page(s)
            print(rr)
            for en in rr:
                # reluts_lst.append({
                #     'Location': location,
                #     'Name': en[0],
                #     'Email': en[1]
                # })
                entry = {
                    'Location': location,
                    'Name': en[0],
                    'Email': en[1]
                    }
                line = [location, en[0], en[1]]
                # file_object = open(f"filipinohomes_result.json", 'a')
                # json.dump(entry, file_object, indent=4)
                with open('filipinohomes_result.csv', "a") as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow(line)


def procces_prov_page(soup):
    relust_lst = []
    agents_raw = soup.find_all('div', {'class': 'agent-content'})
    i=0
    for agent_div in agents_raw:
        # print(agent_div)
        name_pre = agent_div.find('div', {'class': 'agent-name'}).text.strip()
        print(name_pre)
        email_pre = soup.find_all('ul', {'class': 'agent-contact-details'})[i].find_all('li')[-1].text
        try:
            agent_url_personal = f"{base_url}{agent_div.find('a')['href']}"
            s = make_request(agent_url_personal)
            email_full = s.find('ul', {'class': 'agent-contact-details'}).find_all('li')[-1].text
            email_pre = email_full
            name_full = s.find('div', {'class': 'agent-name'}).find('h4').text.strip()
            name_pre = name_full
        except Exception as e:
            print(email_pre, name_pre, e)
        i+=1
        print(name_pre, email_pre)
        relust_lst.append([name_pre, email_pre])
    
    return relust_lst




if __name__ == "__main__":
    all_provinces_range = range(1,81)
    for count_prov_page in all_provinces_range:
        print(count_prov_page)
        
        scrape_prov_page(f'https://filipinohomes.com/agents?{count_prov_page}//', count_prov_page)