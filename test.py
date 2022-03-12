import discord
from discord.ext import commands

# Used for web scrapping
import json
from bs4 import BeautifulSoup
import requests
import random

QUOTES_URL = 'https://zenquotes.io/api/quotes/[key]?option1=value&option2=value'


# Return the text on a website given a URL
def getTextData(URL):
    request = requests.get(URL)
    html_content = BeautifulSoup(request.content, 'html.parser')
    return html_content.get_text()


# Code obtained from
# https://www.youtube.com/watch?v=vQw8cFfZPx0

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Hello!")

    # Commands
    @commands.command()
    async def repeatWords(self, ctx, *words):
        for word in words:
            await ctx.send(word)

    @commands.command()
    async def quote(self, ctx):
        data = getTextData(QUOTES_URL)
        parse = json.loads(data)
        quote = random.choice(parse)
        embedVar = discord.Embed(title=quote.get('q'), description=quote.get('a'), color=0x000080)
        await ctx.send(embed=embedVar)


def setup(client):
    client.add_cog(Test(client))
