import os
import requests
import json
from dotenv import load_dotenv
import re
import time
from typing import Generator, Tuple  # Add for type hinting
import streamlit as st

# Define the fallback trigger phrase
FALLBACK_TRIGGER_PHRASE = "Sorry, I couldn’t find an answer to our support database."

# Load API key and model from .env
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = st.secrets["OPENROUTER_MODEL"]

def query_llm(messages: list, max_retries: int = 3, retry_delay: int = 5, stream: bool = False) -> Tuple[bool, str | Generator[str, None, None]]:
    """
    Sends chat messages to the OpenRouter LLM with retry and optional streaming.

    Args:
        messages (list): Chat messages for the LLM.
        max_retries (int): Number of retry attempts for transient errors.
        retry_delay (int): Seconds to wait between retries.
        stream (bool): If True, return a generator for streaming response.

    Returns:
        - success (bool): True if success, False if rate-limited or failed.
        - response (str or Generator): Full response (non-streaming) or generator (streaming).
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "stream": stream
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30,
                stream=stream
            )

            if response.status_code == 200:
                if stream:
                    def stream_response():
                        for line in response.iter_lines():
                            if line:
                                decoded = line.decode("utf-8")
                                if decoded.startswith("data: "):
                                    chunk = decoded[6:]
                                    if chunk == "[DONE]":
                                        break
                                    try:
                                        chunk_data = json.loads(chunk)
                                        delta = chunk_data["choices"][0]["delta"].get("content", "")
                                        if delta:
                                            yield delta
                                    except json.JSONDecodeError:
                                        print(f"❌ Failed to parse stream chunk: {chunk}")
                    return True, stream_response()
                else:
                    message = response.json()["choices"][0]["message"]["content"].strip()
                    return True, message
            elif response.status_code == 429:
                print(f"⚠️ Rate limit hit (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, (
                    "⚠️ We're currently facing high demand. Please wait a moment and try again.\n"
                    "This is a temporary rate limit from the OpenRouter model provider."
                )
            elif response.status_code == 502:
                print(f"❌ 502 Bad Gateway error (attempt {attempt + 1}/{max_retries}):", response.text)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, "❌ Server error occurred. Please try again later."
            else:
                print(f"❌ OpenRouter API error (attempt {attempt + 1}/{max_retries}):", response.status_code, response.text)
                return False, "❌ Sorry, we couldn't process your request right now. Please try again later."
        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"❌ Connection/Timeout error (attempt {attempt + 1}/{max_retries}):", str(e))
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False, "❌ A technical error occurred. Please try again later."
        except Exception as e:
            print(f"❌ Unexpected error (attempt {attempt + 1}/{max_retries}):", str(e))
            return False, "❌ A technical error occurred. Please try again later."

def extract_fallback_info_with_history(chat_history: list, original_question: str = "") -> dict:
    """
    Extracts email and question from chat history using LLM, with regex fallback for email.

    Args:
        chat_history (list): Full conversation (role: user/assistant, content: message)
        original_question (str): The original question that triggered the fallback

    Returns:
        dict: {"email": "...", "question": "..."} or {} if extraction fails.
    """
    recent_history = chat_history[-4:] if len(chat_history) >= 4 else chat_history
    formatted_history = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_history)

    extraction_prompt = [
        {
            "role": "system",
            "content": (
                "You are an intelligent assistant helping customer support teams.\n"
                "Given the recent chat transcript, extract:\n"
                "1. Email address (must be valid, e.g., name@domain.com, no double dots or invalid characters)\n"
                "2. Full clarified question (resolve vague references like 'it', 'this phone' using context)\n\n"
                "Respond ONLY in this JSON format:\n"
                "{ \"email\": \"...\", \"question\": \"...\" }\n"
                "If either email or question is missing or unclear, leave it blank but return the JSON."
            )
        },
        {
            "role": "user",
            "content": formatted_history
        }
    ]

    # Use non-streaming for extraction to ensure complete JSON
    success, result = query_llm(extraction_prompt, stream=False)

    if success:
        try:
            cleaned_result = result.strip().strip('```json').strip('```').strip()
            parsed = json.loads(cleaned_result)
            email = parsed.get("email", "").strip()
            question = parsed.get("question", "").strip()
            if email and re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                return {"email": email, "question": question or original_question}
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM JSON output: {result} (Error: {str(e)})")

    # Fallback: Extract email using regex from the last user message
    last_user_message = next((msg["content"] for msg in reversed(recent_history) if msg["role"] == "user"), "")
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    email_match = re.search(email_pattern, last_user_message)
    email = email_match.group(0) if email_match else ""

    # Use original_question if available, otherwise fall back to history
    question = original_question
    if not question:
        for i in range(len(recent_history) - 1, -1, -1):
            if recent_history[i]["role"] == "user" and FALLBACK_TRIGGER_PHRASE.lower() not in recent_history[i]["content"].lower():
                question = recent_history[i]["content"]
                break

    if email or question:
        return {"email": email, "question": question}

    print("❌ LLM and regex failed to extract fallback info.")
    return {}

