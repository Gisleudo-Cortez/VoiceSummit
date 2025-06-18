import os
import csv
from . import config

def append_record(timestamp: str, file_path: str, transcription: str, summary: str):
    """Append a new transcription record to the metadata CSV file."""
    os.makedirs(os.path.dirname(config.METADATA_FILE), exist_ok=True)
    file_exists = os.path.isfile(config.METADATA_FILE)
    with open(config.METADATA_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["CREATED", "AUDIO_FILE_PATH", "TRANSCRIPTION", "SUMMARY"])
        writer.writerow([timestamp, file_path, transcription, summary])

def get_records():
    """Read all records from the metadata CSV and return as a list of dicts."""
    if not os.path.isfile(config.METADATA_FILE):
        return []
    records = []
    with open(config.METADATA_FILE, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row:
                records.append(row)
    return records
