import os
from dotenv import load_dotenv
load_dotenv()

# Check if API key is loaded
key = os.getenv("OPENAI_API_KEY")
print(f"API key found: {bool(key)}")
if key:
    print(f"Key starts with: {key[:8]}...")

# Try the OpenAI client
from openai import OpenAI
try:
    client = OpenAI()
    print("OpenAI client created successfully")
except Exception as e:
    print(f"Client creation failed: {e}")