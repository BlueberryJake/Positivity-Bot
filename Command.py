from abc import ABC, abstractmethod


class Command(ABC):
    description = "No description found."
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run_command(self):
        pass

    def print_description(self):
        print(self.description)

class HelloWorld(Command):
    def run_command(self) -> None:
        print("Hello World!")




        