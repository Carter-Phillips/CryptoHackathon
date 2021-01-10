import os
from Scraper import Scraper

client = redis.from_url(os.environ.get("REDIS_URL"))
s = Scraper(client)
s.update_reddit()