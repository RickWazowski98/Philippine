#!/bin/sh
. "venv/bin/activate"
python get_urls_by_each_region_th_condo-1.py
python get_urls_by_each_region_th_condo-2.py
python args_dt_dotproperty-1.py -tn "Thailand condominiums"
python args_dt_load_to_sheet.py -tn "Thailand condominiums"
python args_dt_dotproperty-2.py -tn "Thailand condominiums"
python args_dt_dotproperty-mix.py -tn "Thailand condominiums"