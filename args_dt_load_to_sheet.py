import json
import pygsheets
import time
import yaml
import json
from datetime import datetime
import argparse
from loguru import logger
import os
import sys


my_parser = argparse.ArgumentParser()
my_parser.add_argument('-tn')
args = my_parser.parse_args()
input_tab_name = args.tn

basedir = os.path.dirname(__file__)
logfile = os.path.join(basedir, "logs", f"{input_tab_name.replace(' ','_').lower()}_args_dt_load_to_sheet.log")
logger.add(logfile, rotation="10 MB")
logger.debug(f"Started {input_tab_name}")

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)
mapping_config = config['mappings_tabs'][input_tab_name]

SERVICE_FILE = config['googlesheets']['file']
SHEET_NAME = config['mappings_tabs']['sheet_name']
SHEET1 = mapping_config['tab_name']

gc = pygsheets.authorize(service_file=SERVICE_FILE)
# sh = gc.open(SHEET_NAME)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Hd-WbIN20-hj_7ZzEGcSbxG08kBuAlTlejYDE7pcMuI/edit#gid=589501000')
wks = sh.worksheet_by_title(SHEET1)
# wks.clear(start='B2', end='ZZ9999')


# clear manually BEFORE or add auto to script here (but not formulas columns!)
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_1'], end=config['googlesheets']['dt_sheets_load_range_bulk_1_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_2'], end=config['googlesheets']['dt_sheets_load_range_bulk_2_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_3'], end=config['googlesheets']['dt_sheets_load_range_bulk_3_end'])
# wks.clear(start=config['googlesheets']['dt_sheets_copy_paste_location_clear_start'], end=config['googlesheets']['dt_sheets_copy_paste_location_clear_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_4'], end=config['googlesheets']['dt_sheets_load_range_bulk_4_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_5'], end=config['googlesheets']['dt_sheets_load_range_bulk_5_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_3_4'], end=config['googlesheets']['dt_sheets_load_range_bulk_3_4_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_3_5'], end=config['googlesheets']['dt_sheets_load_range_bulk_3_5_end'])
wks.clear(start=config['googlesheets']['dt_sheets_load_range_bulk_6'], end=config['googlesheets']['dt_sheets_load_range_bulk_6_end'])



file_object = open(f"data/{mapping_config['file_data_bulk_1']}.json", 'r')
projects_data = json.load(file_object)
# print(projects_data)
values_mat = []
for project in projects_data:
    if project != '':
        values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_1'], values=values_mat)


file_object = open(f"data/{mapping_config['file_data_bulk_2']}.json", 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    if project != '':
        values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_2'], values=values_mat)


file_object = open(f"data/{mapping_config['file_data_bulk_3']}.json", 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    if project != '':
        values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_3'], values=values_mat)


file_object = open(f"data/{mapping_config['file_data_bulk_3']}_4.json", 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    if project != '':
        values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_3_4'], values=values_mat)

file_object = open(f"data/{mapping_config['file_data_bulk_3']}_5.json", 'r')
projects_data = json.load(file_object)

values_mat = []
for project in projects_data:
    if project != '':
        values_mat.append(list(project.values()))

wks.update_values(crange=config['googlesheets']['dt_sheets_load_range_bulk_3_5'], values=values_mat)

"""
So when you are done with scraping the project data in a certain tab, you will add an identifier to column AZ in that same tab (i.e. the “manual” edit)
"""

identifier_trigger = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
wks.update_value(config['googlesheets']['dt_sheets_identifer_trigger_end_part1'], identifier_trigger)

# wait here 5-10 mins
wait_time_min = 1
logger.debug(f"Just waiting after load, mins: {wait_time_min}...")
time.sleep(wait_time_min*60)