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

schedule = []
timers = []


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


@tasks.loop(seconds=1.0)
async def checkTimers():
    global outputChannel
    global timers
    newTimers = timers
    currentTime = datetime.now()
    for timer in timers:
        secondsDifference = currentTime.second - timer[0].second
        minutesDifference = currentTime.minute - timer[0].minute
        hoursDifference = currentTime.hour - timer[0].hour
        daysDifference = currentTime.day - timer[0].day

        totalSecondsDifference = secondsDifference + \
                                 60 * minutesDifference + \
                                 60 * 60 * hoursDifference + \
                                 60 * 60 * 24 * daysDifference

        if totalSecondsDifference >= timer[1]:
            await outputChannel.send(str(timer[2]) + ", your " +
                                     str(timer[1] // 60) + " minute timer has rung!")
            newTimers.remove(timer)
    timers = newTimers


@tasks.loop(seconds=1.0)
async def checkSchedule():
    global outputChannel
    global schedule
    newSchedule = schedule
    currentTime = datetime.now()
    for event in schedule:
        currentYear = currentTime.year
        currentMonth = currentTime.month
        currentDay = currentTime.day
        currentHour = currentTime.hour
        currentMinute = currentTime.minute
        currentSecond = currentTime.second

        if currentYear >= event[0] and currentMonth >= event[1] and currentDay >= event[2]\
           and currentHour >= event[3] and currentMinute >= event[4] and currentSecond >= event[5]:
            await outputChannel.send(str(event[6]) + ", one of your events is happening now!")
            newSchedule.remove(event)
    schedule = newSchedule


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
    checkTimers.start()
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
        embedVar = discord.Embed(title=message.author.name, description="Here are following relavent stats",
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
        if message.content == "+timer" or message.content == "+timer check":
            currentTime = datetime.now()
            outputString = "Your Timers:"
            for timer in timers:
                if timer[2] == "<@" + str(message.author.id) + ">":
                    secondsDifference = timer[0].second - currentTime.second
                    minutesDifference = timer[0].minute - currentTime.minute
                    hoursDifference = timer[0].hour - currentTime.hour
                    daysDifference = timer[0].day - currentTime.day

                    totalSecondsDifference = secondsDifference + \
                                             60 * minutesDifference + \
                                             60 * 60 * hoursDifference + \
                                             60 * 60 * 24 * daysDifference
                    totalSecondsDifference += timer[1]

                    daysDifference = totalSecondsDifference // (60 * 60 * 24)
                    totalSecondsDifference -= daysDifference * (60 * 60 * 24)
                    hoursDifference = totalSecondsDifference // (60 * 60)
                    totalSecondsDifference -= hoursDifference * (60 * 60)
                    minutesDifference = totalSecondsDifference // 60
                    totalSecondsDifference -= minutesDifference * 60
                    secondsDifference = totalSecondsDifference

                    outputString = outputString + "\n" + \
                                   str(daysDifference) + " days, " + \
                                   str(hoursDifference) + " hours, " + \
                                   str(minutesDifference) + " minutes, " + \
                                   str(secondsDifference) + " seconds."

                else:
                    continue
            await message.channel.send(outputString + "\nEnd of list")

        elif len(messageWords) >= 1:
            try:
                numMinutes = round(float(messageWords[1]))
                if numMinutes <= 0:
                    await message.channel.send(
                        "Error: Number greater than 0\nSyntax: $timer <Number of Minutes (integer > 0)>")
                else:
                    timers.append([datetime.now(), numMinutes * 60, "<@" + str(message.author.id) + ">"])
                    await message.channel.send(str(numMinutes) + " minute timer has begun!")
            except ValueError:
                await message.channel.send("Error: Not a number\nSyntax: + timer <Number of Minutes (integer > 0)>")

    if message.content.startswith("+schedule"):
        if message.content == "+schedule" or message.content == "+schedule check":
            outputString = "Your Events:"
            for event in schedule:
                if event[6] == "<@" + str(message.author.id) + ">":
                    outputString = outputString + \
                                   "\nYear: " + str(event[0]) + \
                                   ", Month: " + str(event[1]) + \
                                   ", Day: " + str(event[2]) + \
                                   ", Hour: " + str(event[3]) + \
                                   ", Minute: " + str(event[4]) + \
                                   ", Second: " + str(event[5])
                else:
                    continue
            await message.channel.send(outputString + "\nEnd of list")
        elif messageWords[1] == "add":
            if len(messageWords) == 8:
                try:
                    year = round(float(messageWords[2]))
                    month = round(float(messageWords[3]))
                    day = round(float(messageWords[4]))
                    hour = round(float(messageWords[5]))
                    minute = round(float(messageWords[6]))
                    second = round(float(messageWords[7]))

                    if year >= datetime.now().year and month > 0 and day > 0 and hour >= 0 and minute >= 0 and second >= 0:
                        schedule.append([year, month, day, hour, minute, second, "<@" + str(message.author.id) + ">"])
                        await message.channel.send("Event added to your schedule!")

                except ValueError:
                    await message.channel.send("Error: Invalid Syntax\n" +
                                               "Syntax: +schedule add\n" +
                                               "<Year> <Month> <Day> <Hour> <Minute> <Second>")

    if message.content.startswith("+add"):
        totalSum = 0
        try:
            for num in messageWords[1:]:
                totalSum += float(num)
            await message.channel.send("The sum is " + str(totalSum))
        except ValueError:
            await message.channel.send("Error: Invalid Syntax\n" +
                                       "Syntax: +add <num1> <num2> ...")

    if message.content.startswith("+multiply"):
        totalProduct = 1
        try:
            for num in messageWords[1:]:
                totalProduct *= float(num)
            await message.channel.send("The product is " + str(totalProduct))
        except ValueError:
            await message.channel.send("Error: Invalid Syntax\n" +
                                       "Syntax: +multiply <num1> <num2> ...")


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
