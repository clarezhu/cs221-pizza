import requests
import pandas as pd
import datetime as dt
import multiprocessing
import praw
from pandas.io.json import json_normalize
from psaw import PushshiftAPI
import pickle




def getSubComments(comment, subComments, verbose=True):
    if isinstance(comment, praw.models.reddit.comment.Comment):
        subComments.append(comment)
    if not hasattr(comment, "replies"):
        replies = comment.comments()
        #if verbose: print("fetching (" + str(len(subComments)) + " comments fetched total)")
    else:
        replies = comment.replies
    for child in replies:
        getSubComments(child, subComments, verbose=verbose)


def construct_features(idx): #index in submissions
        GiversBotId = 'np6d0'
        submission = submissions[idx]
        #print("STARTING...", idx)
        d = {}

        d['request_id'] = submission.id
        d['request_number_of_comments_at_retrieval'] = submission.num_comments
        d['request_text'] = submission.selftext.lower()
        d['request_title'] = submission.title

        d['number_of_downvotes_of_request_at_retrieval'] = submission.downs
        d['number_of_upvotes_of_request_at_retrieval'] = submission.ups

        if submission.edited == False:
            d['post_was_edited'] = False
        else:
            d['post_was_edited'] = True



        d['requester_account_age_in_days_at_request'] = divmod(submission.created_utc - submission.author.created_utc, 86400)[0]

        d['request_url'] = submission.url


        try:
            requester_created_utc = submission.author.created_utc
        except: #if created_utc is not an attribute, the author has been suspended
            return


        requester_subreddits_at_request = set()

        for author_comment in submission.author.comments.top('all'):
            if author_comment.subreddit.created_utc < submission.created_utc:
                requester_subreddits_at_request.add(author_comment.subreddit.display_name)

        for author_sub in submission.author.submissions.top('all'):
            if author_sub.subreddit.created_utc < submission.created_utc:
                requester_subreddits_at_request.add(author_sub.subreddit.display_name)

        top_level_comments = list(submission.comments)

        d['requester_num_pizza_received_at_request'] = None
        d['requester_num_pizza_given_at_request'] = None
        d['requester_num_pizza_related_posts_at_request'] = None
        d['requester_num_pizza_related_comments_at_request'] = None

        d['giver_username'] = None
        d['giver_user_flair'] = None
        giver_redditor = None

        for tl_comment in top_level_comments:
            tl_text = tl_comment.body.lower()
            child_comments = []
            getSubComments(tl_comment, child_comments)
            for child_comment in child_comments:
                if "GIFT transaction #"  in child_comment.body:
                    info_lines = child_comment.body.splitlines()
                    for info_line in info_lines:
                        if "**A**" in info_line:
                            info_split = info_line.split("|")
                            giver_redditor_name = info_split[2][3:]
                            giver_redditor = reddit.redditor(giver_redditor_name)
                            d['giver_username'] = giver_redditor_name

            try:
                if tl_comment.author.id == GiversBotId:
                    if "* **Received" in tl_comment.body:
                        info_lines = tl_comment.body.splitlines()
                        d['requester_num_pizza_received_at_request'] = int(info_lines[0].split()[2] )
                        d['requester_num_pizza_given_at_request'] = int(info_lines[1].split()[2] )
                        d['requester_num_pizza_related_posts_at_request'] = int(info_lines[2].split()[2])
                        d['requester_num_pizza_related_comments_at_request'] = int(info_lines[2].split()[7])
            except Exception as e:
                continue



        giver_subreddits_at_request = set()
        if giver_redditor:

            for author_comment in giver_redditor.comments.top('all'):
                if author_comment.subreddit.created_utc < submission.created_utc:
                    giver_subreddits_at_request.add(author_comment.subreddit.display_name)

            for author_sub in giver_redditor.submissions.top('all'):
                if author_sub.subreddit.created_utc < submission.created_utc:
                    giver_subreddits_at_request.add(author_sub.subreddit.display_name)


        d['giver_subreddits_at_request'] = list(giver_subreddits_at_request)

        d['requester_subreddits_at_request'] = list(requester_subreddits_at_request)

        d['requester_has_verified_email'] = submission.author.has_verified_email

        d['requester_received_pizza'] = 0
        if submission.link_flair_text == "Fulfilled":
            d['requester_received_pizza'] = 1

        d['requester_user_flair'] = submission.author_flair_text
        d['requester_username'] = submission.author.name
        d['unix_timestamp_of_request'] = submission.created_utc

        print(idx,submission.link_flair_text, d['giver_username'], d['request_url'])

        #if d['requester_received_pizza']:
        #    if (d['giver_username'] == None):
                #print ("WHYYY")


        return d


if __name__ == '__main__':
    reddit = praw.Reddit(client_id='sIF2FculBPoFMg',
                     client_secret='ONlvY9ziXYVBhTeMvp1y4yP4Fg4',
                     user_agent='billyisnotthegoat')

    api = PushshiftAPI(reddit)



    submissions = None
    with open('submissions.pkl','rb') as f:
        submissions = pickle.load(f)
    pool = multiprocessing.Pool(8)


    dict_list = pool.map(construct_features, range(500))
    pool.close()



    df = pd.DataFrame(json_normalize(dict_list))
    pd.to_csv("new.csv", sep = "\t")

    with open('dict_list.pkl', 'wb') as f:
         pickle.dump(dict_list, f)
