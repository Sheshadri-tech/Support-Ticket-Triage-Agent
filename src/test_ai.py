import os
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env
load_dotenv()

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not found in the .env file.")

# Create Groq client
client = Groq(api_key=api_key)

# Send a simple test request
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": (
                "Say hello and confirm that the "
                "Support Ticket Triage Agent AI connection is working."
            )
        }
    ],
)

print("\nAI RESPONSE:")
print(response.choices[0].message.content)