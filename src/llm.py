import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file from project root if present
load_dotenv()

# Prefer OPENAI_API_KEY, fall back to github_token for backwards compatibility
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("github_token")
API_BASE = os.getenv("OPENAI_API_BASE", "https://models.github.ai/inference")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def _get_client():
    if not API_KEY:
        raise RuntimeError(
            "OpenAI API key not found. Set OPENAI_API_KEY or github_token environment variable."
        )
    kwargs = {"api_key": API_KEY}
    if API_BASE:
        kwargs["base_url"] = API_BASE
    return OpenAI(**kwargs)


def translate_text(text: str, source_lang: str = "English", target_lang: str = "Chinese") -> str:
    """Translate text from source_lang to target_lang using the LLM.

    Returns the translated string.
    """
    if not text:
        return ""

    # Use shared client configuration
    token = os.getenv("github_token")
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1-mini"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    system_prompt = (
        f"You are a precise translation assistant. Translate the user's text from {source_lang} to {target_lang}. "
        "Preserve meaning and formatting. Do not add commentary — return only the translation."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        top_p=1,
        max_tokens=2000,
    )

    try:
        return resp.choices[0].message.content.strip()
    except Exception:
        # If response format unexpected, raise for caller to handle/log
        raise RuntimeError(f"Unexpected LLM response format: {resp}")


if __name__ == "__main__":
    sample = "What is the capital of France?"
    try:
        print("Translating sample...")
        print(translate_text(sample, source_lang="English", target_lang="Chinese"))
    except Exception as e:
        print("Error:", e)


def complete_text(prefix: str, max_tokens: int = 200, model: str = None) -> str:
    """Complete the user's partial text using the LLM and return the completed text.

    prefix: partial user content to complete
    max_tokens: max tokens to generate
    model: optional model override
    """
    if not prefix:
        return ""

    token = os.getenv("github_token")
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1-mini"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    system_prompt = (
        "You are a helpful assistant that continues and completes the user's partial content. "
        "When completing, preserve the user's tone, formatting and intent. Do not introduce contradictory facts. "
        "Return only the completed content without extra commentary."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prefix},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        top_p=1,
        max_tokens=max_tokens,
    )

    try:
        return resp.choices[0].message.content.strip()
    except Exception:
        raise RuntimeError(f"Unexpected LLM response format: {resp}")