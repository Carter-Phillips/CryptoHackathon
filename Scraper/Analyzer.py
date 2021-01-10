import argparse
import redis
import json
from google.cloud import language_v1


def analyze(input):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(content=input, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entity_sentiment(request={'document': document})
    redis_client = redis.from_url(
        'redis://:p05ca3a5a99da6bbd8bd06cd80912e4f89710bcc2149d75a64c645485ae85d9eb@ec2-174-129-249-71.compute-1.amazonaws.com:9029')

    print(response)

    # YES RAGHAV I YOINKED YOUR CODE GET HECKED ON
    coinResults = []
    for entity in response.entities:
        if redis_client.hexists('cryptos', entity.name):
            coin = redis_client.hget('cryptos', entity.name)
            if coin.upper() == coin:  # means it is a symbol not a name
                coin = entity.name

            # decoding is required if it is pulled from the db
            # since

            coinResults.append(
                CoinSentiment(coin.decode("utf-8") if type(coin) != str else coin, entity.sentiment.score))


    return coinResults

class CoinSentiment:
    def __init__(self, coin, sentiment):
        self.coin = coin
        self.sentiment = sentiment
