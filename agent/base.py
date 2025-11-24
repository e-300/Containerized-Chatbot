# LAYER 1 - ABSTRACT BASE CLASS
# base interface that will act as the AI platform
# AI client will be the implementation of the interface

from abc import ABC, abstractmethod


class AI_Platform(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass

    @abstractmethod
    def process(self, user_input: str) -> str:
        pass
