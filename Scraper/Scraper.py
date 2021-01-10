from platformScraper import RedditScraper, TwitterScraper, CoindeskScraper
from datetime import datetime


class Scraper:
    def __init__(self):
        self.date_updated_reddit = ''
        self.date_updated_twitter = ''
        self.date_updated_coindesk = ''

    def updateall(self):
        return [self.updatereddit(), self.updatetwitter(), self.updatecoindesk()]

    def updatereddit(self):
        # call all of our scrapers

        # scrape(timeStamp) takes a datetime object
        # and only returns posts newer than it
        scrape_date = datetime.now()
        reddit_results = RedditScraper.scrape(self.date_updated_reddit)
        processed_data = process(reddit_results)
        self.date_updated_reddit = scrape_date
        return processed_data

    def updatetwitter(self):
        scrape_date = datetime.now()
        twitter_results = RedditScraper.scrape(self.date_updated_twitter)
        processed_data = process(twitter_results)
        self.date_updated_twitter = scrape_date
        return processed_data
    
    def updatecoindesk(self):
        scrape_date = datetime.now()
        coindesk_results = RedditScraper.scrape(self.date_updated_coindesk)
        processed_data = process(coindesk_results)
        self.date_updated_coindesk = scrape_date
        return processed_data


def process(results):
    # deal with processing of the data through preprocessor

    # result.processed_title = Preprocess.pipe(result.title)
    # result.text = Preprocess.pipe(result.text)
    # for comment in result.comments:
    #     result.processed_comments.append(Preprocess.pipe(result.title))

    return results
