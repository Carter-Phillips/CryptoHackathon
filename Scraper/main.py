import os
from Scraper import Scraper
from Aggregator import Aggregator
import redis

client = redis.from_url(os.environ.get("REDIS_URL"))
s = Scraper(client)
# IMPORTANT ---- SET local=False IF YOU want the results to be correct or
# it will break something FOR SURE
coin_sentiments = s.update_reddit(local=False)

ag = Aggregator(coin_sentiments, client)
ag.aggregate_by_day()

## CODE TO INSERT crypto.json INTO REDIS
# import json
# import redis
# import os

# client = redis.from_url(os.environ.get("REDIS_URL"))

# json_content = None
# with open("crypto.json", "r") as f:
#     json_content = f.read().replace('\n', '')

# data = json.loads(json_content)
# for key in data:
#     client.hset("cryptos_nodupe", data[key], key)