import typer
from . import config
from . import llm_clients

def summarize_text(text: str, use_api: bool = False) -> str:
    """Summarize a transcript text."""
    if use_api:
        if not config.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found for summarization.")
        client = llm_clients.get_openai_client()
        typer.echo("-> Summarizing with OpenAI API...")
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes text into concise bullet points.",
            },
            {
                "role": "user",
                "content": "Summarize the following text in bullet points:\n\n" + text,
            },
        ]
        response = client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL, messages=messages
        )
        summary = response.choices[0].message.content or ""
        typer.echo("-> Summarization complete.")
        return summary.strip()
    else:
        typer.echo("-> Summarizing with local Ollama model...")
        prompt = "Summarize the following text in bullet points:\n\n" + text
        summary = llm_clients.generate_text(config.OLLAMA_MODEL, prompt)
        typer.echo("-> Summarization complete.")
        return summary.strip()
