import os
import tweepy as tw
import time
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import re
from credentials import Credentials

#import passwords
credential = Credentials()

#connect to postgresql database
engine = create_engine(credential.psql_endpoint)
 
metadata = MetaData()
tweets = Table('singapore_tweets_v2', metadata,
        Column('id', Integer, primary_key=True),
        Column('date', String),
        Column('user', String),
        Column('tweet', String),
        Column('retweet', String),
)

metadata.create_all(engine)

#connect to twitter API
consumer_key= credential.consumer_key
consumer_secret= credential.consumer_secret
access_token= credential.access_token
access_token_secret= credential.access_token_secret
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)

class MyStreamListener(tw.StreamListener):

    def on_status(self, status):
        try:
            if hasattr(status, "retweeted_status"):  # Check if Retweet
                try:
                    data = status.retweeted_status.extended_tweet["full_text"]
                except AttributeError:
                    data = status.retweeted_status.text
		else:
		    pass
		try:
                    query = tweets.insert().values(date=status.created_at, user=status.user.name, tweet=data, retweet='Y')
                    conn = engine.connect()
                    conn.execute(query)
		except:
		    pass
            else:
                try:
                    data = status.extended_tweet["full_text"]
                except AttributeError:
                    data = status.text
		else:
		    pass
		try:
                    query = tweets.insert().values(date=status.created_at, user=status.user.name, tweet=data, retweet='N')
                    conn = engine.connect()
                    conn.execute(query)
		except:
		    pass
        except tw.RateLimitError:
            time.sleep(60*15)
        else:
            pass

if __name__=='__main__':
    while True:
        myStreamListener = MyStreamListener()
        myStream = tw.Stream(auth = api.auth, listener=myStreamListener)
        myStream.filter(track=['singapore'])

