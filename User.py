import sys
import os
sys.path.append(os.path.join( os.path.dirname( __file__ ), 'objects' ))
import Timer


class UserInfo:
    def __init__(self, u) -> None:
        self.rawUser = u
    
    def __str__(self) -> str:
        return f"{self.rawUser.name}#{self.rawUser.discriminator} \n"

class UserProfile:
    def __init__(self, user_info: UserInfo) -> None:
        self.user_info = user_info

        self.seconds_online = 0
        self.total_seconds_online = 0
        self.time_limit = -1

        self.previous_reactions = []
        self.average_reaction = None

        self.timer_list = Timer.TimerList(4)
    
    def __str__(self) -> str:
        return self.user_info.__str__()
    
    def add_time(self, seconds) -> None:
        self.seconds_online += seconds
        self.total_seconds_online += seconds
    
    def reset_time(self) -> None:
        self.seconds_online = 0


class UserProfileList:
    def __init__(self) -> None:
        self.user_profile_list = []
    
    def load_user(self, u) -> None:
        self.user_profile_list.append(UserProfile(UserInfo(u)))
    
    def get_user_profile(self, index) -> UserProfile:
        return self.user_profile_list[index] 
    
    def get_user_info(self, index) -> UserInfo:
        return self.user_profile_list[index].user_info
    
    def get_raw_user(self, index):
        return self.get_user_info(index).rawUser
    
    def get_user_index(self, rawUser) -> int:
        for i in range (len(self.user_profile_list)):
            if self.get_raw_user(i) == rawUser:
                return i
        return -1

    
    def __str__(self) -> str:
        text = ""
        for i in range(len(self.user_profile_list)):
            text += self.user_profile_list[i].__str__()
        return text 