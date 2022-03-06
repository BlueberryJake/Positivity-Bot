# bot.py
import os

import discord
from dotenv import load_dotenv
import random

import requests
from requests.auth import HTTPBasicAuth

from datetime import datetime
from discord.ext import tasks
import time

import json
from bs4 import BeautifulSoup

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

# ================== CONSTANTS ====================
hotlines = ['Canada Drug Rehab Addiction Services Directory', '1-866-462-6362',
            'Centre for Suicide Prevention', '1-833-456-4566',
            'Crisis Services Canada', '1-833-456-4566, or text 45645',
            'First Nations and Inuit Hope for Wellness Help Line', '1‑855‑242-3310',
            'Kids Help Phone', '1-800-668-6868',
            'National Eating Disorder Information Centre', '1-866-633-4220',
            'Native Youth Crisis Hotline', '1-877-209-1266']

RANDOM_DOG_URL = 'https://dog.ceo/api/breeds/image/random'
BREED_DOG_URL_1 = 'https://dog.ceo/api/breed/'
BREED_DOG_URL_2 = '/images/random'

RANDOM_CAT_URL = 'https://api.thecatapi.com/v1/images/search'
BREED_CAT_URL = "https://api.thecatapi.com/v1/breeds"
BREED_CAT_URL_2 = 'https://api.thecatapi.com/v1/images/search?breed_ids='

QUOTES_URL = 'https://zenquotes.io/api/quotes/[key]?option1=value&option2=value'

USERNAME = info[0]
PASSWORD = info[1]
CLIENT_ID = info[2]
SECRET_KEY = info[3]

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

n = 0
lastCall = time.time()
userList = []
timeOnDiscord = []
outputChannel = 0

timerID = 1
eventID = 1
schedule = []
timers = []


class UserInfo:
    def __init__(self, u):
        self.rawUser = u
        self.totalTimeToday = 0
        self.timeOn = 0
        self.timeLimit = -1
        self.prevFiveReactions = []
        self.averageReaction = None



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

    while (not didReact) and (time.time() - lastCall < 5):
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
        userList[index].averageReaction = sum(userList[index].prevFiveReactions) / len(
            userList[index].prevFiveReactions)
        if len(userList[index].prevFiveReactions) == 6:
            userList[index].prevFiveReactions.remove(0)
    else:
        await message.channel.send("No reaction made")


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
            userList.append(UserInfo(member))

    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == "bot-commands":
                outputChannel = channel
    newLoop.start()
    checkTimers.start()
    updateTimers.start()
    checkSchedule.start()


@client.event
async def on_message(message):
    global schedule
    global timers
    messageWords = message.content.split()
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
        outputString = "You were on discord for " + str(
            userList[[u.rawUser for u in userList].index(message.author)].totalTimeToday) + " seconds"
        embedVar = discord.Embed(title=message.author.name, description="Here are following relevant stats",
                                 color=0x00ff00)
        embedVar.add_field(name="Total time on discord today", value=outputString, inline=False)
        embedVar.add_field(name="Recent average mood",
                           value=str(userList[[u.rawUser for u in userList].index(message.author)].averageReaction)[
                                 0:3], inline=False)
        await message.channel.send(embed=embedVar)

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
                userList[[u.rawUser for u in userList].index(message.author)].timeLimit = timeAmount

            except:
                print("Member not found")

        except:
            await message.channel.send("Invalid time")

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
        await message.channel.send(calculateSum(messageWords[1:]))

    if messageWords[0] == "+multiply" or messageWords[0] == "+product":
        await message.channel.send(calculateProduct(messageWords[1:]))

    if messageWords[0] == "+mean" or messageWords[0] == "+average":
        await message.channel.send(calculateMean(messageWords[1:]))

    if message.content == "+hotlines":
        embedVar = discord.Embed(title="Canadian Hotlines", description="", color=0x000080)
        for index in range(int(len(hotlines) / 2)):
            embedVar.add_field(name=hotlines[index * 2], value=hotlines[index * 2 + 1], inline=False)

        await message.channel.send(embed=embedVar)

    if message.content.startswith("+dog"):
        currentURL = getDogURL(message)
        data = getTextData(currentURL)
        parse = (json.loads(data))
        URL = parse.get("message")
        await message.channel.send(URL)

    if message.content.startswith("+cat"):
        currentURL = getCatURL(message)
        if currentURL:
            data = getTextData(currentURL)
            data = data[1:-1]
            parse = (json.loads(data))
            URL = parse.get("url")
            await message.channel.send(URL)
        else:
            await message.channel.send("Invalid Cat Breed!")

    if message.content == "+quote":
        data = getTextData(QUOTES_URL)
        parse = json.loads(data)
        quote = random.choice(parse)
        embedVar = discord.Embed(title=quote.get('q'), description=quote.get('a'), color=0x000080)
        await message.channel.send(embed=embedVar)

    # Display commands
    if message.content.startswith("+help"):
        help_menu = ['**Here are all the commands this bot has to offer!**',
                     'Add a + sign (no spaces) in front of a command to use it.',
                     '',
                     '*hotlines*: Access a list of helplines',
                     '*timer*: Check your timers and add new ones',
                     '*schedule*: Check your schedule and add events',
                     '*mood*: Log your mood into the bot',
                     '*profile*: See your stats, such as Discord usage and average recent mood',
                     '*time*: See how long you spent on Discord today',
                     '*setLimit*: Set how much longer you want to stay on Discord this session',
                     '*quote*: See a motivational quote',
                     '*dog*: See a cute dog photo',
                     '*cat*: See a cute cat photo',
                     '*joke*: Read a joke',
                     '*smile*: Read some good news',
                     '*yum*: See a food picture',
                     '*memes*: See a meme']
        await message.channel.send('\n'.join(help_menu))

    # Post a joke from Reddit
    if message.content.startswith("+joke"):
        joke = reddit_post('https://oauth.reddit.com/r/Jokes/top')

        embed_var = discord.Embed(title=joke[0], description=joke[1], color=0x00ff00)

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post good news from Reddit
    if message.content.startswith("+smile"):
        good_news = reddit_post('https://oauth.reddit.com/r/MadeMeSmile/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post a food picture from Reddit
    if message.content.startswith("+yum"):
        good_news = reddit_post('https://oauth.reddit.com/r/Food/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)

    # Post a meme from Reddit
    if message.content.startswith("+memes"):
        good_news = reddit_post('https://oauth.reddit.com/r/dankmemes/top')

        embed_var = discord.Embed(title=good_news[0], description=good_news[1], color=0x00ff00,
                                  url=good_news[2])
        embed_var.set_image(url=good_news[2])

        channel = message.channel
        await message.channel.send(embed=embed_var)


def calculateSum(nums):
    totalSum = 0
    try:
        for num in nums:
            totalSum += float(num)
        return "The sum is " + str(totalSum)
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +add <num1> <num2> ..."


def calculateProduct(nums):
    totalProduct = 1
    try:
        for num in nums:
            totalProduct *= float(num)
        return "The product is " + str(totalProduct)
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +multiply <num1> <num2> ..."


def calculateMean(nums):
    totalAverage = 0
    try:
        for num in nums:
            totalAverage += float(num)
        return "The mean is " + str(totalAverage / len(nums))
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +mean <num1> <num2> ..."


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


# Return the URL to obtain the image of the dog
def getDogURL(message):
    if message.content == "+dog":
        url = RANDOM_DOG_URL
    else:
        breed = '/'.join(reversed(((message.content.lower()).split())[1:]))
        url = BREED_DOG_URL_1 + breed + BREED_DOG_URL_2

    return url


# Return the URL to obtain the image of the cat
def getCatURL(message):
    if message.content == "+cat":
        url = RANDOM_CAT_URL
    else:
        data = getTextData(BREED_CAT_URL)
        parse = (json.loads(data))
        target = (message.content.split()[1])
        target = target.capitalize()

        length = len(parse)
        targetIndex = " "

        for index in range(length):
            if parse[index].get("name") == target:
                targetIndex = index
        if targetIndex == " ":
            return False
        else:
            catID = parse[targetIndex].get("id")
            url = BREED_CAT_URL_2 + catID
    return url


# Return the text on a website given a URL
def getTextData(URL):
    request = requests.get(URL)
    html_content = BeautifulSoup(request.content, 'html.parser')
    return html_content.get_text()


client.run(TOKEN)
