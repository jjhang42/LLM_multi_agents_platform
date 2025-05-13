# core/agent_tools/client.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_gemini_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
