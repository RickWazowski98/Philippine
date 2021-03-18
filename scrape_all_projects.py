import json
import logging
import requests
from bs4 import BeautifulSoup
from helpers import headers, headers_xml


file_object = open('data/links.json', 'r')
links = json.load(file_object)

