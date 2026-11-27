#!/usr/bin/env python3
"""Build a small, self-contained GitHub Pages catalog from agent.yaml files."""
import html
import os
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / '_site'


def escape(value):
    return html.escape(str(value), quote=True)


def build():
    repository = os.environ.get('GITHUB_REPOSITORY', 'khanhlegood3/gemini-managed-agents-templates')
    server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com').rstrip('/')
    source = f'{server}/{repository}/tree/main'
    cards = []
    for path in sorted(ROOT.glob('*/agent.yaml')):
        config = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not isinstance(config, dict):
            raise ValueError(f'{path}: expected a mapping')
        directory = path.parent.name
        title = directory.replace('-', ' ').title()
        description = config.get('description', 'Agent template')
        examples = config.get('examples', [])
        titles = ''.join(f'<li>{escape(item["title"])}</li>' for item in examples)
        filename = 'README.md' if (path.parent / 'README.md').is_file() else 'agent.yaml'
        link = f'{source}/{quote(directory)}/{filename}'
        cards.append(f'''<article class="card"><p class="eyebrow">AGENT TEMPLATE</p>
<h2>{escape(title)}</h2><p>{escape(description)}</p>
<h3>Example prompts</h3><ul>{titles}</ul>
<a href="{escape(link)}">Explore template <span aria-hidden="true">↗</span></a></article>''')
    if not cards:
        raise ValueError('No agent templates found')
    template = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / 'index.html').write_text(template.replace('<!-- TEMPLATE_CARDS -->', '\n'.join(cards)).replace('<!-- REPOSITORY_URL -->', escape(f'{server}/{repository}')), encoding='utf-8')
    (OUTPUT / 'style.css').write_text((ROOT / 'site' / 'style.css').read_text(encoding='utf-8'), encoding='utf-8')
    print(f'Built {len(cards)} template cards in {OUTPUT}')


if __name__ == '__main__':
    build()
