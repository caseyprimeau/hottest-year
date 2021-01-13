import requests
import datetime
import sqlite3
import pdb

response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
data = response.json()

current_time = datetime.datetime.now().isoformat()
last_price = data['contracts'][0]['lastTradePrice']

with sqlite3.connect('/home/casey/data/hottest.db') as conn:

    cur = conn.cursor()
    cur.execute("INSERT INTO price VALUES(?,?);",
        ((current_time,last_price))
)

print('inserted latest price')