import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Free models available on OpenRouter ───────────────────────
FREE_MODELS = {
    "Z.ai: GLM 4.5 Air":         "z-ai/glm-4.5-air:free",
    "Llama 3.3 70B (Meta)":      "meta-llama/llama-3.3-70b-instruct:free",
    "NVIDIA: Nemotron 3 Super":  "nvidia/nemotron-3-super-120b-a12b:free",
    "StepFun: Step 3.5 Flash":   "stepfun/step-3.5-flash:free",
    "Qwen 3.6 Plus (Alibaba)":   "qwen/qwen3.6-plus:free",
    "MiniMax: MiniMax M2.5":     "minimax/minimax-m2.5:free",
    "OpenAI: gpt-oss-120b":       "openai/gpt-oss-120b:free",
}

# ── Default model ─────────────────────────────────────────────
DEFAULT_MODEL = FREE_MODELS["Qwen 3.6 Plus (Alibaba)"]


def get_openrouter_client() -> OpenAI:
    """
    OpenRouter uses the OpenAI SDK — just different base_url and api_key.
    """
    return OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL",  "http://localhost:8501"),
            "X-Title":      os.getenv("APP_NAME", "Cartier APAC AI Hub"),
        }
    )


def chat_completion(
    messages:    list,
    model:       str   = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens:  int   = 1024,
) -> str:
    """
    Main LLM call — drop-in compatible with all modules.
    """
    client = get_openrouter_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return (
                "⚠️ Rate limit reached on free tier. "
                "Please wait 10 seconds and try again."
            )
        elif "401" in error_msg:
            return (
                "⚠️ Invalid OpenRouter API key. "
                "Check your .env file."
            )
        elif "503" in error_msg:
            return (
                "⚠️ Model temporarily unavailable. "
                "Try switching to a different free model in the sidebar."
            )
        else:
            return f"⚠️ LLM Error: {error_msg}"


def get_available_free_models() -> dict:
    """Returns the free model registry — used by sidebar model selector."""
    return FREE_MODELS


def get_default_model() -> str:
    """Returns the default model string."""
    return DEFAULT_MODEL