import requests
from bs4 import BeautifulSoup


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # Cookie: _gcl_au=1.1.302680934.1578855319; _fbp=fb.1.1578855318763.1559311339; _hjid=3ddfa058-447c-4ab6-bbcc-b4bc87105854; _ga=GA1.2.1763266020.1578855385; _gid=GA1.2.666999625.1580058351; CAKEPHP=bjcv14aurhu03us2aegulm2e54; _ga=GA1.3.1763266020.1578855385; _gid=GA1.3.666999625.1580058351; _hjIncludedInSample=1; _gat_UA-85157164-4=1
    'Host': 'giethua.agenproperti123.com',
    # 'Referer': 'https://www.rumah123.com/en/property-agent/hg-jason-property/git-hua-276/',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

r = requests.get('https://giethua.agenproperti123.com/', headers=headers)
print(r.status_code)
save_html_file = open('response_agenproperti123_test.html', 'wb')
save_html_file.write(r.content)