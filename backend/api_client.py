"""Groq API Client for AI Agency Portal"""
import httpx
import os
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", ""))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

async def ai(messages, api_key=None, model=None):
    """Make AI call using Groq"""
    key = api_key or os.getenv("GROQ_API_KEY", "")
    mdl = model or MODEL

    if not key:
        return "GROQ API key not set - go to Settings page"

    try:
        c = AsyncGroq(api_key=key)
        response = await c.chat.completions.create(
            model=mdl,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate" in error_str.lower():
            return f"[Groq rate limited. Try: llama-3.1-8b-instant or llama3-8b-8192]"
        elif "401" in error_str or "auth" in error_str.lower():
            return "Invalid Groq API key - check Settings"
        return f"[API Error: {error_str[:100]}]"