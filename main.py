# bot.py
import os
import random
import praw
from praw.models.helpers import SubredditHelper
from urllib.request import Request, urlopen
import json
import re
import time

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DEBUG_MODE = False

def connectReddit():
    reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                         client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                         user_agent='USER_AGENT')
    #print ("Trigger: connectReddit")
    return reddit
def getSubreddit(reddit, subredditName):
    subreddit = reddit.subreddit(subredditName)
    #print("Trigger: getSubreddit")
    return subreddit
def getSubredditPosts(subreddit):
    posts = []
    #print("Trigger: getSubredditPosts")
    for submission in subreddit.new(limit=1):
        #print("Trigger: Got submission")
        buildEmbed(submission, subreddit)
    return 

def buildEmbed(submission, subreddit):
    #builds embed
    title = submission.title
    url = submission.url
    author = submission.author
    id = submission.id
    color = random.randint(0, 16777215)
    too_long = False
    content = ''
    content2 = ''
    embed2 = ''
    isNew = newnessCheck(submission)
    if submission.is_self:
        content = submission.selftext
        if len(content) > 1000:
            content2 = '...' + content[1000:] 
            content = content[:1000] + '...'
            too_long = True                  
    else:
        content = submission.url
    embed = {
        "title": submission.title,
        "url": "https://www.reddit.com/r/"+str(subreddit)+"/comments/"+submission.id,
        "color": color,
        "author": {
            "name": submission.author.name,
            "url": "https://www.reddit.com/user/"+submission.author.name,
            "icon_url": submission.author.icon_img
        },
        "fields": [
            {
                "name": "Content",
                "value": content,
                "inline": False
            }
        ]
    }
    if too_long:
        embed2 = {        
        "color": color,
        "fields": [
            {
                "name": "Continued",
                "value": content2,
                "inline": False
            }
        ]
    }
    #print("Trigger: buildEmbed")
    if isNew:
        sendEmbed(embed)
        if too_long:
            sendEmbed(embed2)
    return

def sendEmbed(embed):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }

    payload = json.dumps({'embeds': [embed]})

    try:
         req = Request(WEBHOOK_URL, data=payload.encode(), headers=headers)
         urlopen(req)
         #print("Trigger: sendEmbed")
    except Exception as e:
        print("Error sending embed: "+str(e))
        pass

def newnessCheck(post):
    #checks if post is new
    if post.created_utc > (time.time() - 60):
        #print ("Is new")
        return True
    else:
        #print ("Is not new")
        return False


def main():
    print("Checking for new posts...")
    reddit = connectReddit()
    #read subreddit list from config.json
    with open('config.json') as json_file:
        data = json.load(json_file)
        subreddits = data['subreddits']
    for subreddit in subreddits:
        subreddit = getSubreddit(reddit, subreddit)
        getSubredditPosts(subreddit)
    return

#run main every 60 seconds
while True:
    main()
    time.sleep(60)
    