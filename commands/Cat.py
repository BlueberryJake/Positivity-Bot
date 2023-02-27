import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import utility
import json


class Cat(Command.Command):
    RANDOM_CAT_URL = 'https://api.thecatapi.com/v1/images/search'
    BREED_CAT_URL = "https://api.thecatapi.com/v1/breeds"
    BREED_CAT_URL_2 = 'https://api.thecatapi.com/v1/images/search?breed_ids='
    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        currentURL = self.getCatURL(self.message)
        if currentURL:
            data = utility.getTextData(currentURL)
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
            data = utility.getTextData(self.BREED_CAT_URL)
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