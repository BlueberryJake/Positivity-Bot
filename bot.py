# bot.py
import os

import discord
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    #Set the game
    '''
    game = discord.Game("with the API")
    await client.change_presence(status=discord.Status.idle, activity=game)
    '''
numbers = [ ]

@client.event
async def on_message(message):



    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        pass


        # Ping the role with the ID Number ROLE ID NUMBER (copy ID)
        # await message.channel.send('Hello! <&@ROLE ID NUMBER>')


        #Ping the user with the username ID USERNAME ID NUMBER
        #await message.channel.send('Hello! <@USERNAME ID NUMBER>')

    #Ping the user who sent the message with USERNAME ID NUMBER
    #mention = f'<@!USERNAME ID NUMBER>'
    #if mention in message.content:
    #    await message.channel.send(mention)

    if message.content.startswith('$greet'):
        channel = message.channel
        await channel.send('Say hello!')

        def check(m):
            return m.content == 'hello' and m.channel == channel

        msg = await client.wait_for('message', check=check)
        await channel.send('Hello {.author}!'.format(msg))

    if message.content.startswith('$gamble'):
        await message.channel.send(str(random.randint(1,100)))


    if message.content.startswith("$mood"):
        channel = message.channel
        react = await channel.send('React to this message with how you are feeling')
        await react.add_reaction('👋')

client.run(TOKEN)
