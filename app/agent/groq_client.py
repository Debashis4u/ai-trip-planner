# app/agent/groq_client.py

import os
from groq import Groq

def get_model_name():
    """Get the model name from environment, with fallback."""
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def get_groq_client():
    """Get a configured Groq client instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Set it in .env before starting the app.")
    
    return Groq(api_key=api_key)

def create_chat_completion(client, messages, temperature=0.7, max_tokens=200, **kwargs):
    """Generic function to create chat completions with model selection and fallback."""
    model_name = get_model_name()
    fallback_model = os.getenv("GROQ_MODEL_FALLBACK", "llama-3.3-70b-versatile")
    
    try:
        return client.chat.completions.create(
            messages=messages,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    except Exception as e:
        error_msg = str(e).lower()
        if ("model_not_found" in error_msg or "invalid_request_error" in error_msg) and fallback_model and fallback_model != model_name:
            print(f"⚠️ Model '{model_name}' not available, trying fallback '{fallback_model}'")
            return client.chat.completions.create(
                messages=messages,
                model=fallback_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        raise
