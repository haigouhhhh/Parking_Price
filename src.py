# -*- coding: utf-8 -*-

# Created by Zuoqi Zhang on 2018/2/16.

import requests
import json
import re
import datetime
from dateutil.relativedelta import relativedelta

api_key = 'dcb80824cf2f2c7b8f60c424745aa097412ee9e7'
url = 'https://api.parkwhiz.com/v4/quotes/'
# get_oneday is to get parkibng price for a specific day
def get_oneday(start,end):
     query = "?q=coordinates:42.3601,-71.0589 distance:100"\
             + "&start_time={0}T00:00".format(start)\
             + "&end_time={0}T00:00".format(end)\
             + "&api_key=" + api_key
     response = requests.get(url + query)
     #print(url + query)
     json_data=json.loads(response.text)
     price=[]
     address=[]
     for i in json_data:
             # Check if the city is Boston
             if '_embedded' in i and i['_embedded']['pw:location']['city']=='Boston':
                     pos=[m.start() for m in re.finditer('USD',str(i['purchase_options']))]
                     if len(pos)>0 and pos[0]!='':
                             pos_i=pos[0]
                     else:
                         continue
                     price_=str(i['purchase_options'])[pos_i+7:pos_i+11]
                     try:
                             price_=float(price_)
                             #print(int(price_))
                             price.append(price_)
                             address.append(i['_embedded']['pw:location']['address1'])
                             #print(i)
                             #print(i['_embedded'])
                     except ValueError:
                             price.append(-1)
                             address.append('')
     return price,address


num_of_day=90
start_date=datetime.date(2018, 3, 1)
end_data=datetime.date(2018, 3, 2)
for day in range(0,num_of_day):
     start_date=start_date+relativedelta(days=1)
     end_data=end_data+relativedelta(days=1)
     price,address=get_oneday(start_date,end_data)
     print(len(price))
     #print(address)
#print(json.dumps(json_response, indent=2))
# df(co)