import os
from pathlib import Path

def get_project_root():
    """Return the absolute path to the project root directory."""
    # Start with the current directory
    current_path = Path(os.getcwd()).absolute()

    # Navigate up until we find the project root (identified by having the 'data' folder)
    while current_path.name and not (current_path / 'data' / 'transcript_metadata.csv').exists():
        parent = current_path.parent
        if parent == current_path:  # Reached root without finding project directory
            break
        current_path = parent

    # Verify we found the right directory
    if (current_path / 'data' / 'transcript_metadata.csv').exists():
        return current_path
    else:
        raise FileNotFoundError("Could not locate project root (directory containing data/transcript_metadata.csv)")

def get_paths():
    """Return a dictionary of important project paths."""
    root = get_project_root()
    return {
        'root': root,
        'data': root / 'data',
        'transcripts': root / 'data' / 'transcripts',
        'raw_filings': root / 'data' / 'raw_filings',
        'output': root / 'data' / 'output',
        'logs': root / 'data' / 'logs',
        'metadata': root / 'data' / 'transcript_metadata.csv'
    }
