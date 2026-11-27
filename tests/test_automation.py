import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site
from probe_response import valid_response


class StaticSiteTests(unittest.TestCase):
    def test_build_escapes_data_and_uses_relative_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'site').mkdir()
            (root / 'site' / 'index.html').write_text('<a href="<!-- REPOSITORY_URL -->">repo</a><!-- TEMPLATE_CARDS -->', encoding='utf-8')
            (root / 'site' / 'style.css').write_text('body{}', encoding='utf-8')
            agent = root / 'test-agent'
            agent.mkdir()
            (agent / 'agent.yaml').write_text('description: "<script>alert(1)</script>"\nexamples:\n  - title: "<Example>"\n    prompt: "test"\n', encoding='utf-8')
            with patch.object(build_site, 'ROOT', root), patch.object(build_site, 'OUTPUT', root / '_site'), patch.dict(os.environ, {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_SERVER_URL': 'https://github.com'}):
                build_site.build()
            page = (root / '_site' / 'index.html').read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;', page)
            self.assertIn('&lt;Example&gt;', page)
            self.assertIn('https://github.com/owner/repo/tree/main/test-agent/agent.yaml', page)
            self.assertNotIn('<script>', page)
            self.assertTrue((root / '_site' / 'style.css').is_file())

    def test_real_catalog_contains_every_template(self):
        build_site.build()
        page = (ROOT / '_site' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(page.count('<article class="card">'), len(list(ROOT.glob('*/agent.yaml'))))
        self.assertIn('href="style.css"', page)
        self.assertNotIn('<!-- TEMPLATE_CARDS -->', page)


class ProbeTests(unittest.TestCase):
    def test_response_validation(self):
        self.assertTrue(valid_response('{"id":"abc"}'))
        self.assertTrue(valid_response('event: interaction\ndata: {"type":"content"}\n\ndata: [DONE]\n'))
        for text in ('', 'not json', '{"error":{"message":"bad"}}', 'data: {"type":"error"}\n', 'data: [DONE]', 'event: error\ndata: {"message":"bad"}'):
            with self.subTest(text=text):
                self.assertFalse(valid_response(text))

    def test_matrix_has_valid_payloads(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'output'
            subprocess.run([sys.executable, str(ROOT / 'scripts' / 'probe_matrix.py')], env={**os.environ, 'GITHUB_OUTPUT': str(output)}, check=True)
            entries = json.loads(output.read_text(encoding='utf-8').removeprefix('matrix='))
            self.assertTrue(entries)
            self.assertTrue(all(entry['template'] and entry['chip'] and entry['prompt'] for entry in entries))


if __name__ == '__main__':
    unittest.main()
