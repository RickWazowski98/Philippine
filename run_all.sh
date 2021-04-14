#!/bin/sh
. "venv/bin/activate"
# Thailand
python get_urls_by_each_region_th_condo-1.py
python get_urls_by_each_region_th_condo-2.py
python args_dt_dotproperty-1.py -tn "Thailand condominiums"
python args_dt_load_to_sheet.py -tn "Thailand condominiums"
python args_dt_dotproperty-2.py -tn "Thailand condominiums"
python args_dt_dotproperty-mix.py -tn "Thailand condominiums"

python get_urls_by_each_region.py
python args_dt_dotproperty-1.py -tn "Thailand houses"
python args_dt_load_to_sheet.py -tn "Thailand houses"
python args_dt_dotproperty-2.py -tn "Thailand houses"
python args_dt_dotproperty-mix.py -tn "Thailand houses"

python args_get_urls_by_tab.py -tn "Thailand townhouses"
python args_dt_dotproperty-1.py -tn "Thailand townhouses"
python args_dt_load_to_sheet.py -tn "Thailand townhouses"
python args_dt_dotproperty-2.py -tn "Thailand townhouses"
python args_dt_dotproperty-mix.py -tn "Thailand townhouses"

#Philippines
python args_get_urls_by_tab.py -tn "Philippines condominiums"
python args_dt_dotproperty-1.py -tn "Philippines condominiums"
python args_dt_load_to_sheet.py -tn "Philippines condominiums"
python args_dt_dotproperty-2.py -tn "Philippines condominiums"
python args_dt_dotproperty-mix.py -tn "Philippines condominiums"

python args_get_urls_by_tab.py -tn "Philippines houses"
python args_dt_dotproperty-1.py -tn "Philippines houses"
python args_dt_load_to_sheet.py -tn "Philippines houses"
python args_dt_dotproperty-2.py -tn "Philippines houses"
python args_dt_dotproperty-mix.py -tn "Philippines houses"

python args_get_urls_by_tab.py -tn "Philippines townhouses"
python args_dt_dotproperty-1.py -tn "Philippines townhouses"
python args_dt_load_to_sheet.py -tn "Philippines townhouses"
python args_dt_dotproperty-2.py -tn "Philippines townhouses"
python args_dt_dotproperty-mix.py -tn "Philippines townhouses"

#Vietnam
python args_get_urls_by_tab.py -tn "Vietnam condominiums"
python args_dt_dotproperty-1.py -tn "Vietnam condominiums"
python args_dt_load_to_sheet.py -tn "Vietnam condominiums"
python args_dt_dotproperty-2.py -tn "Vietnam condominiums"
python args_dt_dotproperty-mix.py -tn "Vietnam condominiums"

python args_get_urls_by_tab.py -tn "Vietnam houses"
python args_dt_dotproperty-1.py -tn "Vietnam houses"
python args_dt_load_to_sheet.py -tn "Vietnam houses"
python args_dt_dotproperty-2.py -tn "Vietnam houses"
python args_dt_dotproperty-mix.py -tn "Vietnam houses"

python args_get_urls_by_tab.py -tn "Vietnam townhouses"
python args_dt_dotproperty-1.py -tn "Vietnam townhouses"
python args_dt_load_to_sheet.py -tn "Vietnam townhouses"
python args_dt_dotproperty-2.py -tn "Vietnam townhouses"
python args_dt_dotproperty-mix.py -tn "Vietnam townhouses"

#Malaysia
python args_get_urls_by_tab.py -tn "Malaysia condominiums"
python args_dt_dotproperty-1.py -tn "Malaysia condominiums"
python args_dt_load_to_sheet.py -tn "Malaysia condominiums"
python args_dt_dotproperty-2.py -tn "Malaysia condominiums"
python args_dt_dotproperty-mix.py -tn "Malaysia condominiums"

python args_get_urls_by_tab.py -tn "Malaysia houses"
python args_dt_dotproperty-1.py -tn "Malaysia houses"
python args_dt_load_to_sheet.py -tn "Malaysia houses"
python args_dt_dotproperty-2.py -tn "Malaysia houses"
python args_dt_dotproperty-mix.py -tn "Malaysia houses"

python args_get_urls_by_tab.py -tn "Malaysia townhouses"
python args_dt_dotproperty-1.py -tn "Malaysia townhouses"
python args_dt_load_to_sheet.py -tn "Malaysia townhouses"
python args_dt_dotproperty-2.py -tn "Malaysia townhouses"
python args_dt_dotproperty-mix.py -tn "Malaysia townhouses"

#Indonesia
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

#Singapore
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