# -*- coding: utf-8 -*-

# Created by Zuoqi Zhang on 14/03/2018.

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

day_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

info_table = {}
price_table = {}

check_none_value = {}

api_key = 'dcb80824cf2f2c7b8f60c424745aa097412ee9e7'
url = 'https://api.parkwhiz.com/v4/quotes/'
area = '?q=coordinates:42.358056,-71.063611 distance:10'

start_date = '2008-04-01'
end_date = '2018-04-01'

start = datetime.strptime(start_date, '%Y-%m-%d').date()
end = datetime.strptime(end_date, '%Y-%m-%d').date()

dates = []
day = start
while day < end:
    dates.append(str(day))
    day += timedelta(days=1)
dates.append(str(end))

for i in range(len(dates) - 1):
    start_time = '&start_time=' + dates[i] + 'T00:00'
    end_time = '&end_time=' + dates[i + 1] + 'T00:00'
    query = url + area + start_time + end_time + '&api_key=' + api_key

    print(query)
    response = requests.get(query)

    json_response = response.json()
    # print(json.dumps(json_response, indent=2))

    for location in json_response:
        _id = location['location_id']
        city = location['_embedded']['pw:location']['city']
        if city != 'Boston':
            continue
        address = location['_embedded']['pw:location']['address1']
        coordinates = location['_embedded']['pw:location']['entrances'][0]['coordinates']
        price_list = []
        for option in location['purchase_options']:
            price_list.append(float(option['price']['USD']))
        if len(price_list) > 0:
            price = np.mean(price_list)
        else:
            price = None

        if _id not in info_table.keys():
            info_table[_id] = {'address': address,
                               'coordinates': coordinates}
            price_table[address] = [None for j in range(len(dates) - 1)]
            price_table[address][i] = price
            check_none_value[address] = False
            if price is not None:
                check_none_value[address] = True
        else:
            price_table[address][i] = price
            if price is not None:
                check_none_value[address] = True

info_table = pd.DataFrame.from_dict(info_table, orient='index')
price_table = pd.DataFrame.from_dict(price_table, orient='index')
price_table.set_axis(axis=1, labels=[d + ', ' + day_of_week[datetime.strptime(d, '%Y-%m-%d').date().weekday()] for d in dates[:-1]])

for addr in check_none_value.keys():
    if check_none_value[addr] == False:
        info_table = info_table[info_table.address != addr]
        price_table = price_table[price_table.index != addr]

print(info_table)
print(price_table)

info_table.to_csv('info_table.csv')
price_table.to_csv('price_table.csv')