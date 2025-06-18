# Voice Processing Pipeline

This project provides a robust, automated pipeline to transcribe audio files and leverage Large Language Models (LLMs) to summarize and query their content. It features a background service to watch for and process new audio files, and a powerful Command-Line Interface (CLI) to interact with the processed data.

The system is designed for flexibility and can operate in two distinct modes:
* **Local Mode**: Utilizes locally-hosted, open-source models for all processing. It uses a local Whisper model for transcription and a local LLM (e.g., Llama 2, Mistral) served via Ollama for summarization and Q&A. This mode is free to run and keeps all data on your machine.
* **API Mode**: Leverages the power of OpenAI's APIs. It uses the Whisper API for transcription and the GPT-4 (or other) API for summarization and Q&A. This mode requires an OpenAI API key.

The core workflow is simple: you drop an audio file into a designated folder, the watcher automatically transcribes and summarizes it, and the CLI then allows you to find insights from the content.

## Features

* **Automatic File Processing**: A background watcher service monitors an `input_audio/` directory for new `.wav` or `.mp3` files and processes them automatically.
* **Dual-Mode Transcription**: Transcribes audio to text using either a local Whisper model or the high-accuracy OpenAI Whisper API.
* **Dual-Mode Summarization & Q&A**: Generates summaries and answers questions using either a local model via the Ollama server or OpenAI's GPT API.
* **Persistent Data Storage**: All metadata, transcriptions, and summaries are saved in a clean, readable CSV file located at `data/metadata.csv`.
* **Powerful Command-Line Interface**: A rich CLI tool built with Typer allows you to:
    * Check the status of processed files.
    * View detailed transcriptions and summaries.
    * Ask questions about the content of your audio files.
    * Generate actionable plans and to-do lists from your transcripts.

## Project Structure

The project uses a `src`-layout to separate the source code from other files. Here are the key directories and files:

```
voice_processing/
├── input_audio/        # <== Drop your .wav and .mp3 files here
├── data/
│   └── metadata.csv    # <== Processed data is stored here
├── src/
│   └── voice_processing/ # <== Main Python source code
│       ├── cli.py      # Logic for the CLI tool
│       ├── watcher.py  # Logic for the background file watcher
│       └── ...
├── tests/              # Unit and integration tests
├── .env                # For storing your API keys and configuration
└── pyproject.toml      # Project definition and dependencies
```

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Gisleudo-Cortez/VoiceSummit.git
    cd voice_processing
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # Create the virtual environment
    python -m venv .venv
    # Activate it (Linux/macOS)
    source .venv/bin/activate
    # Or on Windows
    # .venv\Scripts\activate
    ```

3.  **Install Dependencies**
    The project uses optional dependencies so you only install what you need. Install the project in **editable mode** (`-e`) so changes to the code are immediately available.

    * **For Local Mode Only**:
        ```bash
        pip install -e .[local]
        ```
    * **For API Mode Only**:
        ```bash
        pip install -e .[api]
        ```
    * **For Development (to run tests and use both modes)**:
        ```bash
        pip install -e .[local,api,dev]
        ```

## Configuration

Configuration is managed via environment variables, which can be placed in a `.env` file in the project root.

1.  Create the file: `touch .env`
2.  Add the variables you need. Here are the available options:

| Variable            | Description                                            | Default Value                 |
| ------------------- | ------------------------------------------------------ | ----------------------------- |
| `OPENAI_API_KEY`    | Your secret API key from OpenAI. **Required for API mode.** | `None`                        |
| `OPENAI_CHAT_MODEL` | The chat model to use for summarization/Q&A in API mode. | `gpt-4`                       |
| `OLLAMA_MODEL`      | The local model to use via Ollama in local mode.       | `llama2`                      |
| `OLLAMA_BASE_URL`   | The URL for your running Ollama instance.              | `http://localhost:11434`      |


## How to Use

### 1. Processing Audio Files (The Watcher)

The watcher is the background service that finds and processes your audio files.

**Prerequisites for Local Mode**:
* Ensure the Ollama server is running. You can start it by running `ollama serve` in a separate terminal.

**To start the watcher:**
```bash
# To run using local models (default)
voice-processing-watcher

# To run using the OpenAI API
voice-processing-watcher --use-api
```
The watcher will start and monitor the `input_audio/` directory. Now, simply **copy or move** a `.wav` or `.mp3` file into that folder. The watcher will detect it and begin processing. You will see detailed feedback in the terminal as it moves through transcription and summarization.

### 2. Querying Your Data (The CLI)

The CLI is your tool for interacting with the processed data. The base command is `voice-processing-cli`.

* **To Check Status**
    View a summary of all processed files.
    ```bash
    voice-processing-cli status
    ```

* **To Show Details**
    Display the full transcription and summary for a specific file.
    ```bash
    # Show the most recently processed file
    voice-processing-cli show

    # Show the first processed file by its index number
    voice-processing-cli show 1

    # Find and show a file by a partial name match
    voice-processing-cli show my_meeting
    ```

* **To Ask a Question**
    Get answers based on the content of your transcripts. This command can operate in local or API mode.
    ```bash
    # Using the local model
    voice-processing-cli ask "What were the main decisions from the project update?"

    # Using the OpenAI API for a more powerful response
    voice-processing-cli --use-api ask "Generate a list of all people mentioned in the transcripts."
    ```

* **To Generate a Plan**
    Create a list of action items based on the transcripts.
    ```bash
    # Using the local model
    voice-processing-cli plan

    # Using the OpenAI API
    voice-processing-cli --use-api plan
    ```

## Development and Testing

To run the test suite, make sure you have installed the project with the `[dev]` dependencies.
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest
```
