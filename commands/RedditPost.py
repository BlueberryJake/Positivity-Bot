import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import discord 
import random
from requests.auth import HTTPBasicAuth
import requests

#An example for writing a subclass of Command: 
class RedditPost(Command.Command):
    def __init__(self, message, subreddit_name) -> None:
        self.message = message
        self.subreddit_name = subreddit_name

    async def run_command(self):
        good_news = self.reddit_post(f'https://oauth.reddit.com/r/{self.subreddit_name}/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])
        await self.message.channel.send(embed=embed_var)
    
    def get_reddit_info(self):
        # Define variables to store Reddit login info
        with open('password.txt') as f:
            lines = f.readlines()
        info = []
        for line in lines:
            info.append(line.removesuffix('\n'))
        
        self.USERNAME = info[0]
        self.PASSWORD = info[1]
        self.CLIENT_ID = info[2]
        self.SECRET_KEY = info[3]
    
    def reddit_post(self, url: str):
        self.get_reddit_info()
        """Authorize access to Reddit to get required post information. As well,
        retrieve post information and select a random post."""
        # Authenticate account and access posts on a subreddit
        auth = HTTPBasicAuth(self.CLIENT_ID, self.SECRET_KEY)
        data = {'grant_type': 'password',
                'username': self.USERNAME,
                'password': self.PASSWORD}
        headers = {'User-Agent': 'positivitybot'}
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)
        token = res.json()['access_token']
        headers = {**headers, **{'Authorization': f"bearer {token}"}}
        requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
        res = requests.get(url, headers=headers)

        # Go through the posts and save only necessary information
        posts = []
        for post in res.json()['data']['children']:
            # If the post contains a video, save the thumbnail url
            if post['data']['is_video']:
                posts.append((post['data']['title'],
                            post['data']['selftext'],
                            post['data']['thumbnail']))

            # Otherwise, save the image url, if it exists
            else:
                posts.append((post['data']['title'],
                            post['data']['selftext'],
                            post['data']['url']))

        return random.choice(posts)  # Pick a random post to display
