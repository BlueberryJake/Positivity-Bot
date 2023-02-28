import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import art

class Art(Command.Command):
    def __init__(self, message) -> None:
        self.message = message

    async def run_command(self):
        ascii_text = ""
        ascii_text = art.randart()
        print(art.ART_NAMES)
        await self.message.channel.send(ascii_text)
