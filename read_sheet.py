import json
import pygsheets
import time
import yaml
import json

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['googlesheets']['name']
SHEET2 = config['googlesheets']['sheet2']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET2)

# print(wks.get_values('A1','A1000'))

result = wks.get_col(1, include_tailing_empty=False)[1:]

file_object = open('data/provinces-cities-areas.json', 'w')
json.dump(result, file_object, indent=4)