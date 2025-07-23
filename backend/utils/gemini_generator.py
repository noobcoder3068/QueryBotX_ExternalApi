# utils/gemini_generator.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_GEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def generate_answer(prompt: str) -> str:
    res = requests.post(
        f"{GEMINI_GEN_URL}?key={API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
    )
    res.raise_for_status()
    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
