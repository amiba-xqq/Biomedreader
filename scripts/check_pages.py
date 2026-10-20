"""Validate the actual Jekyll output before it is deployed to GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = '/Biomedreader'
expected_quark = {
    'windows': 'https://pan.quark.cn/s/d7308ecd7a92',
    'portable': 'https://pan.quark.cn/s/3ad56e327034',
    'apple': 'https://pan.quark.cn/s/31867e2dc3e0',
    'intel': 'https://pan.quark.cn/s/4130cba6f1d1',
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1s = 0
        self.quark = {}
        self.github = {}
        text = path.read_text(encoding='utf8')
        assert '{{' not in text and '{%' not in text, f'Unrendered Liquid in {path}'
        assert 'chatgpt.site' not in text, f'Old hosting address in {path}'
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            assert values['id'] not in self.ids, 'Duplicate HTML ID'
            self.ids.add(values['id'])
        if tag == 'h1':
            self.h1s += 1
        for key in ('href', 'src'):
            if values.get(key):
                self.links.append(values[key])
        if values.get('data-quark'):
            self.quark[values['data-quark']] = values['href']
        if values.get('data-download'):
            self.github[values['data-download']] = values['href']


pages = {name: Page(root / name) for name in ('index.html', 'downloads.html', 'guide.html')}
for name, page in pages.items():
    assert page.h1s == 1, name
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            continue
        target = unquote(parsed.path)
        if target:
            assert target == base + '/' or target.startswith(base + '/'), (name, link)
            target = target[len(base):].lstrip('/') or 'index.html'
        else:
            target = name
        assert (root / target).is_file(), (name, link)
        if parsed.fragment and target in pages:
            assert unquote(parsed.fragment) in pages[target].ids, (name, link)

assert pages['downloads.html'].quark == expected_quark
assert set(pages['downloads.html'].github) == set(expected_quark)
for link in pages['downloads.html'].github.values():
    assert link.startswith('https://github.com/amiba-xqq/Biomedreader')
    assert '/releases/download/' in link
chapters = {'install', 'start', 'keywords', 'filters', 'ranking', 'refresh', 'browser',
            'views', 'hidden', 'details', 'favorites', 'journals', 'sharing', 'faq'}
assert chapters <= pages['guide.html'].ids
sitemap = ET.parse(root / 'sitemap.xml')
locations = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == 3
assert all(link.startswith('https://amiba-xqq.github.io/Biomedreader/') for link in locations)
assert 'Sitemap: https://amiba-xqq.github.io/Biomedreader/sitemap.xml' in (root / 'robots.txt').read_text()
print('PASS: Jekyll rendered 3 pages, 14 chapters, all local links/assets/anchors, sitemap, 4 exact Quark mappings and 4 GitHub downloads.')
