import praw
import json
from datetime import datetime


def scrape(lastScanned):

    data = ''
    outputData=[]
    with open('./platformScraper/redditInfo.json') as jsonFile:
        data = json.load(jsonFile)

    reddit = praw.Reddit(client_id=data['credentials']['client_id'],
                         client_secret=data['credentials']['client_secret'],
                         user_agent=data['credentials']['user_agent'],
                         username=data['credentials']['username'],
                         password=data['credentials']['password'])


    for subreddit in data['subreddits']:
        for submission in reddit.subreddit(subreddit).new(limit=50):
            if (not lastScanned or datetime.fromtimestamp(submission.created) > lastScanned) and \
                    submission.link_flair_text is not None and submission.selftext != '' and \
                    submission.link_flair_text.lower() != 'comedy':
                submission.comment_sort='top'
                comArr=[]
                for comment in submission.comments:
                    comArr.append(comment.body)
                outputData.append(Post(submission.title, submission.selftext, comArr))
        print(subreddit)

    return outputData


class Post:
    def __init__(self, title, text, comments):
        self.title = title
        self.text = text
        self.comments = comments
        self.processed_title = ''
        self.processed_text = ''
        self.processed_comments = []