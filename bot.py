# bot.py
import os

import discord
from dotenv import load_dotenv
import random

import requests
from requests.auth import HTTPBasicAuth

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

# Define variables to store Reddit login info
with open('password.txt') as f:
    lines = f.readlines()
info = []
for line in lines:
    info.append(line.removesuffix('\n'))
USERNAME = info[0]
PASSWORD = info[1]
CLIENT_ID = info[2]
SECRET_KEY = info[3]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    # Set the game
    '''
    game = discord.Game("with the API")
    await client.change_presence(status=discord.Status.idle, activity=game)
    '''


numbers = []


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        pass

        # Ping the role with the ID Number ROLE ID NUMBER (copy ID)
        # await message.channel.send('Hello! <&@ROLE ID NUMBER>')

        # Ping the user with the username ID USERNAME ID NUMBER
        # await message.channel.send('Hello! <@USERNAME ID NUMBER>')

    # Ping the user who sent the message with USERNAME ID NUMBER
    # mention = f'<@!USERNAME ID NUMBER>'
    # if mention in message.content:
    #    await message.channel.send(mention)

    if message.content.startswith('$greet'):
        channel = message.channel
        await channel.send('Say hello!')

        def check(m):
            return m.content == 'hello' and m.channel == channel

        msg = await client.wait_for('message', check=check)
        await channel.send('Hello {.author}!'.format(msg))

    if message.content.startswith('$gamble'):
        await message.channel.send(str(random.randint(1, 100)))

    if message.content.startswith("$mood"):
        channel = message.channel
        react = await channel.send('React to this message with how you are feeling')
        await react.add_reaction('👋')

    # Post a joke from Reddit
    if message.content.startswith("+ joke"):
        joke = reddit_post('https://oauth.reddit.com/r/Jokes/top')

        embed_var = discord.Embed(title=joke[0], description=joke[1], color=0x00ff00)

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post good news from Reddit
    if message.content.startswith("+ smile"):
        good_news = reddit_post('https://oauth.reddit.com/r/MadeMeSmile/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post a food picture from Reddit
    if message.content.startswith("+ yum"):
        good_news = reddit_post('https://oauth.reddit.com/r/Food/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post a meme from Reddit
    if message.content.startswith("+ memes"):
        good_news = reddit_post('https://oauth.reddit.com/r/dankmemes/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)


def reddit_post(url: str):
    """Authorize access to Reddit to get required post information. As well,
    retrieve post information and select a random post."""
    # Authenticate account and access posts on a subreddit
    auth = HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
    data = {'grant_type': 'password',
            'username': USERNAME,
            'password': PASSWORD}
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


client.run(TOKEN)
