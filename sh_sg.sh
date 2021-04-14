#!/bin/sh
. "venv/bin/activate"
python args_get_urls_by_tab.py -tn "Singapore condominiums"
python args_dt_dotproperty-1.py -tn "Singapore condominiums"
python args_dt_load_to_sheet.py -tn "Singapore condominiums"
python args_dt_dotproperty-2.py -tn "Singapore condominiums"
python args_dt_dotproperty-mix.py -tn "Singapore condominiums"

python args_get_urls_by_tab.py -tn "Singapore houses"
python args_dt_dotproperty-1.py -tn "Singapore houses"
python args_dt_load_to_sheet.py -tn "Singapore houses"
python args_dt_dotproperty-2.py -tn "Singapore houses"
python args_dt_dotproperty-mix.py -tn "Singapore houses"

python args_get_urls_by_tab.py -tn "Singapore townhouses"
python args_dt_dotproperty-1.py -tn "Singapore townhouses"
python args_dt_load_to_sheet.py -tn "Singapore townhouses"
python args_dt_dotproperty-2.py -tn "Singapore townhouses"
python args_dt_dotproperty-mix.py -tn "Singapore townhouses"