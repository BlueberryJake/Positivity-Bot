# bot.py
import os
from datetime import datetime

import discord
from discord.ext import tasks
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

client = discord.Client()

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    loop.start()

    #Set the game
    '''
    game = discord.Game("with the API")
    await client.change_presence(status=discord.Status.idle, activity=game)
    '''
numbers = [ ]a

@tasks.loop(seconds = 5.0)
async def loop():

    await message.channel.send("Time passed: ")

@client.event
async def on_message(message):
    global schedule
    global startTime

    if message.content.startswith("$schedule"):
        messageWords = message.content.split()



    if message.content.startswith("$timer"):
        messageWords = message.content.split()

        startTime = datetime.now()

        if messageWords.length() >= 1:
            try:
                int(messageWords[1])

        await message.channel.send(str(startTime.strftime(r"%I:%M:%S")))
        # Times will always be in the time zone of the host
        # r"%I:%M:%S %p" will give it in AM/PM



    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        pass


        # Ping the role with the ID Number ROLE ID NUMBER (copy ID)
        # await message.channel.send("Hello! <&@ROLE ID NUMBER>")


        #Ping the user with the username ID USERNAME ID NUMBER
        #await message.channel.send("Hello! <@USERNAME ID NUMBER>")

    #Ping the user who sent the message with USERNAME ID NUMBER
    #mention = f"<@!USERNAME ID NUMBER>"
    #if mention in message.content:
    #    await message.channel.send(mention)

    if message.content.startswith("$greet"):
        channel = message.channel
        await channel.send("Say hello!")

        def check(m):
            return m.content == "hello" and m.channel == channel

        msg = await client.wait_for("message", check=check)
        await channel.send("Hello {.author}!".format(msg))

    if message.content.startswith("$gamble"):
        await message.channel.send(str(random.randint(1,100)))


    if message.content.startswith("$mood"):
        channel = message.channel
        react = await channel.send("React to this message with how you are feeling")
        await react.add_reaction("👋")

client.run(TOKEN)