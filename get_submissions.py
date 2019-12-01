import pandas as pd
import datetime as dt
from psaw import PushshiftAPI
import praw 
import pickle

reddit = praw.Reddit(client_id='sIF2FculBPoFMg',
                             client_secret='ONlvY9ziXYVBhTeMvp1y4yP4Fg4',
                                                  user_agent='billyisnotthegoat')

api = PushshiftAPI(reddit)

before_date = int(dt.datetime(2019, 11, 1).timestamp())
after_date = int(dt.datetime(2017, 3, 1).timestamp())

gen = api.search_submissions( after=after_date, before=before_date, subreddit='Random_Acts_Of_Pizza')

objects = list(gen)

kept = []

count = 0



