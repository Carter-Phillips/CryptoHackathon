from datetime import datetime
import redis
import json
from Scraper import CoinSentiment
import sys

class Aggregator():
    def __init__(self, coin_sentiments: list, redis_client: redis.client.Redis):
        self.coin_sentiments = coin_sentiments
        self.rdis_c = redis_client

    def aggregate_by_day(self):
        new_coins_text = {}
        new_coins = {} # will contain any new coins not yet in redis
        # we sort the sentiments based on time created so that when we
        # update the latest_timestamp in redis for a specific coin
        # we know we are not eliminating any posts that were posted
        # before that latest_timestamp BUT AFTER the PREVIOUS latest_timestamp
        self.coin_sentiments.sort(key=lambda cs: cs.created)
        for coin_sentiment in self.coin_sentiments:
            coin = coin_sentiment.coin.upper()

            if coin not in new_coins_text:
                new_coins_text[coin] = {}
            date = datetime.utcfromtimestamp(coin_sentiment.created).date()
            new_coins_text[coin] = {coin_sentiment.created: {"text":coin_sentiment.text}}


            if not self.rdis_c.exists(coin): # first time inserting the coin into db
                if coin not in new_coins:
                    new_coins[coin] = {}
                date = datetime.utcfromtimestamp(coin_sentiment.created).date()
                if date not in new_coins[coin]:
                    new_coins[coin][date] = self.get_new_sentiment_dict(date, coin_sentiment)
                else:
                    avg_sent = new_coins[coin][date]["avg_sentiment"]
                    samples = new_coins[coin][date]["samples"]
                    new_coins[coin][date]["avg_sentiment"] =\
                         self.get_new_avg(avg_sent, samples, coin_sentiment.sentiment)
                    new_coins[coin][date]["samples"] += 1
                    new_coins[coin][date]["timestamp"] = \
                        max(new_coins[coin][date]["timestamp"], coin_sentiment.created)
            else: # for ones present in redis
                top = self.rdis_c.lrange(coin, 0, 0) # returns list with only top element
                top = json.loads(top[0])
                latest_timestamp = top["timestamp"]
                if coin_sentiment.created > latest_timestamp: # new entry
                    # get most recent date in list
                    latest = json.loads(self.rdis_c.lpop(coin))
                    latest_date = datetime.strptime(latest["date"], "%Y-%m-%d").date()
                    if latest_date < datetime.utcnow().date(): # it's a new day!
                        self.rdis_c.lpush(coin, json.dumps(latest))
                        new_latest =\
                            self.get_new_sentiment_dict(datetime.utcnow().date(), coin_sentiment)
                        self.rdis_c.lpush(coin, json.dumps(new_latest))
                        self.trim(coin)
                    else:
                        latest["avg_sentiment"] = \
                            self.get_new_avg(\
                                latest["avg_sentiment"], latest["samples"], coin_sentiment.sentiment\
                            )
                        latest["timestamp"] = max(latest["timestamp"], coin_sentiment.created)
                        self.rdis_c.lpush(coin, json.dumps(latest))

        # push any new coins to redis
        for coin in new_coins_text:
            for date in sorted(new_coins_text[coin])
                self.rdis_c.lpush(coin+'_TEXT', json.dumps({"text": new_coins_text[coin][date], "timestamp":date}))
        for coin in new_coins:
            for date in sorted(new_coins[coin]):
                self.rdis_c.lpush(coin, json.dumps(new_coins[coin][date]))

            self.trim(coin) # trim the linked list for max 30 days of averages

    def trim(self, coin: str):
        if self.rdis_c.llen(coin) > 31:
            self.rdis_c.ltrim(coin, 0, 30)

    def get_new_avg(self, avg_sent: float, samples: int, new_sent: float, new_samples: int = 1) -> float:
        return (samples*avg_sent+new_sent)/(samples+new_samples)

    def get_new_sentiment_dict(self, date, coin_sentiment: CoinSentiment) -> dict:
        return {
            "date": date.strftime("%Y-%m-%d"),
            "avg_sentiment": coin_sentiment.sentiment,
            "samples": 1,
            "timestamp": coin_sentiment.created
        }