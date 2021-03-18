import json
import logging
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml


def get_data_projects(urls):
    result = []
    for url in urls:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        soup = BeautifulSoup(r.content, 'html.parser')

        project_links = soup.find('div', {'id': 'search-results'}).find_all('a')
        
        for link in project_links:
            if link['href'] and link['href'] not in result:
                result.append(link['href'])
    
    return result


if __name__ == "__main__":
    result = get_data_projects([
        # 'https://www.dotproperty.com.ph/condos/all/cebu',
        'https://www.dotproperty.com.ph/condos/all',
        'https://www.dotproperty.com.ph/condos/all?page=2',
        'https://www.dotproperty.com.ph/condos/all?page=3',
        'https://www.dotproperty.com.ph/condos/all?page=4',
        'https://www.dotproperty.com.ph/condos/all?page=5',
        'https://www.dotproperty.com.ph/condos/all?page=6',
        'https://www.dotproperty.com.ph/condos/all?page=7',
        'https://www.dotproperty.com.ph/condos/all?page=8',
        'https://www.dotproperty.com.ph/condos/all?page=9',
        'https://www.dotproperty.com.ph/condos/all?page=10',
        'https://www.dotproperty.com.ph/condos/all?page=11',
        'https://www.dotproperty.com.ph/condos/all?page=12',
        'https://www.dotproperty.com.ph/condos/all?page=13',
        'https://www.dotproperty.com.ph/condos/all?page=14',
        'https://www.dotproperty.com.ph/condos/all?page=15',
        'https://www.dotproperty.com.ph/condos/all?page=16',
        'https://www.dotproperty.com.ph/condos/all?page=17',
        'https://www.dotproperty.com.ph/condos/all?page=18',
        'https://www.dotproperty.com.ph/condos/all?page=19',
        'https://www.dotproperty.com.ph/condos/all?page=20',
        'https://www.dotproperty.com.ph/condos/all?page=21',
        'https://www.dotproperty.com.ph/condos/all?page=22',
        'https://www.dotproperty.com.ph/condos/all?page=23',
        'https://www.dotproperty.com.ph/condos/all?page=24',
        'https://www.dotproperty.com.ph/condos/all?page=25',
        'https://www.dotproperty.com.ph/condos/all?page=26',
        'https://www.dotproperty.com.ph/condos/all?page=27',
        'https://www.dotproperty.com.ph/condos/all?page=28',
        'https://www.dotproperty.com.ph/condos/all?page=29',
        'https://www.dotproperty.com.ph/condos/all?page=30',
        'https://www.dotproperty.com.ph/condos/all?page=31',
        'https://www.dotproperty.com.ph/condos/all?page=32',
        'https://www.dotproperty.com.ph/condos/all?page=33',
        'https://www.dotproperty.com.ph/condos/all?page=34',
        'https://www.dotproperty.com.ph/condos/all?page=35'
    ])

    file_object = open('data/links.json', 'w')
    json.dump(result, file_object, indent=4)

    # TODO: other pages