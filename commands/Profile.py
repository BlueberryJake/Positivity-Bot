import sys
import os
import discord

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command

class Profile(Command.Command):
    def __init__(self, message, user_profile) -> None:
        self.message = message
        self.user_profile = user_profile

    async def run_command(self):
        outputString = "You were on discord for " + str(self.user_profile.seconds_online) + " seconds"
        embedVar = discord.Embed(title=self.message.author.name, description="Here are following relevant stats",
                                 color=0x00ff00)
        embedVar.add_field(name="Total time on discord today", value=outputString, inline=False)
        embedVar.add_field(name="Recent average mood",
                           value=str(self.user_profile.average_reaction), inline=False)
        await self.message.channel.send(embed=embedVar)
