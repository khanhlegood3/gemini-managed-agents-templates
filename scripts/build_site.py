#!/usr/bin/env python3
"""Build a static catalog and a readable page for every agent template."""
import html
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit

import bleach
import markdown
import yaml
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / '_site'


def escape(value):
    return html.escape(str(value), quote=True)


class ResolveLinks(Treeprocessor):
    def __init__(self, md, base_url):
        super().__init__(md)
        self.base_url = base_url

    def run(self, root):
        for node in root.iter('a'):
            href = node.get('href', '')
            if href and not href.startswith(('#', '//')) and not urlsplit(href).scheme:
                node.set('href', urljoin(self.base_url, href))


class ResolveLinksExtension(Extension):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def extendMarkdown(self, md):
        md.treeprocessors.register(ResolveLinks(md, self.base_url), 'resolve_links', 5)


def render_readme(text, source_url):
    """Render Markdown as safe HTML, preserving relative links to the repository."""
    rendered = markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc', 'sane_lists', ResolveLinksExtension(source_url)])
    return bleach.clean(
        rendered,
        tags={'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
              'strong', 'em', 'code', 'pre', 'blockquote', 'hr', 'br', 'table',
              'thead', 'tbody', 'tr', 'th', 'td', 'del'},
        attributes={'a': ['href', 'title'], 'h1': ['id'], 'h2': ['id'],
                    'h3': ['id'], 'h4': ['id'], 'h5': ['id'], 'h6': ['id'],
                    'code': ['class']},
        protocols={'http', 'https', 'mailto'},
        strip=True,
    )


def build():
    repository = os.environ.get('GITHUB_REPOSITORY', 'khanhlegood3/gemini-managed-agents-templates')
    server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com').rstrip('/')
    repo_url = f'{server}/{repository}'
    source = f'{repo_url}/tree/main'
    catalog_template = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
    detail_template = (ROOT / 'site' / 'template.html').read_text(encoding='utf-8')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    cards = []
    for path in sorted(ROOT.glob('*/agent.yaml')):
        config = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not isinstance(config, dict):
            raise ValueError(f'{path}: expected a mapping')
        directory = path.parent.name
        slug = quote(directory, safe='')
        title = directory.replace('-', ' ').title()
        description = config.get('description', 'Agent template')
        examples = config.get('examples', [])
        titles = ''.join(f'<li>{escape(item["title"])}</li>' for item in examples)
        cards.append(f'''<article class="card"><p class="eyebrow">AGENT TEMPLATE</p>
<h2>{escape(title)}</h2><p>{escape(description)}</p>
<h3>Example prompts</h3><ul>{titles}</ul>
<a href="templates/{slug}/">Explore template <span aria-hidden="true">→</span></a></article>''')

        prompts = ''.join(f'<article class="prompt-card"><h3>{escape(item["title"])}</h3><p>{escape(item["prompt"])}</p></article>' for item in examples)
        if not prompts:
            prompts = '<p class="muted">No example prompts are available for this template.</p>'
        readme = path.parent / 'README.md'
        if readme.is_file():
            readme_base = f'{repo_url}/blob/main/{slug}/'
            documentation = render_readme(readme.read_text(encoding='utf-8'), readme_base)
        else:
            documentation = '<h2>About this template</h2><p>This template does not include a README yet. Explore the example prompts and configuration above to learn what it can do.</p>'
        tools = config.get('tools', []) or []
        tool_names = [item.get('type') for item in tools if isinstance(item, dict) and item.get('type')]
        tool_list = ''.join(f'<span class="pill">{escape(name.replace("_", " "))}</span>' for name in tool_names) or '<span class="muted">Not specified</span>'
        replacements = {
            '<!-- TITLE -->': escape(title),
            '<!-- DESCRIPTION -->': escape(description),
            '<!-- REPOSITORY_URL -->': escape(repo_url),
            '<!-- SOURCE_URL -->': escape(f'{source}/{slug}'),
            '<!-- AGENT -->': escape(config.get('base_agent', 'Not specified')),
            '<!-- TOOLS -->': tool_list,
            '<!-- PROMPTS -->': prompts,
            '<!-- DOCUMENTATION -->': documentation,
        }
        detail = re.sub(r'<!-- (?:TITLE|DESCRIPTION|REPOSITORY_URL|SOURCE_URL|AGENT|TOOLS|PROMPTS|DOCUMENTATION) -->', lambda match: replacements[match.group()], detail_template)
        detail_dir = OUTPUT / 'templates' / directory
        detail_dir.mkdir(parents=True, exist_ok=True)
        (detail_dir / 'index.html').write_text(detail, encoding='utf-8')

    if not cards:
        raise ValueError('No agent templates found')
    (OUTPUT / 'index.html').write_text(catalog_template.replace('<!-- TEMPLATE_CARDS -->', '\n'.join(cards)).replace('<!-- REPOSITORY_URL -->', escape(repo_url)), encoding='utf-8')
    (OUTPUT / 'style.css').write_text((ROOT / 'site' / 'style.css').read_text(encoding='utf-8'), encoding='utf-8')
    print(f'Built {len(cards)} template pages and catalog in {OUTPUT}')


if __name__ == '__main__':
    build()
