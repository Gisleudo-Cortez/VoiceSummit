import os
import typer
from . import config
from . import llm_clients

# Global Whisper model (for local usage) to avoid reloading on each call
_local_model = None

def transcribe_file(audio_path: str, use_api: bool = False) -> str:
    """Transcribe an audio file to text."""
    if use_api:
        if not config.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found for transcription.")
        client = llm_clients.get_openai_client()
        typer.echo(f"-> Uploading {os.path.basename(audio_path)} to OpenAI API for transcription...")
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        typer.echo("-> Transcription complete.")
        return transcript.text.strip()
    else:
        global _local_model
        try:
            import whisper
        except ImportError:
            raise RuntimeError(
                "Whisper library not installed. Install with: pip install .[local]"
            )
        
        if _local_model is None:
            typer.echo("-> Loading local Whisper model for the first time... (This may take a few minutes)")
            _local_model = whisper.load_model("base")
        
        typer.echo(f"-> Transcribing {os.path.basename(audio_path)} locally... (This can be slow)")
        result = _local_model.transcribe(audio_path)
        typer.echo("-> Transcription complete.")
        return result.get("text", "").strip()
