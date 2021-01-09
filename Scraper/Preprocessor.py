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
import nltk
import string

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
        if self.redis_client.exists("cryptos"):
            self.loaded = True
            return

        print('cryptos not detected in Redis, loading cryptos... this may take a bit')
        # check crypto file exists 
        if not os.path.exists("crypto.json"):
            raise CryptoNotLoadedException("crypto.json does not exist")

        json_content = None
        with open("crypto.json", "r") as f:
            json_content = f.read().replace('\n', '')

        data = json.loads(json_content)
        redis_table = 'cryptos'
        for key in data:
            client.hset(redis_table, key, data[key])
            client.hset(redis_table, data[key], key)

        self.loaded = True

    def clean_and_get_words(self, text):
        # remove punctuation
        text = "".join([w.lower() for w in text if w not in string.punctuation])
        # tokenize with nltk
        return nltk.word_tokenize(text)

    def identify_cryptos(self, words):
        for wor
        self.check_loaded()

    def porter_stem(self, words):
        self.check_loaded()

    def pipeline(self, text):
        self.clean_and_get_words(text)
        self.identify_cryptos(text)
        self.porter_stem(text)
        self.check_loaded()


if __name__ == '__main__':
    client = redis.from_url(os.environ.get("REDIS_URL"))
    pre = Preprocessor(client)
    clean = "Hello! How are you!! I'm very excited that you're going for a trip to Europe!! Yayy!"
    print(pre.clean_and_get_words(clean))
    