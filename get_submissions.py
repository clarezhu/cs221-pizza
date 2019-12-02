import pandas as pd
import datetime as dt
from psaw import PushshiftAPI
import praw
import multiprocessing
import pickle



def process_object(idx):
    obj = objects[idx]
    print ("STARTING...", idx, multiprocessing.current_process())
    title = obj.title.lower()
    text = obj.selftext
    url = obj.url
    flair = obj.link_flair_text


    if obj.author is None:
        return None

    try:
        test = obj.author.created_utc
        another = obj.author.has_verified_email
    except:
        return None

    if "request]" not in title or text == "[removed]" or text == "[deleted]":
        return None

    if flair == "In Progress":
        return None

    if flair == "No Longer Needed":
        return None

    return obj


if __name__ == "__main__":

    reddit = praw.Reddit(client_id='sIF2FculBPoFMg',client_secret='ONlvY9ziXYVBhTeMvp1y4yP4Fg4',user_agent='billyisnotthegoat')

    api = PushshiftAPI(reddit)

    print("Pushshift API Initialized...")

    before_date = int(dt.datetime(2019, 11, 1).timestamp())
    after_date = int(dt.datetime(2017, 3, 1).timestamp())

    gen = api.search_submissions( after=after_date, before=before_date, subreddit='Random_Acts_Of_Pizza')
    
    
    print("Now enumerating over objects...")

    objects = list(gen)

    print ("Initializing pool...")

    pool = multiprocessing.Pool(16)
    kept = [ x for x in pool.map(process_object, range(len(objects))) if x is not None]
    pool.close()

    
    with open('submissions.pkl','wb') as f:
         pickle.dump(kept, f)
