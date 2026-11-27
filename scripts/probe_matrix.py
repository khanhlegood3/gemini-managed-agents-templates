#!/usr/bin/env python3
"""Validate templates and publish the Actions probe matrix."""
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

root = Path(__file__).resolve().parent.parent
entries = []
for path in sorted(root.glob('*/agent.yaml')):
    config = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(config, dict) or not isinstance(config.get('examples', []), list):
        raise ValueError(f'{path}: invalid configuration or examples')
    for example in config.get('examples', []):
        if not isinstance(example, dict) or not all(isinstance(example.get(k), str) and example[k].strip() for k in ('title', 'prompt')):
            raise ValueError(f'{path}: each example needs a non-empty title and prompt')
        entries.append({'template': path.parent.name, 'chip': example['title'], 'prompt': example['prompt']})
    # Exercise payload generation for each template, without sending any secrets or requests.
    env = {**os.environ, 'GEMINI_API_KEY': 'validation-only'}
    result = subprocess.run([sys.executable, str(root / 'generate_payload.py'), 'Validation'], cwd=path.parent, env=env, check=True, capture_output=True, text=True)
    json.loads(result.stdout)
if not entries:
    raise ValueError('No example prompts found')
if len(entries) > 256:
    raise ValueError('The probe matrix exceeds the GitHub Actions limit of 256 jobs')
print(f'Validated {len(entries)} example prompts')
if 'GITHUB_OUTPUT' in os.environ:
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write('matrix=' + json.dumps(entries, ensure_ascii=True) + '\n')
