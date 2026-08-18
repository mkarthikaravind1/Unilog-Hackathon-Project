"""
LLM provider abstraction. Switch between Groq and Gemini by
setting LLM_PROVIDER in your .env file.

Usage:
    from pipeline.llm_client import call_llm
    response = call_llm(system="You are...", user="Extract...")
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()


def call_llm(
    system: str,
    user: str,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> str:
    """
    Calls the configured LLM provider (groq or gemini).
    Returns the response as a plain string.
    temperature=0.1 keeps outputs deterministic for structured extraction.
    """
    if PROVIDER == "groq":
        return _call_via_groq(system, user, temperature, max_tokens)
    elif PROVIDER == "gemini":
        return _call_via_gemini(system, user, temperature, max_tokens)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{PROVIDER}'. "
            "Set LLM_PROVIDER=groq or LLM_PROVIDER=gemini in your .env"
        )


def _call_via_groq(
    system: str, user: str, temperature: float, max_tokens: int
) -> str :
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Run: pip install groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content

    if content is None:
        raise ValueError("Groq returned an empty response")

    return content.strip()


def _call_via_gemini(
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
) -> str:
    try:
        import importlib

        genai = importlib.import_module("google.generativeai")
    except ImportError:
        raise ImportError("Run: pip install google-generativeai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )

    response = model.generate_content(user)

    text = response.text

    if text is None:
        raise ValueError("Gemini returned an empty response")

    return str(text).strip()


if __name__ == "__main__":
    result = call_llm(
        system="You are a helpful assistant.",
        user="Say hello in one sentence.",
    )
    print(f"Provider : {PROVIDER}")
    print(f"Response : {result}")