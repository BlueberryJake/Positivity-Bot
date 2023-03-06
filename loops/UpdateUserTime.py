import sys
import os
import discord
from discord.ext import tasks

#Add the folder one level up to the path
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
import Loop

class UpdateUserTime(Loop.Loop):
    period_seconds = 5

    def __init__(self, user_profile_list, channel) -> None:
        self.user_profile_list = user_profile_list
        self.channel = channel
    
    @tasks.loop(seconds=period_seconds)
    async def run_loop(self):
        for user_index in range (len(self.user_profile_list.user_profile_list)):
            userProfile = self.user_profile_list.get_user_profile(user_index)
            user = userProfile.user_info.rawUser

            if user.status == discord.Status.online or user.status == discord.Status.dnd:
                userProfile.add_time(5)
            
            if user.status == discord.Status.offline or user.status == discord.Status.invisible:
                userProfile.reset_time()
            
            if userProfile.seconds_online == userProfile.time_limit:
                outputString = "Get out <@" + str(user.id) + "> !"
                await self.channel.send(outputString)
            
            # print(user, userProfile.seconds_online)

