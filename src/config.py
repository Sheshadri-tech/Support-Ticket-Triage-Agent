import os

from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not found in the .env file."
    )


# AI model configuration
GROQ_MODEL = "llama-3.3-70b-versatile"


# AI generation configuration
AI_TEMPERATURE = 0.1