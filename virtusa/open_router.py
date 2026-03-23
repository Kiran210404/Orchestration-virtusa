"""
OpenRouter API Test Module
This file is for testing purposes only.
Use environment variables for API keys in production.
"""
import os
from openai import OpenAI

# API key should come from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set in environment variables")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

# Example usage (uncomment to test):
# response = client.chat.completions.create(
#   model="openai/gpt-oss-120b:free",
#   messages=[
#     {
#       "role": "user",
#       "content": "Hello, how are you?"
#     }
#   ],
#   max_tokens=500
# )