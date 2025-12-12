# Clipboard History Manager

Stores a searchable history of copied text locally, with optional recall.

## Features

- **Clipboard Monitoring**: Automatically captures clipboard content
- **Searchable History**: Search through past clipboard entries
- **Timestamp Tracking**: Each entry is timestamped
- **Quick Recall**: Quickly paste previous clipboard entries
- **Privacy**: All data stored locally, no cloud sync
- **Configurable Retention**: Set how long to keep history

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python clipboard_manager.py [COMMAND] [OPTIONS]
```

### Commands

- `start`: Start monitoring clipboard
- `list`: List clipboard history
- `search QUERY`: Search history
- `get INDEX`: Get entry by index
- `clear`: Clear history
- `stats`: Show statistics

### Options

- `--limit N`: Limit number of entries to show
- `--days N`: Show entries from last N days
- `--max-size MB`: Maximum size for clipboard entries (default: 10MB)

### Examples

```bash
# Start monitoring clipboard
python clipboard_manager.py start

# List recent clipboard history
python clipboard_manager.py list --limit 20

# Search for "password"
python clipboard_manager.py search password

# Get entry #5
python clipboard_manager.py get 5

# Show statistics
python clipboard_manager.py stats

# Clear old entries (older than 30 days)
python clipboard_manager.py clear --days 30
```

## Data Storage

Clipboard history is stored in:
- `~/.clipboard_history/clipboard.json` - History data
- `~/.clipboard_history/config.json` - Configuration

