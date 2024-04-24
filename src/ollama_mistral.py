import ollama
from logs.logging import logger
from conf import conf


class MistralAgent:
    def __init__(self, model: str = conf["llm"]) -> None:
        self.model = model
        # ollama.pull(model)
        pass

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
    mistral_agent = MistralAgent("mistral")
    prompt = "where is hamburg keisuke in singapore?"
    response = mistral_agent.query(prompt)
    print(response)
