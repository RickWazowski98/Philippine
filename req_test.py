"""import requests
from th_bk_condos_parser import get_proxies


HEADERS = {
    "authority": "www.dotproperty.co.th",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5,en-US;q=0.4",
    "cookie": "__cfduid=d5ab83dc3d72ea34d45bd085e774b913b1613420556; dot_property_group_idu=eyJpdiI6ImVIMmdUaTF5eDZTZjZRMEptcWIwSHc9PSIsInZhbHVlIjoiQnVERUhGd3BqVFFcL2NZalNIMzVNekNYZmx0WlhQRHVBOEJBZGJ0a1pOK0xPNzl1bHhtQVRycElKcmdScWNMSVIiLCJtYWMiOiJkM2Y2MTc1NDkyZTg0ZjY5ZDg5NjhmNzViODM2ZGJiZmUxODQ5OGYyNDA5YzM3ODAzZDk1MDFkNWUyOWZlNzZkIn0%3D; user_language=eyJpdiI6IjczZGU2MkkwUm5JWU12akdBUWYwRmc9PSIsInZhbHVlIjoiczl6dmQ4SGt2YUlsTEhnZk0zTWlUZz09IiwibWFjIjoiYmNjMTNjZWEzNDBjNjQwNjc0NjUyZGIxZGI5Y2QxNGMwYTVkMjJmMjBmZGUxZDE0NmQzOTgzNTQ0ZDNhZmYzYiJ9; XSRF-TOKEN=eyJpdiI6IjVPVk9NekJyaWVxWUg1OW12NnpTckE9PSIsInZhbHVlIjoiV1pxbGJ0QnNVZXFtWHpSa2IrZ3FVYmhDVFowMEc2M2h3RTZpc29QdWxxT2krV1p2dkJCblFxWkNzVjR6YnA5WWNKeHk5UHg0eGF2WGtzTWZiWUdFamc9PSIsIm1hYyI6ImU2Yzg1ODlkYTNiNmQ3MWQ0NTdhMzk5ZWNiN2VkODFlZDFmZTFjNGFjM2IxM2JjODM2ZWUxMGFmN2JiM2E5NGIifQ%3D%3D; dot_property_group=eyJpdiI6IjNvMnFvUDdGeVFjV0hTQ21aVmlcL3FRPT0iLCJ2YWx1ZSI6IjRwSWJsNUJGYXhna1ZHdFJcL0FFeFljV1F5RHlscldFdERnWjJZRCswS1lFQW5KT2E1TG92Y1EycVlhUk5oTTRTQ1FBcUpnRFcyKzgrdDgwTStYT1NBZz09IiwibWFjIjoiODUyYTA4YTIzODM4NTc4MDBmZTRkMDdiNjU5ZmMxZGI5MTZmODhkNjI2NTI0MWExZDhiNTM0NzQ0MjFhZjVlNiJ9",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": '?0',
    "sec-fetch-dest": 'document',
    "sec-fetch-mode": 'navigate',
    "sec-fetch-site": 'none',
    "sec-fetch-user": '?1',
    "upgrade-insecure-requests": '1',
    "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    "Content-type": 'text/plain; charset="utf-8"',
}

page_url = 'https://www.dotproperty.co.th/en/condos-for-sale/Chiang-Mai/Mueang-Chiang-Mai/Fa-Ham'


r = requests.session().get(page_url, headers=HEADERS, proxies=get_proxies())
r.encoding = 'UTF-8'
print(r.text)"""
import json
with open('data/links_th_condo_thai_prov.json', 'r+') as th_links:
    th_data = json.load(th_links)
with open('data/links_th_condo_bk_dist.json', 'r+') as bk_links:
    bk_data = json.load(bk_links)
thai_links = th_data + bk_data
with open('data/links_th_condo.json', 'w') as j_file:
    json.dump(thai_links, j_file, indent=4)