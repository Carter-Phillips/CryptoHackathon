from platformScraper import RedditScraper, TwitterScraper, CoindeskScraper
from datetime import datetime
import Preprocessor


class Scraper:
    def __init__(self):
        self.date_updated_reddit = False
        self.date_updated_twitter = False
        self.date_updated_coindesk = False

    def update_all(self):
        return [self.updatereddit(), self.updatetwitter(), self.updatecoindesk()]

    def update_reddit(self):
        # call all of our scrapers

        # scrape(timeStamp) takes a datetime object
        # and only returns posts newer than it
        scrape_date = datetime.now()
        reddit_results = RedditScraper.scrape(self.date_updated_reddit)
        processed_data = process(reddit_results)
        self.date_updated_reddit = scrape_date
        return processed_data

    def update_twitter(self):
        scrape_date = datetime.now()
        twitter_results = RedditScraper.scrape(self.date_updated_twitter)
        processed_data = process(twitter_results)
        self.date_updated_twitter = scrape_date
        return processed_data
    
    def update_coindesk(self):
        scrape_date = datetime.now()
        coindesk_results = RedditScraper.scrape(self.date_updated_coindesk)
        processed_data = process(coindesk_results)
        self.date_updated_coindesk = scrape_date
        return processed_data


def process(result):
    # deal with processing of the data through preprocessor

    pre = Preprocessor()
    result.processed_title = pre.pipe(result.title)
    result.text = pre.pipe(result.text)
    for comment in result.comments:
        result.processed_comments.append(pre.pipe(comment))

    return result
