from embed_query import embed_user_query
from similarity import get_top_chunks
from prompt_builder import build_prompt
from llm_interface import query_llm, extract_fallback_info_with_history
import warnings
import json
from datetime import datetime
import os
import re
from typing import Generator, Tuple  # Add for type hinting

warnings.filterwarnings("ignore", category=FutureWarning)

# Track whether we are waiting for email after a fallback
waiting_for_fallback_info = False
fallback_trigger_phrase = "Sorry, I couldn’t find an answer to that in our support database."
original_question = ""

# Holds latest chat history globally in CLI mode
chat_history = []

def get_chatbot_response(question: str, history: list) -> Tuple[str, list, bool]:
    """
    Orchestrates the chatbot pipeline: embedding → retrieval → prompt → LLM call.

    Args:
        question (str): User's latest question.
        history (list): List of past messages (role/user/assistant).

    Returns:
        tuple:
            - response (str): Final answer from the chatbot.
            - updated_history (list): Chat history including latest exchange.
            - is_fallback (bool): True if fallback triggered, False otherwise.
    """
    global waiting_for_fallback_info, original_question

    # If waiting for email, skip embedding and retrieval
    if waiting_for_fallback_info:
        extracted = extract_fallback_info_with_history(history + [{"role": "user", "content": question}], original_question)
        if extracted.get("email") and extracted.get("question"):
            try:
                save_unanswered_question(extracted)
                response = (
                    f"✅ Thank you! We've noted your question about: \"{extracted['question']}\" "
                    f"and will contact you at {extracted['email']} shortly."
                )
                waiting_for_fallback_info = False
                original_question = ""
            except Exception as e:
                print(f"❌ Failed to save unanswered question: {str(e)}")
                response = (
                    "⚠️ Sorry, we couldn’t save your question due to a technical issue. "
                    "Please try again or contact support directly."
                )
        else:
            response = (
                "⚠️ Sorry, we couldn't extract a valid email or question. "
                "Please provide your email address (e.g., user@example.com) and confirm your question."
            )

        updated_history = history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": response}
        ]
        return response, updated_history, False

    # Step 1: Embed user query
    query_embedding = embed_user_query(question)

    # Step 2: Retrieve top 3 relevant chunks
    top_chunks = get_top_chunks(query_embedding, top_k=3)

    # Step 3: Build LLM prompt
    messages = build_prompt(question, top_chunks, history)

    # Step 4: Get response from OpenRouter (streaming)
    success, result = query_llm(messages, stream=True)

    if not success:
        print("⚠️ Query failed. Returning error message without updating history.")
        return result, history, False

    # Step 5: Collect streaming response for history and fallback detection
    response = ""
    for chunk in result:
        response += chunk

    # Step 6: Update conversation history
    updated_history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": response}
    ]

    # Step 7: Check for fallback trigger with flexible pattern
    fallback_pattern = r"(sorry|i couldn’t find|no answer|not found).*?(support database|our database)"
    is_fallback = bool(re.search(fallback_pattern, response.lower())) or fallback_trigger_phrase.lower() in response.lower()
    if is_fallback:
        waiting_for_fallback_info = True
        original_question = question

    return response, updated_history, is_fallback

def save_unanswered_question(entry: dict):
    entry["timestamp"] = datetime.utcnow().isoformat()
    file_path = "Source Code/Assets/unanswered_queries.jsonl"
    
    # # Ensure Assets folder exists
    # os.makedirs("Assets", exist_ok=True)
    
    print("📝 Saving fallback query:", entry)
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"❌ Error saving to {file_path}: {str(e)}")
        raise

