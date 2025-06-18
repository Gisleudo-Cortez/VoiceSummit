import requests
import openai
from . import config

# --- OpenAI Client ---
_openai_client = None

def get_openai_client():
    """Get the OpenAI client, initializing it if necessary."""
    global _openai_client
    if _openai_client is None:
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")
        _openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client

# --- Ollama Client ---
def generate_text(model: str, prompt: str) -> str:
    """Generate text from a local model via the Ollama REST API."""
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to connect to Ollama at {config.OLLAMA_BASE_URL}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to generate text with Ollama: {e}")
