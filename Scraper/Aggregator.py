class Aggregator():
    def __init__(self, coin_sentiments: list):
        self.coin_sentiments = coin_sentiments

    def aggregate_by_day(self):
        for coin_sentiment in self.coin_sentiments:
            print(coin_sentiment.created)
        pass
        