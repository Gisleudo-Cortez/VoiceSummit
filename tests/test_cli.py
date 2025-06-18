import pytest
from typer.testing import CliRunner
from types import SimpleNamespace
from voice_processing.cli import app

# Create a runner instance to invoke CLI commands
runner = CliRunner()

@pytest.fixture
def mock_storage_and_config(monkeypatch):
    """A fixture to mock storage and config for all CLI tests."""
    dummy_records = [
        {'CREATED': '2025-06-18T12:00:00Z', 'AUDIO_FILE_PATH': '/path/file1.wav', 'TRANSCRIPTION': 'Alice went to the market.', 'SUMMARY': 'Alice shopping.'},
        {'CREATED': '2025-06-18T13:00:00Z', 'AUDIO_FILE_PATH': '/path/file2.mp3', 'TRANSCRIPTION': 'Bob will build a house.', 'SUMMARY': 'Bob building.'}
    ]
    # Patch the get_records function in the storage module
    monkeypatch.setattr("voice_processing.storage.get_records", lambda: dummy_records)
    # Ensure the API key is set for --use-api tests
    monkeypatch.setattr("voice_processing.config.OPENAI_API_KEY", "test-key-for-cli")
    return dummy_records

def test_status_command(mock_storage_and_config):
    """Tests the 'status' command output."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Total files processed: 2" in result.stdout
    assert "file1.wav" in result.stdout
    assert "file2.mp3" in result.stdout

def test_show_command_by_index(mock_storage_and_config):
    """Tests the 'show' command using a numeric index."""
    result = runner.invoke(app, ["show", "1"])
    assert result.exit_code == 0
    assert "Alice went to the market." in result.stdout
    assert "Alice shopping." in result.stdout

def test_show_command_latest(mock_storage_and_config):
    """Tests that 'show' with no arguments displays the latest record."""
    result = runner.invoke(app, ["show"])
    assert result.exit_code == 0
    assert "Bob will build a house." in result.stdout # Should be the last record
    assert "Bob building." in result.stdout

def test_ask_local_command(mock_storage_and_config, monkeypatch):
    """Tests the 'ask' command in local mode."""
    # Mock the local LLM client function
    monkeypatch.setattr("voice_processing.llm_clients.generate_text", lambda model, prompt: "Local LLM says: She went to buy food.")
    result = runner.invoke(app, ["ask", "What did Alice do?"])
    assert result.exit_code == 0
    assert "Local LLM says: She went to buy food." in result.stdout

def test_ask_api_command(mock_storage_and_config, monkeypatch):
    """Tests the 'ask' command with the --use-api flag."""
    # Mock the OpenAI client and its response structure
    class MockChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)
    mock_response = SimpleNamespace(choices=[MockChoice("API says: Alice went to the market.")])
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: mock_response)))
    monkeypatch.setattr("voice_processing.llm_clients.get_openai_client", lambda: mock_client)

    result = runner.invoke(app, ["--use-api", "ask", "What did Alice do?"])
    assert result.exit_code == 0
    assert "API says: Alice went to the market." in result.stdout

def test_plan_local_command(mock_storage_and_config, monkeypatch):
    """Tests the 'plan' command in local mode."""
    monkeypatch.setattr("voice_processing.llm_clients.generate_text", lambda model, prompt: "- Buy groceries\n- Build a house")
    result = runner.invoke(app, ["plan"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.stdout

def test_plan_api_command(mock_storage_and_config, monkeypatch):
    """Tests the 'plan' command with the --use-api flag."""
    class MockChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)
    mock_response = SimpleNamespace(choices=[MockChoice("- API Plan: Bob needs to build a house.")])
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: mock_response)))
    monkeypatch.setattr("voice_processing.llm_clients.get_openai_client", lambda: mock_client)

    result = runner.invoke(app, ["--use-api", "plan"])
    assert result.exit_code == 0
    assert "API Plan: Bob needs to build a house." in result.stdout
