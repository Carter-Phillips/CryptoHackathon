"""
This class is re-usable. Recycle it for all text rather than creating a new
instance per text.
#1)
Will load crypto.json into redis if not present. 
Automatically inverts crypto.json to identify coin names too

#2) 
Will identify cryptos in a given piece of text

#3)
Will apply porter stemming to text

#4)
Will put feature #2 and #3 in a pipeline function to apply both and return result
"""
import os
import redis
import json

class CryptoNotLoadedException(Exception):
    pass

class Preprocessor():
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.loaded = False
        self.check_and_load_cryptos()

    def check_loaded(self):
        # check crypto file exists 
        if not self.loaded:
            raise CryptoNotLoadedException("")

    def check_and_load_cryptos(self):
        if self.redis_client.get("cryptos"):
            self.loaded = True
            return
        # check crypto file exists 
        if not os.path.exists("crypto.json"):
            raise CryptoNotLoadedException("crypto.json does not exist")

        json_content = None
        with open("crypto.json", "r") as f:
            json_content = f.read().replace('\n', '')

        data = json.loads(json_content)
        # for (key, value) in data:
        #     print("%s %s" % (key, value))
        self.loaded = True

    def identify_cryptos(self, text):
        self.check_loaded()

    def porter_stem(self, text):
        self.check_loaded()

    def pipeline(self, text):
        self.check_loaded()


if __name__ == '__main__':
    client = redis.from_url(os.environ.get("REDIS_URL"))
    pre = Preprocessor(client)
    