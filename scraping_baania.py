import json
import pandas as pd

with open("page_source_test_brokers?&offset=0&limit=2000.html", "r") as page_source_file:
    source_text = page_source_file.read()

source_data = source_text.split('"brokers":')[1].split(',"query":{"offset":"0","limit":"2000"},"namespacesRequired"')[0]

data = json.loads(source_data)
# print(type(data), len(data['data']))

result_matrix = []

for broker in data['data']:
    full_name = broker['name']
    url = 'https://www.baania.com/en{}'.format(broker['link'])
    contactInfo = broker['contactInfo']
    # print(contactInfo)
    try:
        if '@' not in contactInfo:
            email = ''
        else:
            contact_strs = contactInfo.split(',')
            if not contact_strs:
                email = contactInfo
            else:
                for c in contact_strs:
                    if '@' in c:
                        email = c
    except:
        email = ''
    
    result_matrix.append({
                'Full name': full_name,
                'broker profile URL': url,
                'E-mail': email
            })

df_result = pd.DataFrame(result_matrix)
df_result.to_csv('output_baania.csv', index=False)