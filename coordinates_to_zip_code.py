# -*- coding: utf-8 -*-

# Created by Zuoqi Zhang on 2018/4/12.

import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

shape = gpd.read_file('ZIP_Codes/ZIP_Codes.shp')
gjson = shape.to_crs(epsg='4326').to_json()
gjson = json.loads(gjson)

postal_table = pd.DataFrame(columns=['zip_code'])
geos = []
for obj in gjson['features']:
    zip_code = obj['properties']['ZIP5']
    geometry = obj['geometry']['coordinates'][0]

    if zip_code != '02467' and len(geometry) >= 3:
        geos.append(Polygon(geometry))
        postal_table = postal_table.append({'zip_code': zip_code}, ignore_index=True)

info_table = pd.read_csv('info_table.csv', index_col=0)
coors = []
for xy in info_table.coordinates:
    coor = xy.replace('[', '').replace(']', '').split(', ')
    coors.append(Point([float(coor[1]), float(coor[0])]))

info_table = gpd.GeoDataFrame(info_table.drop('coordinates', axis=1), crs={'init': 'epsg:4326'}, geometry=coors)
postal_table = gpd.GeoDataFrame(postal_table, crs={'init': 'epsg:4326'}, geometry=geos)

# print(info_table)
# print(postal_table)

coors_with_code = gpd.sjoin(info_table, postal_table, how="inner", op='intersects')

# print(coors_with_code)

price_table = pd.read_csv('price_table.csv', index_col=0)
price_table.loc[:, 'AVG'] = price_table.mean(axis=1, skipna=True)
avg_table = price_table['AVG']

addr_with_code = pd.concat(coors_with_code.loc[coors_with_code['address'] == addr] for addr in price_table.axes[0])

avg_with_code = []
for addr in addr_with_code.address:
    zc = addr_with_code.loc[addr_with_code['address'] == addr]['zip_code'].item()
    avg = avg_table.get(addr)
    avg_with_code.append([zc, avg])

avg_with_code = pd.DataFrame.from_records(avg_with_code, columns=['zip_code', 'avg']).groupby('zip_code', axis=0).mean()
avg_with_code = avg_with_code.to_dict()['avg']

postal_table = postal_table[postal_table['zip_code'].isin(avg_with_code.keys())].sort_values('zip_code')
postal_table['avg_price'] = avg_with_code.values()

postal_table.plot(column='avg_price', cmap='Reds')
plt.savefig('heatmap.jpg')