import ollama
from logs.logging import logger
from conf import conf
from .prompt import PromptLoader


class Agent:
    def __init__(self, model: str = conf["llm"]) -> None:
        try:
            ollama.show(model)
        except ollama._types.ResponseError:
            logger.info(f"pulling model {model} from ollama")
            ollama.pull(model)
        self.model = model
        self.prompts = PromptLoader()
        self.system_prompt = self.prompts.system_prompt

    def extract_fields(self, prompt: str) -> str:
        """extracts fields such as price and cuisine.

        Args:
            prompt (str): instagram post

        Returns:
            str: llm response
        """
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response["message"]["content"]

    def query(self, prompt: str) -> str:
        """responds to a user's query. Contains a system prompt to help guide the llm response

        Args:
            prompt (str): user query

        Returns:
            str: llm response
        """
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response["message"]["content"]


if __name__ == "__main__":
    agent = Agent("llama3")
    prompt = "where is hamburg keisuke in singapore?"
    response = agent.query(prompt)
    print(response)
