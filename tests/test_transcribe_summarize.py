import pytest
from types import SimpleNamespace
from voice_processing import transcribe, summarize

def test_transcribe_local(monkeypatch, tmp_path):
    """Tests local transcription by mocking the whisper library."""
    pytest.importorskip('whisper')

    dummy_model = SimpleNamespace(transcribe=lambda path: {'text': 'hello local world'})
    # Patch the whisper library functions as they are called inside transcribe.py
    monkeypatch.setattr("voice_processing.transcribe._local_model", None) # Reset model
    monkeypatch.setattr("whisper.load_model", lambda name: dummy_model)

    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b'dummy audio')
    result = transcribe.transcribe_file(str(audio_file), use_api=False)
    assert result == 'hello local world'

def test_transcribe_api(monkeypatch, tmp_path):
    """Tests API transcription by mocking the OpenAI client."""
    # Mock the response from the OpenAI client
    mock_transcript = SimpleNamespace(text="hello api world")
    mock_client = SimpleNamespace(audio=SimpleNamespace(transcriptions=SimpleNamespace(create=lambda model, file: mock_transcript)))
    monkeypatch.setattr("voice_processing.llm_clients.get_openai_client", lambda: mock_client)
    monkeypatch.setattr("voice_processing.config.OPENAI_API_KEY", "test-key-for-transcribe")

    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b'dummy audio')
    result = transcribe.transcribe_file(str(audio_file), use_api=True)
    assert result == 'hello api world'

def test_summarize_local(monkeypatch):
    """Tests local summarization by mocking the llm_clients function."""
    # Patch the centralized function for generating text with Ollama
    monkeypatch.setattr("voice_processing.llm_clients.generate_text", lambda model, prompt: "local summary")
    
    text = 'Some long transcript...'
    result = summarize.summarize_text(text, use_api=False)
    assert result == 'local summary'

def test_summarize_api(monkeypatch):
    """Tests API summarization by mocking the OpenAI client."""
    class MockChoice:
        def __init__(self, content):
            self.message = SimpleNamespace(content=content)
    mock_response = SimpleNamespace(choices=[MockChoice('api summary')])
    mock_client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: mock_response)))
    monkeypatch.setattr("voice_processing.llm_clients.get_openai_client", lambda: mock_client)
    monkeypatch.setattr("voice_processing.config.OPENAI_API_KEY", "test-key-for-summarize")

    text = 'Transcript text'
    result = summarize.summarize_text(text, use_api=True)
    assert result == 'api summary'
