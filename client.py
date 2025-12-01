from openai import OpenAI
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Read API key from environment variable (no real key in code)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in your environment / .env file")

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-4.1-mini",  # example model
    input="Write a haiku about AI.",
    store=True
)

print(response.output_text)
