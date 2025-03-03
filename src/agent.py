import ollama
from logs.logging import logger
from conf import conf
from .prompt import PromptLoader
from smolagents import CodeAgent, LiteLLMModel
from src.tools import filter_documents


class Agent:
    def __init__(self, model: str = conf["llm"]) -> None:
        try:
            ollama.show(model)
        except ollama._types.ResponseError:
            logger.info(f"pulling model {model} from ollama")
            ollama.pull(model)
        self.model = model
        self.agentic_model = CodeAgent(
            tools=[
                filter_documents,
            ],
            model=LiteLLMModel(model_id=f"ollama/{conf['llm']}"),
            add_base_tools=True,
            max_steps=20,
            verbosity_level=2,
        )
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

    def query_with_tool(self, prompt: str):
        response = self.agentic_model.run(prompt)
        return response


if __name__ == "__main__":
    agent = Agent()
    prompt = "where is hamburg keisuke in singapore?"
    response = agent.query(prompt)
    print(response)
