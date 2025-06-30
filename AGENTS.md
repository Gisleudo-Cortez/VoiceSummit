## Build, Lint, and Test

- **Install dependencies**: `pip install -e .[dev]`
- **Run all tests**: `pytest`
- **Run a single test file**: `pytest tests/test_cli.py`
- **Run a single test function**: `pytest tests/test_cli.py::test_status_command`
- **Linting**: No linter is configured, but follow `black` formatting.

## Code Style

- **Formatting**: Use `black` for code formatting.
- **Imports**: Group imports: 1. standard library, 2. third-party, 3. local application. Sort alphabetically.
- **Typing**: Use type hints for all function signatures. Use `typing_extensions.Annotated` for Typer CLI arguments.
- **Naming**: Use `snake_case` for variables and functions. Use `PascalCase` for classes.
- **Error Handling**: Use `typer.secho` for user-facing errors and `typer.Exit` to exit with a non-zero code.
- **Docstrings**: Use docstrings for all public modules, classes, and functions.
- **Configuration**: Centralize configuration in `src/voice_processing/config.py`.
- **LLM Clients**: Abstract LLM client logic in `src/voice_processing/llm_clients.py`.
- **Storage**: Abstract data storage logic in `src/voice_processing/storage.py`.
- **CLI**: Keep CLI logic in `src/voice_processing/cli.py` and `src/voice_processing/watcher.py`.
