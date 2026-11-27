#!/usr/bin/env python3
"""Validate a Gemini JSON or streaming SSE response without exposing its contents."""
import json
import sys
from pathlib import Path


def valid_response(text):
    text = text.strip()
    if not text:
        return False
    try:
        objects = [json.loads(text)]
    except json.JSONDecodeError:
        objects = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('event:') and line[6:].strip().lower() in ('error', 'interaction.error'):
                return False
            if not line or line.startswith((':', 'event:', 'id:', 'retry:')):
                continue
            if line.startswith('data:'):
                line = line[5:].strip()
            if line == '[DONE]':
                continue
            try:
                objects.append(json.loads(line))
            except json.JSONDecodeError:
                return False
    return bool(objects) and all(isinstance(obj, dict) and 'error' not in obj and obj.get('event_type') != 'error' and obj.get('type') != 'error' for obj in objects)


if __name__ == '__main__':
    sys.exit(0 if valid_response(Path(sys.argv[1]).read_text(encoding='utf-8')) else 1)
