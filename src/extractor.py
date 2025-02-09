import re
from .agent import Agent
from typing import Union
from logs.logging import logger
from .prompt import PromptLoader


class Extractor:
    """extracts relevant metadata info such as cuisine, price, taste, worth-it, location."""

    def __init__(self, text: str) -> None:
        self.prompts = PromptLoader()
        self.cuisine_prompt = self.prompts.extract_cuisine
        self.price_prompt = self.prompts.extract_price
        self.text = text
        self.agent = Agent()

    def extract_cuisine(self):
        query = self.cuisine_prompt.format(food_review=self.text)
        cuisine = self.agent.extract_fields(query)
        return cuisine

    def extract_price(self):
        pattern = r"Price:\s*(.+)"
        price = re.findall(pattern, self.text)
        if price:
            print(price[0])
            query = self.price_prompt.format(price_list=price[0])
            price_output = self.agent.extract_fields(query)
            print(price_output)
            return price_output
        else:
            logger.error(f"No price rating found in {self.text}")
            return price

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
            logger.error(f"No taste rating found in {self.text}")
            return taste

    def extract_worth_it(self):
        pattern = r"Worth-it:\s*(.+)"
        worth_it = re.findall(pattern, self.text)
        if worth_it:
            return worth_it[0]
        else:
            logger.error(f"No worth-it rating found in {self.text}")
            return worth_it

    def extract_location(self):
        pattern = r"Location:\s*(.+)"
        location = re.findall(pattern, self.text)
        if location:
            return location[0]
        else:
            logger.error(f"No location found in {self.text}")
            return location
