import requests


proxies = {
 "http": "http://5.79.73.131:13010",
 "http": "https://5.79.73.131:13010",
}

URL_target = 'https://filipinohomes.com/juanito-jr--tiongson'

headers = {
    'authority': 'www.klungbaan.com',
    'method': 'GET',
    'path': '/agents-chiang-mai/',
    'scheme': 'https',
    }

# r = requests.get(URL_target, timeout=30, headers=headers, proxies=proxies)  
r = requests.get(URL_target, timeout=120)  
print(r.status_code)

with open(f"page_source_test_{URL_target.split('/')[-1]}.html", "w") as page_source_file:
    page_source_file.write(r.text)







"""
URL_target = 'https://batdongsan.com.vn/nha-moi-gioi'

headers = {
    'Cookie': 'SERVERID=A; __cfduid=df67f42c8989d66be673b0792c315049f1581269983; _gcl_au=1.1.1597115442.1581269986; _ga=GA1.3.502199446.1581269986; _gid=GA1.3.1434534760.1581269986; _ym_uid=1581269987994501000; _ym_d=1581269987; _ym_visorc_56443120=w; _ym_isad=1; sidtb=OvO2SgDId1KyybB06iuuFXhh9h8XYpgL; usidtb=jxQJm65jXVqeyDh17nDiE7Hq5v8yMjAc; ASP.NET_SessionId=onwjvlbkue1pctlfxdclb4gg; ins-gaSSId=53e229a3-d452-90e6-1bfe-9a25df9af66f_1581269990; __zlcmid=wfituhJq0MXQ9w; ins-product-id=eb2778; BROKER_TYPE=%7B%22BrokerType%22%3A0%7D; _gat_UA-3729099-1=1; insdrSV=13'
}
"""