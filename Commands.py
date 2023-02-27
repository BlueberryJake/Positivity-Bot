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




