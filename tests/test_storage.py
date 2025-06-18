import os
from voice_processing import storage

# The only change is adding 'monkeypatch' to the function's arguments
def test_append_and_get_records(tmp_path, monkeypatch):
    """Tests that records can be appended and retrieved correctly."""
    # Use a temporary CSV file to avoid collisions
    temp_csv = tmp_path / "metadata.csv"
    # Monkeypatch the config to use the temporary file
    monkeypatch.setattr("voice_processing.storage.config.METADATA_FILE", str(temp_csv))

    # Ensure fresh start
    if os.path.exists(storage.config.METADATA_FILE):
        os.remove(storage.config.METADATA_FILE)

    # Append two records
    storage.append_record('2025-06-17T12:00:00Z', '/path/to/audio1.wav', 'transcript1', 'summary1')
    storage.append_record('2025-06-17T13:00:00Z', '/path/to/audio2.mp3', 'transcript2', 'summary2')

    # Read them back
    records = storage.get_records()
    assert len(records) == 2
    assert records[0]['AUDIO_FILE_PATH'] == '/path/to/audio1.wav'
    assert records[0]['TRANSCRIPTION'] == 'transcript1'
    assert records[0]['SUMMARY'] == 'summary1'

    # Clean up (optional as tmp_path handles it, but good practice)
    os.remove(storage.config.METADATA_FILE)
