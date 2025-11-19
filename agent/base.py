# This is the base interface that will act as the AI platform
# Next we will create an ai client that will be the implmentation of that interface


from abc import ABC, abstractmethod

class AI_Platform(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass

    @abstractmethod
    def process(self, user_input: str) -> str:
        pass