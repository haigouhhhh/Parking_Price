import requests
import json
import csv
import pandas as pd
import re
import numpy as np

#Read parking price data from local csv table

price=pd.read_csv("./price_table.csv")
price['mean']=price.mean(axis=1)
price.fillna(0, inplace=True)
site_price={}

#store the averaged parking cost per day of each parking site into dictionary site_price

for i in range(len(price)):
    site_name=price.iloc[i][0]
    ave_price=price.iloc[i][-1]
    if(ave_price>0):
        site_price.update({site_name:ave_price})

#merge price and coordinates of parking site into a whole table

info_table=pd.read_csv("./info_table.csv")
for i in range(len(info_table)):
    site_name=info_table.iloc[i][1]
    if site_name in site_price.keys():
        site_coor=info_table.iloc[i][2]
        site_price.update({site_name:[site_coor,site_price[site_name]]})
#print(site_price)



# get the neighbors information of each parking site from googleplace api
col=['restaurant','hospital','bank','museum','park','establishment','price']
df=pd.DataFrame(columns=col)
for key in (site_price.keys()):
    value=site_price[key]
    coor=value[0]
    coor=re.split(',',coor)
    lat=float(coor[0][1:])
    lng=float(coor[1][:-1])
    print(lat,lng)
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={0},{1}&radius=5000&&key=AIzaSyC5DreNdg-q5Nlp1jD6w9yyzMl6H6LyMYk".format(lat,lng)
    response = requests.get(url)
    json_data = json.loads(response.text)
    print(json_data)
    #count the number of specific buildings around these sites
    rest=0
    ho=0
    ba=0
    mu=0
    pa=0
    es=0

    while(json_data['results']!=None and len(json_data['results'])>0):
       result=json_data['results']
       page_token=json_data['next_page_token']
       for each_neigh in result:
           type=each_neigh['types']

           if('food' in type):
               rest=rest+1
           if('hospital' in type):
               ho=ho+1
           if('bank' in type):
               ba=ba+1
           if('museum' in type):
               mu=mu+1
           if('park' in type):
               pa=pa+1
           if('establishment' in type):
               es=es+1
       if(page_token==None):
           break
       #read the next two pages of searching results
       print(page_token)
       url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={0},{1}&radius=5000&&key=AIzaSyD_p2CUYMbkV-fmpS59qKdlxURR681wwPI".format(
           lat, lng)
       response = requests.get(url)
       json_data = json.loads(response.text)
       print(json_data)
    print(rest,ho,ba,mu,pa,es)
