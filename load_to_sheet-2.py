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


# wks.update_value('A10', "test")

file_object = open('data/provinces-cities-areas_data.json', 'r')
provinces_data = json.load(file_object)

wks.update_values(crange='B2', values=provinces_data)