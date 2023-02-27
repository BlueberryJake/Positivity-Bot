import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command
import discord

class Hotlines(Command.Command):
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

