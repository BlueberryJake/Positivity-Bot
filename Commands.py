import discord
import random
from Command import Command
from utility import getTextData
import json


#An example for writing a subclass of Command: 
class Template(Command):
    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        pass

class Hotlines(Command):
    description = '*hotlines*: Access a list of helplines'
    hotlines = ['Canada Drug Rehab Addiction Services Directory', '1-866-462-6362',
            'Centre for Suicide Prevention', '1-833-456-4566',
            'Crisis Services Canada', '1-833-456-4566, or text 45645',
            'First Nations and Inuit Hope for Wellness Help Line', '1‑855‑242-3310',
            'Kids Help Phone', '1-800-668-6868',
            'National Eating Disorder Information Centre', '1-866-633-4220',
            'Native Youth Crisis Hotline', '1-877-209-1266']
    
    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        embedVar = discord.Embed(title="Canadian Hotlines", description="", color=0x000080)
        for index in range(int(len(self.hotlines) / 2)):
            embedVar.add_field(name=self.hotlines[index * 2], value=self.hotlines[index * 2 + 1], inline=False)

        await self.message.channel.send(embed=embedVar)


class Help(Command):
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
    def __init__(self, message) -> None:
        self.message = message
    
    async def run_command(self):
        await self.message.channel.send('\n'.join(self.help_menu))

class Dog(Command):
    RANDOM_DOG_URL = 'https://dog.ceo/api/breeds/image/random'
    BREED_DOG_URL_1 = 'https://dog.ceo/api/breed/'
    BREED_DOG_URL_2 = '/images/random'

    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        currentURL = self.getDogURL(self.message)
        data = getTextData(currentURL)
        parse = (json.loads(data))
        URL = parse.get("message")
        await self.message.channel.send(URL)

    def getDogURL(self, message):
        if message.content == "+dog":
            url = self.RANDOM_DOG_URL
        else:
            breed = '/'.join(reversed(((message.content.lower()).split())[1:]))
            url = self.BREED_DOG_URL_1 + breed + self.BREED_DOG_URL_2
        return url

class Cat(Command):
    RANDOM_CAT_URL = 'https://api.thecatapi.com/v1/images/search'
    BREED_CAT_URL = "https://api.thecatapi.com/v1/breeds"
    BREED_CAT_URL_2 = 'https://api.thecatapi.com/v1/images/search?breed_ids='
    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        currentURL = self.getCatURL(self.message)
        if currentURL:
            data = getTextData(currentURL)
            data = data[1:-1]
            parse = (json.loads(data))
            URL = parse.get("url")
            await self.message.channel.send(URL)
        else:
            await self.message.channel.send("Invalid Cat Breed!")

    def getCatURL(self, message):
        if message.content == "+cat":
            url = self.RANDOM_CAT_URL
        else:
            data = getTextData(self.BREED_CAT_URL)
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
                url = self.BREED_CAT_URL_2 + catID
        return url

class Quote(Command):
    QUOTES_URL = 'https://zenquotes.io/api/quotes/[key]?option1=value&option2=value'

    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        data = getTextData(self.QUOTES_URL)
        parse = json.loads(data)
        quote = random.choice(parse)
        embedVar = discord.Embed(title=quote.get('q'), description=quote.get('a'), color=0x000080)
        await self.message.channel.send(embed=embedVar)