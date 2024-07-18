import ollama
from logs.logging import logger
from conf import conf


class Agent:
    def __init__(self, model: str = conf["llm"]) -> None:
        try:
            ollama.show(model)
        except ollama._types.ResponseError:
            logger.info(f"pulling model {model} from ollama")
            ollama.pull(model)
        self.model = model

    def query(self, prompt: str):
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


if __name__ == "__main__":
    agent = Agent("llama3")
    prompt = "where is hamburg keisuke in singapore?"
    response = agent.query(prompt)
    print(response)
