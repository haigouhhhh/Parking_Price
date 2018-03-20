# -*- coding: utf-8 -*-

# Created by Zuoqi Zhang on 19/03/2018.

import folium
import pandas as pd
import geopandas as gpd

day_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

info_table = pd.read_csv('info_table.csv', index_col=0)
price_table = pd.read_csv('price_table.csv', index_col=0)

coor = pd.concat(info_table.loc[info_table['address'] == addr] for addr in price_table.axes[0])

weekday = pd.concat([price_table.loc[:, price_table.columns.str.contains(i)] for i in day_of_week[:5]], axis=1)
weekend = pd.concat([price_table.loc[:, price_table.columns.str.contains(i)] for i in day_of_week[5:]], axis=1)

weekday_avg = weekday.mean(axis=1, skipna=True)
weekend_avg = weekend.mean(axis=1, skipna=True)

city_map = folium.Map([42.358056, -71.063611], zoom_start=12)
shape = gpd.read_file('City_of_Boston_Boundary.shp')
gjson = shape.to_crs(epsg='4326').to_json()
city_map.add_child(folium.features.GeoJson(gjson))

for i in range(len(coor) - 1):
    c = [float(num) for num in coor['coordinates'].iloc[i].replace('[', '').replace(']', '').split(',')]
    folium.Marker(location=c, popup='Weekday Avg: {}, Weekend Avg: {}'.format(weekday_avg[i], weekend_avg[i]), icon=folium.Icon(color='blue')).add_to(city_map)

city_map.save('map.html')