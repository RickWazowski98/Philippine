import json
import pygsheets
import time
import yaml
import json

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['googlesheets']['name']
SHEET1 = config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
# sh = gc.open(SHEET_NAME)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
wks = sh.worksheet_by_title(SHEET1)


# clear manually BEFORE or add auto to script here (but not AN column!)

file_object = open('data/projects_data.json', 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    values_mat.append(list(project.values()))

wks.update_values(crange='A2', values=values_mat)

# TODO: load GPS as well
file_object = open('data/projects_data_gps_and_others.json', 'r')
projects_data_gps_and_others = json.load(file_object)

values_mat = []
for project in projects_data_gps_and_others:
    values_mat.append(list(project.values()))

wks.update_values(crange='AR2', values=values_mat)