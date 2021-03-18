import time
import requests
# import yaml
from bs4 import BeautifulSoup


headers_property24 = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data',
    'Host': 'www.property24.com.ph',
    'Origin': 'https://www.property24.com.ph',
    'Referer': 'https://www.property24.com.ph/broker-agency/teody-embrado/395414',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def scrape_email_by_id(): #id later
    try:
        url = 'https://www.property24.com.ph/Agencies/AgencyFullContact?id=395414&ContactType=Email'
        r = requests.post(url, headers=headers_property24, timeout=35)
        if r.status_code != 200:
            print('status_code', r.status_code)
            return None
        return r.content
    except Exception as e:
        print('Error - {}'.format(e))


if __name__ == "__main__":
    print(scrape_email_by_id())