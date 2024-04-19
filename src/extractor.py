import re
from .ollama_mistral import MistralAgent
from typing import Union
from logs.logging import logger

mistral_agent = MistralAgent("mistral")


class Extractor:
    def __init__(self, text: str) -> None:
        self.text = text

    def extract_cuisine(self):
        return "japanese"

    def extract_price(self):
        pass

    def extract_taste(self) -> Union[str, None]:
        """extracts taste rating from post. As taste is used to check if a review spans across more than 1 post,
        it is possible for a post to have no taste rating before merging with the subsequent post(s).
        Only the last post of a review will contain all the ratings.

        Returns:
            Union[str,None]: taste rating or None
        """
        pattern = r"Taste:\s*(.+)"
        taste = re.findall(pattern, self.text)
        if taste:
            return taste[0]
        else:
            return taste

    def extract_worth_it(self):
        pattern = r"Worth-it:\s*(.+)"
        worth_it = re.findall(pattern, self.text)
        return worth_it[0]

    def extract_location(self):
        pattern = r"Location:\s*(.+)"
        location = re.findall(pattern, self.text)
        return location[0]
