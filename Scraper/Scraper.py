from platformScraper import RedditScraper, TwitterScraper, CoindeskScraper
from datetime import datetime
from Preprocessor import Preprocessor
from Analyzer import Analyzer
import redis
import time
from os import path
import json

# to use you need to first initialize a Scraper object,
# then initialize the processor with Scraper.initialize_processor(redis_client)
# then you can update anything you need, processed data will be returned when an update is called.

class Scraper:


    def __init__(self, redis_client: redis.client.Redis):
        self.date_updated_reddit = False
        self.date_updated_twitter = False
        self.date_updated_coindesk = False
        self.redis_client = redis_client
        #self.preprocessor = Preprocessor(self.redis_client)
        self.analyzer = Analyzer(self.redis_client)

    def update_all(self):
        return [self.updatereddit(), self.updatetwitter(), self.updatecoindesk()]

    def update_reddit(self):
        if path.exists('redditJson.json'):
            data = ''
            processed_data = []
            with open('redditJson.json') as jsonFile:
                data = json.load(jsonFile)

            for sentiment in data['posts']:
                processed_data.append(CoinSentiment(sentiment['coin'], sentiment['sentiment'], sentiment['created']))

            return processed_data
        else:
            # call all of our scrapers

            # scrape(timeStamp) takes a datetime object
            # and only returns posts newer than it
            scrape_date = datetime.now()
            reddit_results = RedditScraper.scrape(self.date_updated_reddit)
            print('DONE REDDIT SCRAPE WITH {} RESULTS'.format(reddit_results.__len__()))

            for_analysis = []
            for result in reddit_results:
                for_analysis.append(["%s %s" % (result.title, result.text), result.created])
                for comment in result.comments:
                    for_analysis.append([comment.text, comment.created])

            now = time.time()
            coin_sentiments = self.analyzer.analyze(for_analysis)
            print("Time taken for analysis: " + str(time.time() - now))
            print("Number of posts analyzed (including comments): " + str(len(for_analysis)))
            print("Number of sentiments received: " + str(len(coin_sentiments)))

            self.date_updated_reddit = scrape_date
            x = False
            posts = []
            for result in coin_sentiments:
                posts.append({"coin": result.coin, "sentiment": result.sentiment, "created": result.created})

            jsonOut = {"posts": posts}

            with open('redditJson.json', 'w+') as outfile:
                json.dump(jsonOut, outfile)
            return coin_sentiments

            return coin_sentiments

    def update_twitter(self):
        scrape_date = datetime.now()
        twitter_results = RedditScraper.scrape(self.date_updated_twitter)
        processed_data = self.process(twitter_results)
        self.date_updated_twitter = scrape_date
        return processed_data

    def update_coindesk(self):
        scrape_date = datetime.now()
        coindesk_results = RedditScraper.scrape(self.date_updated_coindesk)
        processed_data = self.process(coindesk_results)
        self.date_updated_coindesk = scrape_date
        return processed_data

    def process(self, result):
        # deal with processing of the data through preprocessor
        pre = self.preprocessor
        result.processed_title = pre.pipeline(result.title)
        result.text = pre.pipeline(result.text)
        for comment in result.comments:
            result.processed_comments.append(pre.pipeline(comment))

        return result

class CoinSentiment:
    def __init__(self, coin, sentiment, created):
        self.coin = coin
        self.sentiment = sentiment
        self.created = created

if __name__ == '__main__':
    import os
    client = redis.from_url(os.environ.get("REDIS_URL"))
    s = Scraper(client)
    s.update_reddit()




