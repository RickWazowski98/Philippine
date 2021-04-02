#!/bin/sh
. "venv/bin/activate"
python args_get_urls_by_tab.py -tn "Laos condominiums"
python args_dt_dotproperty-1.py -tn "Laos condominiums"
python args_dt_load_to_sheet.py -tn "Laos condominiums"
python args_dt_dotproperty-2.py -tn "Laos condominiums"
python args_dt_dotproperty-mix.py -tn "Laos condominiums"
python args_get_urls_by_tab.py -tn "Laos houses"
python args_dt_dotproperty-1.py -tn "Laos houses"
python args_dt_load_to_sheet.py -tn "Laos houses"
python args_dt_dotproperty-2.py -tn "Laos houses"
python args_dt_dotproperty-mix.py -tn "Laos houses"
python args_get_urls_by_tab.py -tn "Laos townhouses"
python args_dt_dotproperty-1.py -tn "Laos townhouses"
python args_dt_load_to_sheet.py -tn "Laos townhouses"
python args_dt_dotproperty-2.py -tn "Laos townhouses"
python args_dt_dotproperty-mix.py -tn "Laos townhouses"