# bot.py
from collections import UserList
import os
import time
import discord
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

n = 0
lastCall = time.time()
userList = []
outputChannel = 0

class userInfo:
    def __init__(self, u):
        self.rawUser = u
        self.totalTimeToday = 0
        self.timeOn = 0
        self.timeLimit = -1

@tasks.loop(seconds=5.0)
async def newLoop():
    global userList, outputChannel
    for guild in client.guilds:
            for member in guild.members:
                if member.status == discord.Status.online or member.status == discord.Status.dnd:
                    try: 
                        userList[[u.rawUser for u in userList].index(member)].timeOn += 5
                    except:
                        print("Member not found")
                if member.status == discord.Status.offline or member.status == discord.Status.invisible:
                    try:
                        userList[[u.rawUser for u in userList].index(member)].totalTimeToday += userList[[u.rawUser for u in userList].index(member)].timeOn
                        userList[[u.rawUser for u in userList].index(member)].timeOn = 0
                    except:
                        print("Member not found")
    for user in userList:
        if user.timeOn == user.timeLimit:
            outputString = "Get out <@" + str(user.rawUser.id) + "> !"
            await outputChannel.send(outputString)

@client.event
async def on_ready():
    global userList, outputChannel
    print('We have logged in as {0.user}'.format(client))
    for guild in client.guilds:
            for member in guild.members:
                userList.append(userInfo(member))
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == "bot-commands":
                outputChannel = channel
    newLoop.start()

@client.event
async def on_message(message):
    global n, lastCall, userList
    if message.author == client.user:
        return

    if message.content.startswith('c'):

        if time.time() - lastCall < 3:
            await message.channel.send("Wait 3 sec")

        else:
            await message.channel.send(n)
            n = n + 1
            lastCall = time.time()


    if message.content == "+ profile":
        outputString = "You were on discord for " + str(userList[[u.rawUser for u in userList].index(message.author)].timeOn) + " seconds"
        embedVar = discord.Embed(title=message.author.name, description="Here are following relavent stats", color=0x00ff00)
        embedVar.add_field(name="Total time on discord today", value=outputString, inline=False)
        embedVar.add_field(name="Schedule", value="idk", inline=False)
        await message.channel.send(embed=embedVar)

    if message.content == "mem":
        for guild in client.guilds:
            for member in guild.members:
                await message.channel.send(member.id)
    
    if message.content == "+ time":
        #print(message.author.id)
        outputString = "You were on discord for " + str(userList[[u.rawUser for u in userList].index(message.author)].timeOn) + " seconds"
        await message.channel.send(outputString)
    
    if message.content.startswith("+ setTimer"):
        content = message.content.split()
        print(content)
        try:
            timeAmount = int(content[2])
            print(timeAmount)

            if timeAmount <= 0:
                raise ValueError

            try: 
                userList[[u.rawUser for u in userList].index(message.author)].timeLimit = timeAmount

            except:
                print("Member not found")

        except:
            await message.channel.send("Invalid time")

client.run(TOKEN)
