import pandas as pd
import datetime as dt
from psaw import PushshiftAPI
import praw
import pickle

reddit = praw.Reddit(client_id='sIF2FculBPoFMg',client_secret='ONlvY9ziXYVBhTeMvp1y4yP4Fg4',user_agent='billyisnotthegoat')

api = PushshiftAPI(reddit)

print("Pushshift API Initialized...")

before_date = int(dt.datetime(2019, 11, 1).timestamp())
after_date = int(dt.datetime(2017, 3, 1).timestamp())

gen = api.search_submissions( after=after_date, before=before_date, subreddit='Random_Acts_Of_Pizza')

print("Now enumerating over objects...")

objects = list(gen)

kept = []

count = 0


for idx, obj in enumerate(objects):
    if idx % 100 == 0:
        print (idx)
    title = obj.title.lower()
    text = obj.selftext
    url = obj.url
    flair = obj.link_flair_text


    if obj.author == None:
        continue

    try:
        test = obj.author.created_utc
    except:
        continue

    if "request]" not in title or text == "[removed]" or text == "[deleted]":
        continue

    if flair == "No Longer Needed":
        continue

    if flair == "Fulfilled":
        count += 1

    kept.append(obj)



print (len(objects), count, len(kept))

print ("percentage of fulfilled:",  count / len(kept))

with open('submissions.pkl','wb') as f:
    pickle.dump(kept, f)
