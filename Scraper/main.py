import os
from Scraper import Scraper
from Aggregator import Aggregator
import redis

client = redis.from_url(os.environ.get("REDIS_URL"))
s = Scraper(client)
coin_sentiments = s.update_reddit()

ag = Aggregator(coin_sentiments)
ag.aggregate_by_day()