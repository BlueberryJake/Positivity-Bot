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

class Timer2:
    def __init__(self, seconds=0, minutes=0):
        self.seconds = seconds
        self.paused = False
    
    def tick(self):
        if not self.paused:
            self.seconds -= 1
        return self.seconds == 0
    
    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.pause = False

class TimerList:
    def __init__(self, list) -> None:
        self.timer_list = list
    
    def add_timer(self, timer):
        self.timer_list.append(timer)
    
    def tick_all(self):
        for timer in self.timer_list:
            timer.tick()
    





class Timer:
    def __init__(self, author, weeks=0, days=0, hours=0, minutes=0, seconds=0, paused=False):
        global timerID
        self.author = author

        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.setFromTotalSeconds(self.toTotalSeconds())

        self.paused = paused
        self.ID = timerID
        timerID += 1

    def tick(self):
        if not self.paused:
            self.seconds -= 1
            self.setFromTotalSeconds(self.toTotalSeconds())

    def toTotalSeconds(self):
        totalSeconds = 0
        totalSeconds += self.seconds
        totalSeconds += self.minutes * 60
        totalSeconds += self.hours * 60 * 60
        totalSeconds += self.days * 60 * 60 * 24
        totalSeconds += self.weeks * 60 * 60 * 24 * 7
        return totalSeconds

    def setFromTotalSeconds(self, totalSeconds):
        self.weeks = totalSeconds // (60 * 60 * 24 * 7)

        totalSeconds -= self.weeks * (60 * 60 * 24 * 7)
        self.days = totalSeconds // (60 * 60 * 24)

        totalSeconds -= self.days * (60 * 60 * 24)
        self.hours = totalSeconds // (60 * 60)

        totalSeconds -= self.hours * (60 * 60)
        self.minutes = totalSeconds // 60

        totalSeconds -= self.minutes * 60
        self.seconds = totalSeconds

    def getTimeLeft(self):
        return [self.weeks, self.days, self.hours, self.minutes, self.seconds]

    def getAuthor(self):
        return self.author

    def getID(self):
        return self.ID

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def describe(self):
        description = ""
        description += "ID #" + str(self.ID) + ": "
        description += str(self.weeks) + " weeks, "
        description += str(self.days) + " days, "
        description += str(self.hours) + " hours, "
        description += str(self.minutes) + " minutes, "
        description += str(self.seconds) + " seconds."
        return description


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


@tasks.loop(seconds=5.0)
async def newLoop():
    global outputChannel
    for user_index in range (len(userProfileList.user_profile_list)):
        userProfile = userProfileList.get_user_profile(user_index)
        user = userProfile.user_info.rawUser

        if user.status == discord.Status.online or user.status == discord.Status.dnd:
            userProfile.add_time(5)
        
        if user.status == discord.Status.offline or user.status == discord.Status.invisible:
            userProfile.reset_time()
        
        if userProfile.seconds_online == userProfile.time_limit:
            outputString = "Get out <@" + str(user.id) + "> !"
            await outputChannel.send(outputString)
        
        # print(user, userProfile.seconds_online)

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
async def checkTimers2():
    for userProfile in userProfileList.user_profile_list:
        for timer in userProfile.timer_list.timer_list:
            if timer.tick():
                await outputChannel.send(str(userProfile.user_info.rawUser.id))



@tasks.loop(seconds=1.0)
async def checkTimers():
    global outputChannel
    global timers
    newTimers = timers[:]
    for timer in timers:
        if timer.getTimeLeft() == [0, 0, 0, 0, 0]:
            await outputChannel.send(str(timer.getAuthor()) + ", timer #" + str(timer.ID) + " has rung!")
            newTimers.remove(timer)
    timers = newTimers


@tasks.loop(seconds=1.0)
async def updateTimers():
    global timers
    for timer in timers:
        timer.tick()


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

    for user in userProfileList.user_profile_list:
        user.timer_list = TimerList([])

    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == "bot-commands":
                outputChannel = channel
    newLoop.start()
    checkTimers.start()
    updateTimers.start()
    checkSchedule.start()
    checkTimers2.start()


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
        outputString = "You were on discord for " + str(
            userList[[u.rawUser for u in userList].index(message.author)].timeOn) + " seconds"
        await message.channel.send(outputString)

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
        index = userProfileList.get_user_index(message.author)
        userProfile = userProfileList.get_user_profile(index)

        userProfile.timer_list.add_timer(Timer2(10))

    if message.content.startswith("+timer"):  # Timer
        modifiedTimers = False
        if message.content == "+timer" or message.content == "+timer check":
            outputString = "Your Timers:"
            for timer in timers:
                if timer.getAuthor() == "<@" + str(message.author.id) + ">":
                    outputString += "\n" + timer.describe()
                else:
                    continue
            await message.channel.send(outputString + "\nEnd of list")

        elif message.content.startswith("+timer remove"):
            newTimers = timers[:]
            if messageWords[2] == "all":
                for timer in timers:
                    if timer.getAuthor() == "<@" + str(message.author.id) + ">":
                        newTimers.remove(timer)
                timers = newTimers[:]
                await message.channel.send("Successfully removed all timers!")
            else:
                try:
                    chosenID = int(messageWords[2])
                    newTimers = timers[:]
                    for timer in timers:
                        if timer.getAuthor() == "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                            newTimers.remove(timer)
                            await message.channel.send("Successfully removed timer #" + str(timer.getID()) + "!")
                            modifiedTimers = True
                            break
                        elif timer.getAuthor() != "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                            await message.channel.send("Error: That is not your timer!")
                            break
                    timers = newTimers[:]
                    if not modifiedTimers:
                        await message.channel.send("Error: Timer ID not found!")
                except ValueError:
                    await message.channel.send("Error: Not a number\nSyntax: +timer remove <timer ID number>")

        elif message.content.startswith("+timer pause"):
            try:
                chosenID = int(messageWords[2])
                for timer in timers:
                    if timer.getAuthor() == "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                        timer.pause()
                        await message.channel.send("Successfully paused timer #" + str(timer.getID()) + "!")
                        modifiedTimers = True
                        break
                    elif timer.getAuthor() != "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                        await message.channel.send("Error: That is not your timer!")
                        break
                if not modifiedTimers:
                    await message.channel.send("Error: Timer ID not found!")
            except ValueError:
                await message.channel.send("Error: Not a number\nSyntax: +timer pause <timer ID number>")

        elif message.content.startswith("+timer unpause"):
            try:
                chosenID = int(messageWords[2])
                for timer in timers:
                    if timer.getAuthor() == "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                        timer.unpause()
                        await message.channel.send("Successfully unpaused timer #" + str(timer.getID()) + "!")
                        modifiedTimers = True
                        break
                    elif timer.getAuthor() != "<@" + str(message.author.id) + ">" and timer.getID() == chosenID:
                        await message.channel.send("Error: That is not your timer!")
                        break
                if not modifiedTimers:
                    await message.channel.send("Error: Timer ID not found!")
            except ValueError:
                await message.channel.send("Error: Not a number\nSyntax: +timer unpause <timer ID number>")

        elif len(messageWords) >= 1:
            try:
                numMinutes = round(float(messageWords[1]))
                if numMinutes <= 0:
                    await message.channel.send(
                        "Error: Number greater than 0\nSyntax: +timer <Number of Minutes (integer > 0)>")
                else:
                    timers.append(Timer("<@" + str(message.author.id) + ">", 0, 0, 0, numMinutes, 0, False))
                    await message.channel.send(str(numMinutes) + " minute timer has begun!")
            except ValueError:
                await message.channel.send("Error: Not a number\nSyntax: +timer <Number of Minutes (integer > 0)>")

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
