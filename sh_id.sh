#!/bin/sh
. "venv/bin/activate"
python args_get_urls_by_tab.py -tn "Indonesia condominiums"
python args_dt_dotproperty-1.py -tn "Indonesia condominiums"
python args_dt_load_to_sheet.py -tn "Indonesia condominiums"
python args_dt_dotproperty-2.py -tn "Indonesia condominiums"
python args_dt_dotproperty-mix.py -tn "Indonesia condominiums"

python args_get_urls_by_tab.py -tn "Indonesia houses"
python args_dt_dotproperty-1.py -tn "Indonesia houses"
python args_dt_load_to_sheet.py -tn "Indonesia houses"
python args_dt_dotproperty-2.py -tn "Indonesia houses"
python args_dt_dotproperty-mix.py -tn "Indonesia houses"

python args_get_urls_by_tab.py -tn "Indonesia townhouses"
python args_dt_dotproperty-1.py -tn "Indonesia townhouses"
python args_dt_load_to_sheet.py -tn "Indonesia townhouses"
python args_dt_dotproperty-2.py -tn "Indonesia townhouses"
python args_dt_dotproperty-mix.py -tn "Indonesia townhouses"