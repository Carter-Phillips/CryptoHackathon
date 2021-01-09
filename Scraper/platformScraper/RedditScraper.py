import praw
import json



def scrape(lastScrapped):

    data = ''
    outputData=[]
    with open('redditInfo.json') as jsonFile:
        data = json.load(jsonFile)

    reddit = praw.Reddit(client_id=data['credentials']['client_id'],
                         client_secret=data['credentials']['client_secret'],
                         user_agent=data['credentials']['user_agent'],
                         username=data['credentials']['username'],
                         password=data['credentials']['password'])


    for subreddit in data['subreddits']:
        for submission in reddit.subreddit(subreddit).new(limit=20):
            if submission.link_flair_text is not None and submission.selftext != '' and submission.link_flair_text.lower() != 'comedy':
                submission.comment_sort='top'
                comArr=[]
                for comment in submission.comments:
                    comArr.append(comment.body)
                outputData.append(Post(submission.title, submission.selftext, comArr))

    return outputData


class Post:
    def __init__(self, title, text, comments):
        self.title = title
        self.text = text
        self.comments = comments
