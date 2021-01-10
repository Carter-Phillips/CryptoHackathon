from datetime import datetime

class Aggregator():
    def __init__(self, coin_sentiments: list):
        self.coin_sentiments = coin_sentiments

    def aggregate_by_day(self):
        for coin_sentiment in self.coin_sentiments:
            date = datetime.utcfromtimestamp(coin_sentiment.created)\
                    .strftime("%Y-%m-%d %H:%M:%S")
            

        