import argparse
import redis
import json
from google.cloud import language_v1
from Preprocessor import Preprocessor
import time

class Analyzer():
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.preprocessor = Preprocessor(redis_client, local=True)
        self.client = language_v1.LanguageServiceClient()
        
    def analyze(self, input):
        """Run a sentiment analysis request on text within a passed filename."""
        document = language_v1.Document(content=input, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = self.client.analyze_entity_sentiment(request={'document': document})

        # YES RAGHAV I YOINKED YOUR CODE GET HECKED ON
        coinResults = []
        for entity in response.entities:
            if entity.sentiment.score != 0:
                coin = self.preprocessor.get_crypto(entity.name)
                if coin:
                    coin_sentiment = CoinSentiment(coin, entity.sentiment.score)
                    print("Adding sentiment for %s sentiment value %.2f"\
                        % (coin_sentiment.coin, coin_sentiment.sentiment))
                    coinResults.append(coin_sentiment)


        return coinResults

class CoinSentiment:
    def __init__(self, coin, sentiment):
        self.coin = coin
        self.sentiment = sentiment
