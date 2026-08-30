from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

print("1. Script started")

load_dotenv()

print("2. Groq key loaded:", bool(os.getenv("GROQ_API_KEY")))

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

print("3. Sending request to Groq...")

response = llm.invoke("Say hello in one sentence.")

print("4. Response received:")
print(response.content)