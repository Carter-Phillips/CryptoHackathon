from binance.client import Client
import json

class binancePriceFetch:
    def __init__(self):
        with open('./utils/binanceAPI.json') as jsonFile:
            data = json.load(jsonFile)
        self.client = Client(data['key'], data['secret'])

    def getPrice(self, coin):
        result = self.client.get_symbol_ticker(symbol = coin+'USDT')
        return result['price']