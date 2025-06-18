import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Model Configuration ---
# Model for summarization/Q&A via OpenAI API
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4")

# Local model for summarization/Q&A via Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# --- Service URLs ---
# URL for the Ollama REST API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- File Paths ---
# Directory to store generated data like the metadata CSV
DATA_DIR = os.getenv("DATA_DIR", "data")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.csv")

# Default directory to watch for new audio files
DEFAULT_WATCH_DIR = os.getenv("DEFAULT_WATCH_DIR", "input_audio")
