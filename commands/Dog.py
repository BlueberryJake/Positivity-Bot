import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import utility
import json

class Dog(Command.Command):
    RANDOM_DOG_URL = 'https://dog.ceo/api/breeds/image/random'
    BREED_DOG_URL_1 = 'https://dog.ceo/api/breed/'
    BREED_DOG_URL_2 = '/images/random'

    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        currentURL = self.getDogURL(self.message)
        data = utility.getTextData(currentURL)
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