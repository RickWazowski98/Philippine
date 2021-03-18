#!/bin/sh
. "venv/bin/activate"
python args_get_urls_by_tab.py -tn "Vietnam houses"
python args_dt_dotproperty-1.py -tn "Vietnam houses"
python args_dt_load_to_sheet.py -tn "Vietnam houses"
python args_dt_dotproperty-2.py -tn "Vietnam houses"
python args_dt_dotproperty-mix.py -tn "Vietnam houses"