import requests
import pandas as pd
import datetime as dt
from psaw import PushshiftAPI


api = PushshiftAPI()

before_date = int(dt.datetime(2019, 11, 1).timestamp())

gen = api.search_submissions( before=before_date, mod_removed=False, subreddit='Random_Acts_Of_Pizza', limit=5)

objects = list(gen)

kept = []

for object in objects:
    dict = object.d_
    lc_title = dict["title"].lower()
    if "request]" in lc_title:
        kept.append(object)
        print (dict["selftext"], "||||||", dict["title"])

print (kept)


print (pd.DataFrame(kept))
