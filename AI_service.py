import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class PentestAI:
    def __init__(self):
        # API key is pulled securely from .env
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, query):
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model=self.model,
        )
        return chat_completion.choices[0].message.content