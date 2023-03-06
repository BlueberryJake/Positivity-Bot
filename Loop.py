from abc import ABC, abstractmethod


class Loop(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def run_loop(self):
        pass



    