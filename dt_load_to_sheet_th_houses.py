import json
import pygsheets
import time
import yaml
import json
from datetime import datetime

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)


SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = 'Dot Property Data - Real Estate Data' # config['googlesheets']['name']
SHEET1 = 'Thailand houses' # config['googlesheets']['sheet1']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
sh = gc.open(SHEET_NAME)
wks = sh.worksheet_by_title(SHEET1)


# clear manually BEFORE or add auto to script here (but not formulas columns!)
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_1'], end=config['googlesheets']['dt_sheets_load_range_bulk_1_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_2'], end=config['googlesheets']['dt_sheets_load_range_bulk_2_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_3'], end=config['googlesheets']['dt_sheets_load_range_bulk_3_end'])
wks.clear(start=config['googlesheets']['dt_sheets_copy_paste_location_clear_start'], end=config['googlesheets']['dt_sheets_copy_paste_location_clear_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_4'], end=config['googlesheets']['dt_sheets_load_range_bulk_4_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_5'], end=config['googlesheets']['dt_sheets_load_range_bulk_5_end'])


file_object = open('data/projects_data_th_houses_result_bulk_1.json', 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_1'], values=values_mat)


file_object = open('data/projects_data_th_houses_result_bulk_2.json', 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_2'], values=values_mat)


file_object = open('data/projects_data_th_houses_result_bulk_3.json', 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_3'], values=values_mat)


"""
So when you are done with scraping the project data in a certain tab, you will add an identifier to column AZ in that same tab (i.e. the “manual” edit)
"""

identifier_trigger = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
wks.update_value(config['googlesheets']['dt_sheets_identifer_trigger_end_part1'], identifier_trigger)

# wait here 5-10 mins