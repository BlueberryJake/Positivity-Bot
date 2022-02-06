# bot.py
from collections import UserList
import os
import time
import discord
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.reactions = True
client = discord.Client(intents=intents)

n = 0
userList = []
outputChannel = 0

class userInfo:
    def __init__(self, u):
        self.rawUser = u
        self.totalTimeToday = 0
        self.timeOn = 0
        self.timeLimit = -1
        self.prevFiveReactions = []
        self.averageReaction = None

@tasks.loop(seconds=5.0)
async def newLoop():
    global userList, outputChannel
    for guild in client.guilds:
            for member in guild.members:
                try: 
                    index = [u.rawUser for u in userList].index(member)
                
                    if member.status == discord.Status.online or member.status == discord.Status.dnd:
                        userList[index].timeOn += 5
                        userList[index].totalTimeToday += 5

                    if member.status == discord.Status.offline or member.status == discord.Status.invisible:
                        userList[index].timeOn = 0

                except:
                    print("Member not found")
    for user in userList:
        if user.timeOn == user.timeLimit:
            outputString = "Get out <@" + str(user.rawUser.id) + "> !"
            await outputChannel.send(outputString)

@tasks.loop(count=1)
async def rxnLoop(message, user):
    global userList, outputChannel

    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    didReact = False
    lastCall = time.time()

    while (not didReact) and (time.time()-lastCall < 5):
        reactionValue = -1
        for reaction in message.reactions:
            async for person in reaction.users():
                    if person == user:
                        try:
                            reactionValue = 1 + numbers.index(reaction.emoji)
                            didReact = True
                            break
                        except:
                            reactionValue = -1
            if didReact:
                    break
        if didReact:
            break

    index = [u.rawUser for u in userList].index(user)
    if reactionValue != -1:
        await message.channel.send("Reaction made") 
        userList[index].prevFiveReactions.append(reactionValue)
        userList[index].averageReaction = sum(userList[index].prevFiveReactions)/len(userList[index].prevFiveReactions)
        if(len(userList[index].prevFiveReactions) == 6):
            userList[index].prevFiveReactions.remove(0)
    else:
        await message.channel.send("No reaction made") 

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

    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '0️⃣']

    if message.content == "+mood":
        react = await outputChannel.send('React to this message with how you are feeling')
        for index in range(5):
            await react.add_reaction(numbers[index])

        react = react.channel.last_message
        rxnLoop.start(react, message.author)

    if message.content == "+profile":
        outputString = "You were on discord for " + str(userList[[u.rawUser for u in userList].index(message.author)].totalTimeToday) + " seconds"
        embedVar = discord.Embed(title=message.author.name, description="Here are following relavent stats", color=0x00ff00)
        embedVar.add_field(name="Total time on discord today", value=outputString, inline=False)
        embedVar.add_field(name="Recent average mood", value=str(userList[[u.rawUser for u in userList].index(message.author)].averageReaction)[0:3], inline=False)
        await message.channel.send(embed=embedVar)
    
    if message.content == "+time":
        outputString = "You were on discord for " + str(userList[[u.rawUser for u in userList].index(message.author)].timeOn) + " seconds"
        await message.channel.send(outputString)
    
    if message.content.startswith("+setLimit"):
        content = message.content.split()
        try:
            timeAmount = int(content[2])

            if timeAmount <= 0:
                raise ValueError

            try: 
                userList[[u.rawUser for u in userList].index(message.author)].timeLimit = timeAmount

            except:
                print("Member not found")

        except:
            await message.channel.send("Invalid time")

client.run(TOKEN)
