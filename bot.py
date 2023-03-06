# bot.py
import os

import discord
from dotenv import load_dotenv
import random
from discord.ext import commands

import requests

from datetime import datetime
from discord.ext import tasks
import time

import json
from bs4 import BeautifulSoup

from Command import HelloWorld

import sys
sys.path.append(os.path.join( os.path.dirname( __file__ ), 'commands' ))
import Hotlines, Dog, Cat, Quote, Help, RedditPost, Art, Profile
import User
import utility
sys.path.append(os.path.join( os.path.dirname( __file__ ), 'objects' ))
import Timer
sys.path.append(os.path.join( os.path.dirname( __file__ ), 'loops' ))
import CheckTimers
import UpdateUserTime


helloWorld = HelloWorld()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
# client = discord.Client(intents=intents)
client = commands.Bot(intents=intents, command_prefix='$')

n = 0
lastCall = time.time()
userList = []
timeOnDiscord = []
outputChannel = 0

timerID = 1
eventID = 1
schedule = []
timers = []

userProfileList = User.UserProfileList()

class Event:
    def __init__(self, author, year, month, day, hour, minute):
        global eventID
        self.author = author
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

        self.ID = eventID
        eventID += 1

    def monthToWord(self):
        if self.month == 1:
            return "January"
        elif self.month == 2:
            return "February"
        elif self.month == 3:
            return "March"
        elif self.month == 4:
            return "April"
        elif self.month == 5:
            return "May"
        elif self.month == 6:
            return "June"
        elif self.month == 7:
            return "July"
        elif self.month == 8:
            return "August"
        elif self.month == 9:
            return "September"
        elif self.month == 10:
            return "October"
        elif self.month == 11:
            return "November"
        elif self.month == 12:
            return "December"

    def describe(self):
        description = ""
        description += "ID #" + str(self.ID) + ": "
        description += self.monthToWord() + " "
        description += str(self.day) + ", "
        description += str(self.year) + ", at "
        description += str(self.hour) + ":"
        description += str(self.minute) + "."
        return description

@tasks.loop(count=1)
async def rxnLoop(message, user):
    global userList, outputChannel
    # print(userList, outputChannel)

    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    didReact = False
    lastCall = time.time()

    while (not didReact) and (time.time() - lastCall < 10):
        reactionValue = -1
        for reaction in message.reactions:
            async for person in reaction.users():
                print(person, user)
                print(person.id)
                if person == user and person.id != 939362278703235103:
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
    
    index = userProfileList.get_user_index(user)
    if reactionValue != -1:
        await message.channel.send("Reaction made")
        userProfile = userProfileList.get_user_profile(index)
        userProfile.previous_reactions.append(reactionValue)
        userProfile.average_reaction = sum(userProfile.previous_reactions) / len (userProfile.previous_reactions)
        if len(userProfile.previous_reactions) == 6:
            userProfile.previous_reactions.remove(0)
    else:
        await message.channel.send("No reaction made")

@tasks.loop(seconds=1.0)
async def checkSchedule():
    global outputChannel
    global schedule
    newSchedule = schedule[:]
    currentTime = datetime.now()
    for event in schedule:
        currentYear = currentTime.year
        currentMonth = currentTime.month
        currentDay = currentTime.day
        currentHour = currentTime.hour
        currentMinute = currentTime.minute

        if currentYear >= event.year and currentMonth >= event.month and currentDay >= event.day \
                and currentHour >= event.hour and currentMinute >= event.minute:
            await outputChannel.send(event.author + ", event #" + str(event.ID) + " is happening now!")
            newSchedule.remove(event)
    schedule = newSchedule


@client.event
async def on_ready():
    global userList, outputChannel
    print('We have logged in as {0.user}'.format(client))

    for guild in client.guilds:
        for member in guild.members:
            userProfileList.load_user(member)
    print(userProfileList)



    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == "bot-commands":
                outputChannel = channel
    updateUserTime = UpdateUserTime.UpdateUserTime(userProfileList, outputChannel)
    updateUserTime.run_loop.start()
    checkTimers.start()
    updateTimers.start()
    checkSchedule.start()
    checkTimers2 = CheckTimers.CheckTimers(userProfileList,outputChannel)
    checkTimers2.run_loop.start()
    # checkTimers2.start()


@client.event
async def on_message(message):
    global schedule
    global timers
    messageWords = message.content.split()
    global n, lastCall, userList

    if message.author == client.user:
        return

    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '0️⃣']
    if message.content == "+test_log":
        print(userProfileList)

    if message.content == "+mood":
        react = await outputChannel.send('React to this message with how you are feeling')
        for index in range(5):
            await react.add_reaction(numbers[index])

        react = react.channel.last_message
        rxnLoop.start(react, message.author)

    if message.content == "+profile":
        index = userProfileList.get_user_index(message.author)
        userProfile = userProfileList.get_user_profile(index)
        profile = Profile.Profile(message, userProfile)
        await profile.run_command()
        

    if message.content == "+time":
        index = userProfileList.get_user_index(message.author)
        userProfile = userProfileList.get_user_profile(index)
        time = Profile.Time(message, userProfile)
        await time.run_command()

    if message.content.startswith("+setLimit"):
        content = message.content.split()
        try:
            timeAmount = int(content[1])

            if timeAmount <= 0:
                raise ValueError

            try:
                userProfile = userProfileList.get_user_profile(userProfileList.get_user_index(message.author))
                userProfile.time_limit = timeAmount 

            except:
                print("Member not found")

        except:
            await message.channel.send("Invalid time")
    if message.content.startswith("+2timer"):
        messageWords = message.content.split(" ")
        index = userProfileList.get_user_index(message.author)
        userProfile = userProfileList.get_user_profile(index)
        if messageWords[1] == "check":
            await message.channel.send(userProfile.timer_list)
        elif messageWords[1] == "remove":
            if messageWords[2] == "all":
                for i in range(len(userProfile.timer_list.timer_list)):
                    userProfile.timer_list.reset_timer(i)
            else:
                userProfile.timer_list.reset_timer(int(messageWords[2]))
        elif messageWords[1] == "pause":
            if messageWords[2] == "all":
                for i in range(len(userProfile.timer_list.timer_list)):
                    userProfile.timer_list.pause_timer(i)
            else:
                userProfile.timer_list.pause_timer(int(messageWords[2]))
        elif messageWords[1] == "unpause":
            if messageWords[2] == "all":
                for i in range(len(userProfile.timer_list.timer_list)):
                    userProfile.timer_list.unpause_timer(i)
            else:
                userProfile.timer_list.unpause_timer(int(messageWords[2]))
        else:
            userProfile.timer_list.add_new_timer(int(messageWords[1]))


    if message.content.startswith("+schedule"):
        if message.content == "+schedule" or message.content == "+schedule check":
            outputString = "Your Events:"
            for event in schedule:
                if event.author == "<@" + str(message.author.id) + ">":
                    outputString += "\n" + event.describe()
                else:
                    continue
            await message.channel.send(outputString + "\nEnd of list")
        elif messageWords[1] == "add":
            if len(messageWords) == 7:
                try:
                    year = round(float(messageWords[2]))
                    month = round(float(messageWords[3]))
                    day = round(float(messageWords[4]))
                    hour = round(float(messageWords[5]))
                    minute = round(float(messageWords[6]))

                    if year >= datetime.now().year and month > 0 and day > 0 and hour >= 0 and minute >= 0:
                        schedule.append(Event("<@" + str(message.author.id) + ">", year, month, day, hour, minute))
                        await message.channel.send("Event added to your schedule!")

                except ValueError:
                    await message.channel.send("Error: Invalid Syntax\n" +
                                               "Syntax: +schedule add\n" +
                                               "<Year> <Month> <Day> <Hour> <Minute>")
    if messageWords[0] == "+add" or messageWords[0] == "+sum":
        await message.channel.send(utility.calculateSum(messageWords[1:]))

    if messageWords[0] == "+multiply" or messageWords[0] == "+product":
        await message.channel.send(utility.calculateProduct(messageWords[1:]))

    if messageWords[0] == "+mean" or messageWords[0] == "+average":
        await message.channel.send(utility.calculateMean(messageWords[1:]))

    if message.content == "+hotlines":
        hotlines = Hotlines.Hotlines(message)
        await hotlines.run_command()
        
    if message.content.startswith("+dog"):
        dog = Dog.Dog(message)
        await dog.run_command()

    if message.content.startswith("+cat"):
        cat = Cat.Cat(message)
        await cat.run_command()

    if message.content == "+quote":
        quote = Quote.Quote(message)
        await quote.run_command()

    # Display commands
    if message.content.startswith("+help"):
        help = Help.Help(message)
        await help.run_command()
    
    if message.content.startswith("+art"):
        art = Art.Art(message)
        await art.run_command()
    
        

    # Post a joke from Reddit
    if message.content.startswith("+joke"):
        joke = reddit_post('https://oauth.reddit.com/r/Jokes/top')

        embed_var = discord.Embed(title=joke[0], description=joke[1], color=0x00ff00)
        await message.channel.send(embed=embed_var)

    # Post good news from Reddit
    if message.content.startswith("+smile"):
        smile = RedditPost.RedditPost(message, "MadeMeSmile")
        await smile.run_command()
    
    # Post a food picture from Reddit
    if message.content.startswith("+yum"):
        food = RedditPost.RedditPost(message, "Food")
        await food.run_command()

    # Post a meme from Reddit
    if message.content.startswith("+memes"):
        meme = RedditPost.RedditPost(message, "dankmemes")
        await meme.run_command()

if __name__ == "__main__":
    client.run(TOKEN)
