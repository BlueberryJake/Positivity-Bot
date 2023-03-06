import sys
import os
from discord.ext import tasks

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Loop

class CheckTimers(Loop.Loop):

    def __init__(self, user_profile_list, channel) -> None:
        self.user_profile_list = user_profile_list
        self.channel = channel
    
    @tasks.loop(seconds=1.0)
    async def run_loop(self):
        for userProfile in self.user_profile_list.user_profile_list:
            userProfile.timer_list.tick_all()
            for index in range(len(userProfile.timer_list.rings)):
                if userProfile.timer_list.rings[index]:
                    userProfile.timer_list.rings[index] = False
                    await self.channel.send("<@" + str(userProfile.user_info.rawUser.id) + ">")

