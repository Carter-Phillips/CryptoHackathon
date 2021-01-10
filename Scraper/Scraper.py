from platformScraper import RedditScraper, TwitterScraper, CoindeskScraper
from datetime import datetime
from Preprocessor import Preprocessor
from Analyzer import Analyzer
import redis
import time

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
        # call all of our scrapers

        # scrape(timeStamp) takes a datetime object
        # and only returns posts newer than it
        scrape_date = datetime.now()
        reddit_results = RedditScraper.scrape(self.date_updated_reddit)
        print('DONE REDDIT SCRAPE WITH {} RESULTS'.format(reddit_results.__len__()))
        coinSentiments = []
        for result in reddit_results:
            post = self.analyzer.analyze(result.title + ' ' + result.text)
            comms = []
            for comment in result.comments:
                comms.append(self.analyzer.analyze(comment))
            coinSentiments.append([post, comms])
        self.date_updated_reddit = scrape_date
        return coinSentiments

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

if __name__ == '__main__':
    import os
    client = redis.from_url(os.environ.get("REDIS_URL"))
    s = Scraper(client)
    s.update_reddit()