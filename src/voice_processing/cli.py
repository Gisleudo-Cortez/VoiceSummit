import os
import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.spinner import Spinner
from rich.table import Table
from . import storage, config, llm_clients

# Create a Typer app instance
app = typer.Typer(
    add_completion=False,
    help="CLI to query audio transcripts and summaries.",
)

class AppState:
    def __init__(self, use_api: bool):
        self.use_api = use_api

def _get_context_text():
    """Helper to retrieve all transcriptions or summaries as a single text block."""
    records = storage.get_records()
    if not records:
        return None, None
    full_text = "\n\n---\n\n".join(rec["TRANSCRIPTION"] for rec in records if rec["TRANSCRIPTION"])
    # Use summaries if full text is too long, to conserve tokens
    if len(full_text) > 12000:
        context_text = "\n\n---\n\n".join(rec["SUMMARY"] for rec in records if rec["SUMMARY"])
        return context_text, "summaries"
    return full_text, "transcriptions"

def _answer_question(ctx: typer.Context, question: str) -> str:
    app_state: AppState = ctx.obj
    context_text, context_type = _get_context_text()
    if not context_text:
        return "No transcripts available to answer questions."

    if app_state.use_api:
        client = llm_clients.get_openai_client()
        messages = [
            {"role": "system", "content": f"You are a helpful assistant. Answer the user's question based *only* on the provided context from audio {context_type}. If the answer is not in the context, say so."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"},
        ]
        response = client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL, messages=messages
        )
        return response.choices[0].message.content or "No answer returned."
    else:
        prompt = f"Based on the following transcripts, answer the question. Only use the provided information.\n\nTranscripts:\n{context_text}\n\nQuestion: {question}\nAnswer:"
        return llm_clients.generate_text(config.OLLAMA_MODEL, prompt)

def _generate_plan(ctx: typer.Context) -> str:
    app_state: AppState = ctx.obj
    context_text, context_type = _get_context_text()
    if not context_text:
        return "No transcripts available to generate a plan."

    if app_state.use_api:
        client = llm_clients.get_openai_client()
        messages = [
            {"role": "system", "content": "You are an assistant who creates action plans from text. Analyze the context and extract actionable tasks. If there are no actions, say so."},
            {"role": "user", "content": f"Context from audio {context_type}:\n{context_text}\n\nPlease create a bulleted list of action items:"},
        ]
        response = client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL, messages=messages
        )
        return response.choices[0].message.content or "No plan returned."
    else:
        prompt = f"Read the following transcripts and extract a list of actionable tasks or next steps. Provide a plan with bullet points.\n\nTranscripts:\n{context_text}\n\nAction Plan:"
        return llm_clients.generate_text(config.OLLAMA_MODEL, prompt)

from rich.table import Table

@app.command()
def status():
    """Show a summary of processed audio files."""
    records = storage.get_records()
    if not records:
        typer.echo("No audio files have been processed yet.")
        return

    count = len(records)
    typer.secho(f"Total files processed: {count}", fg=typer.colors.BLUE)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Index", style="dim", width=5)
    table.add_column("File Name")
    table.add_column("Created Date", justify="right")

    # Show last 10 records
    for i, rec in enumerate(records[-10:], 1):
        fname = os.path.basename(rec["AUDIO_FILE_PATH"])
        table.add_row(str(len(records) - 10 + i), fname, rec["CREATED"])

    console.print(table)

@app.command()
def show(identifier: Annotated[str, typer.Argument(help="Index (e.g., '1') or partial filename of the record to show. Shows the latest if omitted.")] = None):
    """Show the full transcription and summary of a specific record."""
    records = storage.get_records()
    if not records:
        typer.echo("No records found.")
        return

    rec_to_show = None
    if identifier is None:
        rec_to_show = records[-1] # Default to the last record
    elif identifier.isdigit():
        idx = int(identifier)
        if 1 <= idx <= len(records):
            rec_to_show = records[idx - 1]
    else:
        # Find first record whose file path contains the identifier
        rec_to_show = next((r for r in records if identifier.lower() in r["AUDIO_FILE_PATH"].lower()), None)

    if not rec_to_show:
        typer.secho(f"Error: No record found for identifier '{identifier}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"File: {rec_to_show['AUDIO_FILE_PATH']}", fg=typer.colors.BLUE)
    typer.secho(f"Created: {rec_to_show['CREATED']}", fg=typer.colors.BLUE)
    typer.secho("\n--- Transcription ---", fg=typer.colors.GREEN)
    typer.echo(rec_to_show["TRANSCRIPTION"])
    typer.secho("\n--- Summary ---", fg=typer.colors.YELLOW)
    typer.echo(rec_to_show["SUMMARY"])


console = Console()

@app.command()
def ask(ctx: typer.Context, question: Annotated[str, typer.Argument(help="Question to ask about the transcripts.")]):
    """Ask a question about the content of all processed transcripts."""
    with console.status("[bold green]Thinking...", spinner="dots"):
        answer = _answer_question(ctx, question)
    typer.echo(answer)


@app.command()
def plan(ctx: typer.Context):
    """Generate an action plan from all processed transcripts."""
    with console.status("[bold green]Generating plan...", spinner="dots"):
        plan_text = _generate_plan(ctx)
    typer.echo(plan_text)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    use_api: bool = typer.Option(
        False, "--use-api", help="Use OpenAI API instead of local models."
    ),
):
    """
    Callback to set up shared state (like the 'use_api' flag) for all commands.
    """
    if use_api and not config.OPENAI_API_KEY:
        typer.secho("Error: --use-api specified but OPENAI_API_KEY is not set.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    # Store the state in the context object to be accessed by commands
    ctx.obj = AppState(use_api=use_api)

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)

if __name__ == "__main__":
    app()
