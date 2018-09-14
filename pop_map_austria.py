import requests
import pandas as pd
from collections import OrderedDict
import json
import matplotlib.pyplot as plt
import numpy as np

url = 'https://query.wikidata.org/sparql'

query = """
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>

SELECT DISTINCT ?itemLabel (AVG(?item_lat) AS ?lat) (AVG(?item_long) AS ?long) (AVG(?Einwohnerzahl) AS ?pop) WHERE {
  ?item p:P31 ?statement.
  ?statement ps:P31 wd:Q667509.
  filter not exists {?statement pq:P582 [].}
  ?item rdfs:label ?itemLabel.
  ?item (p:P625/psv:P625) ?item_node.
  ?item_node wikibase:geoLatitude ?item_lat.
  ?item_node wikibase:geoLongitude ?item_long.
  ?item wdt:P1082 ?Einwohnerzahl.
  FILTER((LANG(?itemLabel)) = "de")
}
GROUP BY ?itemLabel
ORDER BY ?itemLabel
"""

bGetDataWikidata=1
if bGetDataWikidata:
    r = requests.get(url, params = {'format': 'json', 'query': query})
    r.raise_for_status()
    data = r.json()
    gemeinden = []
    for item in data['results']['bindings']:
        gemeinden.append(OrderedDict({
            'Name': item['itemLabel']['value'],
            'lat' : item['lat']['value'],
            'long' : item['long']['value'],
            'pop' : item['pop']['value']
        }))


    df = pd.DataFrame(gemeinden)
    df.set_index('Name', inplace=True)
    df = df.astype({'pop': float , 'lat' : float, 'long' : float })

    df.to_csv('data.csv')

df = pd.read_csv('data.csv')
bPlot=1
bNames=0
bLegend=0
if bPlot:


    fig = plt.figure(figsize=(22, 12))

    ax = fig.add_subplot(111)
    plt.axis('off')
    ax.scatter(x=df['long'].values,y=df['lat'].values,s=df['pop'].values/100,alpha=0.5,linewidths=0)
    if bLegend:
        x_legend=[11,11,11,11,11]
        y_legend=[48.5,48.15,48,47.9,47.8]
        s_legend=[10000,1000,100,10,1]
        s_slegend=[]
        for entry in s_legend:
            s_slegend.append(str(entry*100))
        ax.scatter(x=x_legend,y=y_legend,s=s_legend,alpha=0.5,linewidths=0)
        for label, x, y in zip(s_slegend, x_legend, y_legend):
            plt.annotate(
                label,fontsize=1,
                xy=(x, y), xytext=(50, 0),size=15,
                textcoords='offset points',arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
    if bNames:
        for label, x, y in zip(df['Name'].values, df['long'].values, df['lat'].values):
            plt.annotate(
                label,fontsize=1,
                xy=(x, y), xytext=(0, 0),
                textcoords='offset points')
    fig.savefig("map.pdf")

#plt.show()
