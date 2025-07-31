def build_prompt(question: str, top_chunks: list, history: list = None) -> list:
    """
    Builds a list of messages (chat format) for the LLM to enable conversation memory.

    Args:
        question (str): The user's latest question.
        top_chunks (list): Top relevant content chunks.
        history (list): Previous chat history as list of dicts with 'role' and 'content'.

    Returns:
        list: Chat messages formatted for LLM (OpenRouter-style).
    """

    # Combine chunks into a single structured context string
    context_parts = []
    for i, chunk in enumerate(top_chunks, 1):
        section = chunk.get("section", chunk.get("category", ""))
        chunk_type = chunk.get("type", "")
        label = f"{chunk_type.capitalize()} - {section}" if section else chunk_type.capitalize()
        context_parts.append(f"---\n[{label}]\n{chunk['content']}")
    
    context = "\n".join(context_parts)

    # Prompt with behavior instructions
    messages = [
        {
        "role": "system",
        "content": (
            "You are a smart, professional, and friendly customer support assistant for **Quantum Arc**, a premium tech retailer specializing in smartphones, laptops, desktops, and accessories.\n\n"
            "Your role is to assist users by answering questions **strictly using the provided support context below**.\n\n"
            "⚠️ Important instructions:\n"
            "- Answer ONLY using the context provided. Do NOT rely on prior knowledge, training data, or external information.\n"
            "- Be short, clear, and human-like — just like a real customer service representative.\n"
            "- Never guess, invent, or expand on answers beyond the given Support Context.\n"
            "- If the user says something vague like 'its battery' or 'this product', infer what they're referring to by checking chat history.\n"
            "- If the user greets or thanks you casually, respond politely and warmly.\n\n"
            "🚫 If the answer is NOT found in the support context, reply **exactly like this**:\n"
            "\"Sorry, I couldn’t find an answer to that in our support database. Could you please share your email address and your question? We’ll get back to you soon.\"\n\n"
            "Do NOT include disclaimers, general advice, or make up details. You are ONLY allowed to use the provided support data."
        )
        },
        {
            "role": "system",
            "content": f"Support Context:\n{context}"
        }
    ]

    # Include prior chat history if available
    if history:
        messages.extend(history)

    # Add the current user question
    messages.append({"role": "user", "content": question})

    return messages
