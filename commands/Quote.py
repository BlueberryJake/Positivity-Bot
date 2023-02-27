import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import utility
import json
import random
import discord

class Quote(Command.Command):
    QUOTES_URL = 'https://zenquotes.io/api/quotes/[key]?option1=value&option2=value'

    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        data = utility.getTextData(self.QUOTES_URL)
        parse = json.loads(data)
        quote = random.choice(parse)
        embedVar = discord.Embed(title=quote.get('q'), description=quote.get('a'), color=0x000080)
        await self.message.channel.send(embed=embedVar)