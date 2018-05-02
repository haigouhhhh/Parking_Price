# -*- coding: utf-8 -*-

# Created by Zuoqi Zhang on 2018/4/1.

import folium
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

info_table = pd.read_csv('info_table.csv', index_col=0)
price_table = pd.read_csv('price_table.csv', index_col=0)

coor_price = pd.merge(info_table, price_table, left_on='address', right_index=True)
coor_price['avg'] = coor_price.drop(['address', 'coordinates'], axis=1).mean(axis=1, skipna=True)
coor_price[['x', 'y']] = coor_price['coordinates'].str.strip('[]').str.split(', ', expand=True).rename(columns={0:'x', 1:'y'}).astype('float64')
coor_price = coor_price[['address', 'x', 'y', 'avg']]

min_x = coor_price['x'].min()
max_x = coor_price['x'].max()
coor_price['x'] = (coor_price['x'] - min_x) / (max_x - min_x) * 50

min_y = coor_price['y'].min()
max_y = coor_price['y'].max()
coor_price['y'] = (coor_price['y'] - min_y) / (max_y - min_y) * 50

# kvalues = [i for i in range(3, 10)]
# errors = []
#
# for k in kvalues:
#     kmeans = KMeans(init='k-means++', n_clusters=k, n_init=100)
#     kmeans.fit_predict(coor_price.drop(['address'], axis=1))
#
#     error = kmeans.inertia_
#     errors.append(error)
#
# plt.plot(kvalues, errors)
# plt.xlabel('Number of Clusters (k)')
# plt.ylabel('Error')
# plt.title('K-Means')

kmeans = KMeans(init='k-means++', n_clusters=5, n_init=100)
kmeans.fit_predict(coor_price.drop(['address'], axis=1))

centroids = kmeans.cluster_centers_
labels = kmeans.labels_
# error = kmeans.inertia_
# print(error)

avg = centroids[:, 2]
# print(sorted(avg))
rank = [sorted(avg).index(v) for v in avg]

colors = ['yellow', 'gold', 'orangered', 'red', 'darkred']

coor_price['x'] = coor_price['x'] / 50 * (max_x - min_x) + min_x
coor_price['y'] = coor_price['y'] / 50 * (max_y - min_y) + min_y

plt.scatter(x=coor_price['x'], y=coor_price['y'], c=labels, s=10)
plt.savefig('cluster.jpg')
# plt.show()

city_map = folium.Map([42.358056, -71.063611], zoom_start=12)
shape = gpd.read_file('City_of_Boston_Boundary/City_of_Boston_Boundary.shp')
gjson = shape.to_crs(epsg='4326').to_json()
city_map.add_child(folium.features.GeoJson(gjson))

for i in range(len(coor_price)):
    c = [coor_price['x'].iloc[i], coor_price['y'].iloc[i]]
    l = labels[i]
    r = rank[l]
    folium.CircleMarker(location=c, radius=10, color='white',
                        fill=True, fill_color=colors[r], fill_opacity=1,
                        popup=coor_price['address'].iloc[i] + ' $' + str(int(coor_price['avg'].iloc[i]))).add_to(city_map)

city_map.save('cluster_map.html')