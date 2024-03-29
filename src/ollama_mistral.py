import ollama


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
        print(response["message"]["content"])


if __name__ == "__main__":
    mistral_agent = MistralAgent("mistral")
    prompt = "where is hamburg keisuke in singapore?"
    mistral_agent.query(prompt)
