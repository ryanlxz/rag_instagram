import re
from ollama_mistral import MistralAgent

mistral_agent = MistralAgent("mistral")


class Extractor:
    def __init__(self) -> None:
        pass

    def extract_cuisine(self):
        pass

    def extract_price(self):
        pass

    def extract_taste(self, text: str):
        # no need llm
        pattern = r"Taste:\s*(.+)"
        taste = re.findall(pattern, text)
        return taste

    def extract_worth_it(self):
        pass

    def extract_location(self):
        pass


if __name__ == "__main__":
    pass
