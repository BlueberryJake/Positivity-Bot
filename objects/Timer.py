
class Timer:
    def __init__(self, seconds=0, minutes=0):

        self.seconds = seconds
        self.paused = False
        self.finished = False

        if self.seconds < 0:
            self.finished = True
    
    def tick(self):
        if not self.paused and not self.finished:
            self.seconds -= 1
        if self.seconds == 0:
            self.finished = True
            self.seconds = -1
            return True
        
        return False
        
    def set(self, seconds):
        self.seconds = seconds
        self.finished = False
    
    def reset(self):
        self.seconds = -1
        self.finished = True
    
    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.paused = False
    
    def __str__(self):
        return self.seconds

class TimerList:
    def __init__(self, size) -> None:
        self.timer_list = []
        self.rings = []
        for i in range(size):
            self.timer_list.append(Timer(-1))
            self.rings.append(False)

    
    def add_new_timer(self, seconds):
        for timer in self.timer_list:
            if timer.finished:
                timer.set(seconds)
                return 0
        print("No room for new timers")
    
    def reset_timer(self, index):
        self.timer_list[index].reset()
    
    def pause_timer(self, index):
        self.timer_list[index].pause()
    
    def unpause_timer(self, index):
        self.timer_list[index].unpause()
    
    def tick_all(self):
        for index in range(len(self.timer_list)):
            timer = self.timer_list[index]
            if timer.tick():
                self.rings[index] = True
    
    def __str__(self)->str:
        string = ""
        for index in range(len(self.timer_list)):
            string += f"ID: {index} {self.timer_list[index].__str__()} \n"
        return string 

    