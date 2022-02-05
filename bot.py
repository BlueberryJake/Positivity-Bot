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
timeOnDiscord = []
outputChannel = 0
        

@tasks.loop(seconds=5.0)
async def newLoop():
    global timeOnDiscord
    for guild in client.guilds:
            for member in guild.members:
                if member.status == discord.Status.online or member.status == discord.Status.dnd:
                    try: 
                        timeOnDiscord[1][timeOnDiscord[0].index(member)] += 5
                    except:
                        print("Member not found")
                if member.status == discord.Status.offline or member.status == discord.Status.invisible:
                    try: 
                        timeOnDiscord[1][timeOnDiscord[0].index(member)] = 0
                    except:
                        print("Member not found")

@tasks.loop(seconds=5.0)
async def checkOvertime():
    global timeOnDiscord, outputChannel
    print(timeOnDiscord)
    for guild in client.guilds:
        for member in guild.members:
            index = timeOnDiscord[0].index(member)
            if timeOnDiscord[1][index] == timeOnDiscord[2][index] and timeOnDiscord[2][index] != -1:
                #timeOnDiscord[2][index] += 20
                outputString = "Get out <@" + str(member.id) + "> !"
                await outputChannel.send(outputString)

@client.event
async def on_ready():
    global timeOnDiscord, outputChannel
    print('We have logged in as {0.user}'.format(client))
    for guild in client.guilds:
            for member in guild.members:
                userList.append(member)
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == "bot-commands":
                outputChannel = channel
    userTime = [0] * len(userList)
    userSetTime = [-1] * len(userList)
    timeOnDiscord = [userList,userTime,userSetTime]
    newLoop.start()
    checkOvertime.start()

@client.event
async def on_message(message):
    global n, lastCall
    if message.author == client.user:
        return

    if message.content.startswith('c'):

        if time.time() - lastCall < 3:
            await message.channel.send("Wait 3 sec")

        else:
            await message.channel.send(n)
            n = n + 1
            lastCall = time.time()
    
    if message.content == "e":
        embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
        embedVar.add_field(name="Field1", value="hi", inline=False)
        embedVar.add_field(name="Field2", value="hi2", inline=False)
        await message.channel.send(embed=embedVar)

    if message.content == "+ profile":
        outputString = "You were on discord for " + str(timeOnDiscord[1][timeOnDiscord[0].index(message.author)]) + " seconds"
        embedVar = discord.Embed(title=message.author.name, description="Here are following relavent stats", color=0x00ff00)
        embedVar.add_field(name="Time on discord", value=outputString, inline=False)
        embedVar.add_field(name="Field2", value="hi2", inline=False)
        await message.channel.send(embed=embedVar)

    if message.content == "mem":
        for guild in client.guilds:
            for member in guild.members:
                await message.channel.send(member.id)
    
    if message.content == "+ time":
        #print(message.author.id)
        outputString = "You were on discord for " + str(timeOnDiscord[1][timeOnDiscord[0].index(message.author)]) + " seconds"
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
                timeOnDiscord[2][timeOnDiscord[0].index(message.author)] = timeAmount

            except:
                print("Member not found")

        except:
            await message.channel.send("Invalid time")

client.run(TOKEN)
