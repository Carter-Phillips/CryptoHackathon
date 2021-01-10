"""
This class is re-usable. Recycle it for all text rather than creating a new
instance per text.

USAGE:
pre = Preprocessor()
# crypto contains the set of crypto coins mentioned, words is the 
# porter stemmed, lowercased words in the text
crypto, words = pre.pipeline(text)

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
import typing

class CryptoNotLoadedException(Exception):
    pass

class NoLocalCryptoDbException(Exception):
    pass

class Preprocessor():
    """
    local=True will read the read json into memory to speed it up significantly
    """
    def __init__(self, redis_client: redis.client.Redis, local: bool = False):
        self.redis_client = redis_client
        self.redis_table = "cryptos"
        self.local = local
        if self.local:
            self.crypto_db = {}
        self.loaded = False

        self.check_and_load_cryptos()

        self.ttokenizer = nltk.TweetTokenizer() # tt = tweet tokenizer
        self.stemmer = nltk.PorterStemmer() # porter stemmer 

    def check_loaded(self):
        # check crypto file exists 
        if not self.loaded:
            raise CryptoNotLoadedException("")

    def check_and_load_cryptos(self):
        if self.local:
            json_content = None
            with open("crypto.json", "r") as f:
                json_content = f.read().replace('\n', '')

            data = json.loads(json_content)
            for key in data:
                self.crypto_db[key] = data[key]
                self.crypto_db[data[key]] = key

        # will not load redis stuff if local
        if self.local or self.redis_client.exists(self.redis_table):
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
        for key in data:
            client.hset(self.redis_table, key, data[key])
            client.hset(self.redis_table, data[key], key)

        self.loaded = True

    def tokenize(self, text: str) -> list:
        return self.ttokenizer.tokenize(text)

    def clean_punctuation(self, words: str) -> list:
        new_words = []
        for word in words:
            # removes punctuation and makes lower case
            new = "".join([w for w in word if w not in string.punctuation])
            if new != "":
                new_words.append(new)
        return new_words

    def lower_words(self, words: str) -> list:
        new_words = []
        for word in words:
            # removes punctuation and makes lower case
            new = "".join([w.lower() for w in word])
            if new != "":
                new_words.append(new)
        return new_words

    def identify_cryptos(self, words: list) -> list:
        self.check_loaded()
        coins = set()
        for word in words:
            if self.redis_client.hexists(self.redis_table, word):
                coin = self.redis_client.hget(self.redis_table, word)
                if coin.upper() == coin: # means it is a symbol not a name
                    coin = word
                
                # decoding is required if it is pulled from the db
                # since 
                coins.add(coin.decode("utf-8") if type(coin) != str else coin)

        return list(coins)

    def get_crypto(self, word: str) -> typing.Optional[str]:
        self.check_loaded()
        if not self.local:
            raise NoLocalCryptoDbException("To use this method initialize Preprocessor with arg local=True")
        
        coin = None
        if word in self.crypto_db:
            coin = self.crypto_db[word]
            if coin.upper() == coin: # means it is a symbol not a name
                coin = word

        return coin

    def porter_stem(self, words: list) -> list:
        self.check_loaded()
        for i, word in enumerate(words):
            words[i] = self.stemmer.stem(word)
        return words 

    def pipeline(self, text: str) -> tuple:
        words = self.tokenize(text) 
        return self.identify_cryptos(self.clean_punctuation(words)),\
                 self.porter_stem(self.lower_words(words))
