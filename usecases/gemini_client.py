import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from typing import List, Dict

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'credentials.env'))

def get_client() -> genai.Client:
    """Returns a configured Gemini Client instance using GEMINI_API_KEY."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY environment variable not set or found in config/credentials.env.", file=sys.stderr)
        raise ValueError("Missing GEMINI_API_KEY")

    return genai.Client(api_key=api_key)

def send_prompt(prompt: str, context: List[Dict[str, str]] = None) -> str:
    """
    Sends a prompt to Gemini 2.5 Flash with optional context.

    Args:
        prompt: The user prompt to send.
        context: Optional conversation history as list of dicts with 'role' and 'parts'.

    Returns:
        The response string from Gemini.
    """
    try:
        client = get_client()

        contents = []
        if context:
            for msg in context:
                # Format to match genai schema
                contents.append(
                    {"role": msg["role"], "parts": [{"text": msg["parts"]}]}
                )

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return response.text
    except errors.APIError as e:
        print(f"[Error] Gemini API Error: {e}", file=sys.stderr)
        raise
    except ValueError as e:
        print(f"[Error] Configuration Error: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"[Error] Unexpected error when calling Gemini: {e}", file=sys.stderr)
        raise
