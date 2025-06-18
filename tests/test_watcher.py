from types import SimpleNamespace
from voice_processing import watcher

def test_watcher_process(monkeypatch, tmp_path):
    # Monkeypatch transcribe and summarize to avoid real processing
    monkeypatch.setattr('voice_processing.watcher.transcribe.transcribe_file',
                        lambda path, use_api=False: 'transcribed text')
    monkeypatch.setattr('voice_processing.watcher.summarize.summarize_text',
                        lambda text, use_api=False: 'summary text')

    # Monkeypatch storage.append_record to capture the data
    saved = {}
    def fake_append(ts, path, text, summary):
        saved.update(timestamp=ts, path=path, text=text, summary=summary)
    monkeypatch.setattr('voice_processing.watcher.storage.append_record', fake_append)

    # Speed up any time.sleep calls
    monkeypatch.setattr('voice_processing.watcher.time.sleep', lambda x: None)

    # Create a dummy file to simulate an event
    audio_file = tmp_path / "audio.wav"
    audio_file.write_bytes(b'dummy')
    event = SimpleNamespace(is_directory=False, src_path=str(audio_file))
    
    handler = watcher.AudioHandler(use_api=False)

    # --- THE FIX ---
    # Instead of calling handler.on_created(event), which starts a background thread,
    # we call the internal _handle_event method directly. This makes the test
    # synchronous and predictable, eliminating the race condition.
    handler._handle_event(event.src_path)

    # Verify that data was captured correctly, now that we've waited
    assert saved.get('text') == 'transcribed text'
    assert saved.get('summary') == 'summary text'
    assert saved.get('path', '').endswith('audio.wav')
    assert 'T' in saved.get('timestamp', '')
