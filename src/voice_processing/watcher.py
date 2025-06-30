import os
import time
import threading
import typer
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from datetime import datetime, timezone
from . import transcribe, summarize, storage, config

app = typer.Typer(add_completion=False)

class AudioHandler(PatternMatchingEventHandler):
    def __init__(self, use_api=False):
        super().__init__(patterns=["*.wav", "*.mp3"], ignore_directories=True)
        self.use_api = use_api
        self.processing_lock = threading.Lock()
        self.processed_files = set()

    def on_created(self, event):
        self.process_event(event.src_path)

    def on_modified(self, event):
        self.process_event(event.src_path)

    def process_event(self, file_path):
        with self.processing_lock:
            if file_path in self.processed_files:
                return  # Already processing this file
            self.processed_files.add(file_path)

        # Run processing in a separate thread to not block the observer
        thread = threading.Thread(target=self._handle_event, args=(file_path,))
        thread.start()

    def _handle_event(self, file_path):
        try:
            typer.echo(f"Detected audio file: {file_path}")
            # Wait for file to stabilize
            time.sleep(1) # Initial wait
            last_size = -1
            for _ in range(5):  # Check for 5 seconds
                try:
                    current_size = os.path.getsize(file_path)
                    if current_size == last_size:
                        break
                    last_size = current_size
                    time.sleep(1)
                except FileNotFoundError:
                    typer.secho(f"File disappeared: {file_path}", fg=typer.colors.RED)
                    return # File was deleted before processing could start

            ts = os.path.getmtime(file_path)
            created_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

            text = transcribe.transcribe_file(file_path, use_api=self.use_api)
            summary = summarize.summarize_text(text, use_api=self.use_api)
            storage.append_record(created_iso, os.path.abspath(file_path), text, summary)

            typer.secho(f"Successfully processed: {os.path.basename(file_path)}", fg=typer.colors.GREEN)

        except Exception as e:
            typer.secho(f"Error processing {file_path}: {e}", fg=typer.colors.RED)
        finally:
            # Allow file to be re-processed if it's modified again
            with self.processing_lock:
                if file_path in self.processed_files:
                    self.processed_files.remove(file_path)


def process_existing_files(watch_dir: str, handler: "AudioHandler"):
    """Process any audio files that were missed while the watcher was not running."""
    typer.echo("Checking for unprocessed files...")
    processed_paths = storage.get_processed_files()
    found_unprocessed = False
    for filename in os.listdir(watch_dir):
        if filename.endswith((".wav", ".mp3")):
            file_path = os.path.abspath(os.path.join(watch_dir, filename))
            if file_path not in processed_paths:
                found_unprocessed = True
                typer.echo(f"Found unprocessed file: {filename}")
                handler.process_event(file_path)
    if not found_unprocessed:
        typer.echo("No unprocessed files found.")

@app.command()
def watch(
    watch_dir: str = typer.Argument(
        config.DEFAULT_WATCH_DIR,
        help="Directory to watch for new audio files.",
    ),
    use_api: bool = typer.Option(
        False, "--use-api", help="Use OpenAI API instead of local models."
    ),
):
    """
    Watch a directory for new audio files and process them automatically.
    """
    if use_api and not config.OPENAI_API_KEY:
        typer.secho("Error: --use-api specified but OPENAI_API_KEY is not set.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Ensure the watch directory exists
    os.makedirs(watch_dir, exist_ok=True)
    abs_watch_dir = os.path.abspath(watch_dir)

    mode = "API" if use_api else "Local"
    typer.echo(f"Starting watcher in {mode} mode.")
    typer.echo(f"Watching directory: {abs_watch_dir} (Press Ctrl+C to stop)")

    handler = AudioHandler(use_api=use_api)
    
    # Process any files that were missed
    process_existing_files(abs_watch_dir, handler)

    observer = Observer()
    observer.schedule(handler, abs_watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    typer.echo("Watcher stopped.")

if __name__ == "__main__":
    app()
