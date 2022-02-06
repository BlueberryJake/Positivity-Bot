# bot.py
import os

import discord
from dotenv import load_dotenv
import random
import json

import requests
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

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
