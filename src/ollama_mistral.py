import ollama
from logs.logging import logger


class MistralAgent:
    def __init__(self, model: str) -> None:
        # ollama.pull(model)
        pass

    def query(self, prompt: str):
        response = ollama.chat(
            model="mistral",
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
