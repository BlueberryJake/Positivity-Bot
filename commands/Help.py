import sys
import os

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Command

class Help(Command.Command):
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