from collections import UserList
import os
import time
import discord

from datetime import datetime
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

schedule = []
timers = []


@tasks.loop(seconds=1.0)
async def newLoop():
    global timeOnDiscord
    for guild in client.guilds:
        for member in guild.members:
            if member.status == discord.Status.online or member.status == discord.Status.dnd:
                try:
                    timeOnDiscord[1][timeOnDiscord[0].index(member)] += 5
                except:
                    return
                    print("Member not found")
            if member.status == discord.Status.offline or member.status == discord.Status.invisible:
                try:
                    timeOnDiscord[1][timeOnDiscord[0].index(member)] = 0
                except:
                    return
                    print("Member not found")


@tasks.loop(seconds=1.0)
async def checkOvertime():
    global timeOnDiscord, outputChannel
    # print(timeOnDiscord)
    for guild in client.guilds:
        for member in guild.members:
            index = timeOnDiscord[0].index(member)
            if timeOnDiscord[1][index] == timeOnDiscord[2][index] and timeOnDiscord[2][index] != -1:
                # timeOnDiscord[2][index] += 20
                outputString = "Get out <@" + str(member.id) + "> !"
                await outputChannel.send(outputString)


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
            await outputChannel.send(str(timer[2]) + ", your " + str(timer[1] // 60) + " minute timer has rung!")
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
    timeOnDiscord = [userList, userTime, userSetTime]
    newLoop.start()
    checkOvertime.start()
    checkTimers.start()
    checkSchedule.start()


@client.event
async def on_message(message):
    global n, lastCall

    global schedule
    global timers
    messageWords = message.content.split()

    if message.author == client.user:
        return

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
                    outputString = outputString +\
                                   "\nYear: " + str(event[0]) +\
                                   ", Month: " + str(event[1]) +\
                                   ", Day: " + str(event[2]) +\
                                   ", Hour: " + str(event[3]) +\
                                   ", Minute: " + str(event[4]) +\
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
                                               "Syntax: + schedule add\n" +
                                               "<Year> <Month> <Day> <Hour> <Minute> <Second>")


    if message.content.startswith('c'):  # c

        if time.time() - lastCall < 3:
            await message.channel.send("Wait 3 sec")

        else:
            await message.channel.send(n)
            n = n + 1
            lastCall = time.time()

    if message.content == "e":  # e
        embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
        embedVar.add_field(name="Field1", value="hi", inline=False)
        embedVar.add_field(name="Field2", value="hi2", inline=False)
        await message.channel.send(embed=embedVar)

    if message.content == "+profile":  # profile
        outputString = "You were on discord for " + str(
            timeOnDiscord[1][timeOnDiscord[0].index(message.author)]) + " seconds"
        embedVar = discord.Embed(title=message.author.name, description="Here are following relavent stats",
                                 color=0x00ff00)
        embedVar.add_field(name="Time on discord", value=outputString, inline=False)
        embedVar.add_field(name="Field2", value="hi2", inline=False)
        await message.channel.send(embed=embedVar)

    if message.content == "mem":  # member ids
        for guild in client.guilds:
            for member in guild.members:
                await message.channel.send(member.id)

    if message.content == "+time":  # Time on Discord
        # print(message.author.id)
        outputString = "You were on discord for " + str(
            timeOnDiscord[1][timeOnDiscord[0].index(message.author)]) + " seconds"
        await message.channel.send(outputString)

    if message.content.startswith("+setTimer"):
        content = message.content.split()
        # print(content)
        try:
            timeAmount = int(content[2])
            # print(timeAmount)

            if timeAmount <= 0:
                raise ValueError

            try:
                timeOnDiscord[2][timeOnDiscord[0].index(message.author)] = timeAmount

            except:
                return
                print("Member not found")

        except:
            await message.channel.send("Invalid time")


client.run(TOKEN)
