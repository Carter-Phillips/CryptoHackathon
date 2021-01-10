# Introduction

We created a text aggregation website for cryptocurrencies

Currently it will only scrape from reddit, as the other social medias we wanted to use required verified developer accounts which we did not have

We use google's entity sentiment analysis cloud function to get the sentiment in user submissions towards a list of cryptocurrencies that we have on our database.

Once we run this analysis we keep track of the daily sentiment in the database, as well as all the words that are within the user submissions which allows us to create a word map

We did not have time to implement a price/sentiment by day graph, but we have all the data in the database, it would just take a little front end work.


## Running the webiste
1. Run `pip install -r requirements.txt`
2. The dash app:
`python app.py`
3. go to `http://127.0.0.1:8050`
