#!/usr/bin/env python3
"""
Clipboard History Manager - Stores searchable history of copied text.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import pyperclip
except ImportError:
    print("Error: pyperclip library is required.")
    print("Install it with: pip install pyperclip")
    sys.exit(1)


class ClipboardManager:
    def __init__(self, data_dir: Optional[str] = None, max_size_mb: int = 10):
        if data_dir is None:
            data_dir = Path.home() / '.clipboard_history'
        else:
            data_dir = Path(data_dir)
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.data_dir / 'clipboard.json'
        self.config_file = self.data_dir / 'config.json'
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        self.load_data()
    
    def load_data(self):
        """Load clipboard history and config."""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'max_entries': 1000,
                'retention_days': 30
            }
            self.save_config()
    
    def save_data(self):
        """Save clipboard history."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def save_config(self):
        """Save configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_entry(self, content: str):
        """Add entry to history."""
        # Skip if too large
        if len(content.encode('utf-8')) > self.max_size_bytes:
            return False
        
        # Skip if same as last entry
        if self.history and self.history[-1]['content'] == content:
            return False
        
        entry = {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'size': len(content.encode('utf-8'))
        }
        
        self.history.append(entry)
        
        # Limit history size
        max_entries = self.config.get('max_entries', 1000)
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]
        
        self.save_data()
        return True
    
    def monitor(self, interval: float = 1.0):
        """Monitor clipboard for changes."""
        print("Monitoring clipboard... Press Ctrl+C to stop.")
        print(f"History file: {self.history_file}")
        print()
        
        last_content = None
        
        try:
            while True:
                try:
                    current_content = pyperclip.paste()
                    
                    if current_content and current_content != last_content:
                        if self.add_entry(current_content):
                            preview = current_content[:50].replace('\n', ' ')
                            if len(current_content) > 50:
                                preview += "..."
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Captured: {preview}")
                        
                        last_content = current_content
                    
                    time.sleep(interval)
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def list_entries(self, limit: Optional[int] = None, days: Optional[int] = None):
        """List clipboard history entries."""
        entries = self.history.copy()
        
        # Filter by days
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            entries = [e for e in entries 
                      if datetime.fromisoformat(e['timestamp']) >= cutoff]
        
        # Reverse to show newest first
        entries.reverse()
        
        # Limit
        if limit:
            entries = entries[:limit]
        
        if not entries:
            print("No clipboard history entries found.")
            return
        
        print(f"\nClipboard History ({len(entries)} entries):")
        print("=" * 70)
        
        for i, entry in enumerate(entries, 1):
            dt = datetime.fromisoformat(entry['timestamp'])
            content = entry['content']
            preview = content[:60].replace('\n', ' ')
            if len(content) > 60:
                preview += "..."
            
            size_kb = entry['size'] / 1024
            print(f"{i}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}] ({size_kb:.1f} KB)")
            print(f"   {preview}")
            print()
    
    def search(self, query: str, limit: Optional[int] = None):
        """Search clipboard history."""
        query_lower = query.lower()
        matches = []
        
        for entry in reversed(self.history):
            if query_lower in entry['content'].lower():
                matches.append(entry)
                if limit and len(matches) >= limit:
                    break
        
        if not matches:
            print(f"No entries found matching '{query}'")
            return
        
        print(f"\nFound {len(matches)} matching entries:")
        print("=" * 70)
        
        for i, entry in enumerate(matches, 1):
            dt = datetime.fromisoformat(entry['timestamp'])
            content = entry['content']
            preview = content[:80].replace('\n', ' ')
            if len(content) > 80:
                preview += "..."
            
            print(f"{i}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"   {preview}")
            print()
    
    def get_entry(self, index: int):
        """Get entry by index (1-based, newest first)."""
        if not self.history:
            print("No clipboard history.")
            return
        
        entries = list(reversed(self.history))
        
        if index < 1 or index > len(entries):
            print(f"Invalid index. Range: 1-{len(entries)}")
            return
        
        entry = entries[index - 1]
        dt = datetime.fromisoformat(entry['timestamp'])
        
        print(f"\nEntry #{index}:")
        print("=" * 70)
        print(f"Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Size: {entry['size']} bytes")
        print(f"Content:")
        print("-" * 70)
        print(entry['content'])
        print("-" * 70)
        
        # Option to copy to clipboard
        try:
            response = input("\nCopy to clipboard? (y/n): ")
            if response.lower() == 'y':
                pyperclip.copy(entry['content'])
                print("Copied to clipboard!")
        except KeyboardInterrupt:
            pass
    
    def clear(self, days: Optional[int] = None):
        """Clear clipboard history."""
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            original_count = len(self.history)
            self.history = [e for e in self.history 
                          if datetime.fromisoformat(e['timestamp']) >= cutoff]
            removed = original_count - len(self.history)
            print(f"Removed {removed} entries older than {days} days.")
        else:
            response = input("Clear all clipboard history? (yes/no): ")
            if response.lower() == 'yes':
                self.history = []
                print("Clipboard history cleared.")
            else:
                print("Cancelled.")
        
        self.save_data()
    
    def stats(self):
        """Show statistics."""
        if not self.history:
            print("No clipboard history.")
            return
        
        total_entries = len(self.history)
        total_size = sum(e['size'] for e in self.history)
        avg_size = total_size / total_entries if total_entries > 0 else 0
        
        # Entries by day
        by_day = {}
        for entry in self.history:
            date = datetime.fromisoformat(entry['timestamp']).date()
            by_day[date] = by_day.get(date, 0) + 1
        
        print("\nClipboard History Statistics:")
        print("=" * 70)
        print(f"Total Entries: {total_entries}")
        print(f"Total Size: {total_size / (1024*1024):.2f} MB")
        print(f"Average Entry Size: {avg_size:.0f} bytes")
        print(f"Days with Activity: {len(by_day)}")
        print(f"\nMost Active Days:")
        for date, count in sorted(by_day.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {date}: {count} entries")


def main():
    parser = argparse.ArgumentParser(description='Clipboard History Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start monitoring clipboard')
    start_parser.add_argument('--interval', type=float, default=1.0,
                             help='Check interval in seconds')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List clipboard history')
    list_parser.add_argument('--limit', type=int, help='Limit number of entries')
    list_parser.add_argument('--days', type=int, help='Show entries from last N days')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search history')
    search_parser.add_argument('query', type=str, help='Search query')
    search_parser.add_argument('--limit', type=int, help='Limit results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get entry by index')
    get_parser.add_argument('index', type=int, help='Entry index (1-based)')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear history')
    clear_parser.add_argument('--days', type=int,
                             help='Clear entries older than N days')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    manager = ClipboardManager()
    
    if args.command == 'start':
        manager.monitor(args.interval if hasattr(args, 'interval') else 1.0)
    elif args.command == 'list':
        manager.list_entries(
            limit=getattr(args, 'limit', None),
            days=getattr(args, 'days', None)
        )
    elif args.command == 'search':
        manager.search(args.query, getattr(args, 'limit', None))
    elif args.command == 'get':
        manager.get_entry(args.index)
    elif args.command == 'clear':
        manager.clear(getattr(args, 'days', None))
    elif args.command == 'stats':
        manager.stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

