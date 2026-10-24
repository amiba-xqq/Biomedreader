"""Validate the actual Jekyll output before it is deployed to GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = '/Biomedreader'
expected_quark = {
    'windows': 'https://pan.quark.cn/s/9e03e03670b9',
    'portable': 'https://pan.quark.cn/s/bc814f34d962',
    'apple': 'https://pan.quark.cn/s/4e3b4b69e8a7',
    'intel': 'https://pan.quark.cn/s/7e133dd9b236',
}
expected_legacy_quark = dict(windows='https://pan.quark.cn/s/d7308ecd7a92',portable='https://pan.quark.cn/s/3ad56e327034',apple='https://pan.quark.cn/s/31867e2dc3e0',intel='https://pan.quark.cn/s/4130cba6f1d1')
filenames = dict(windows='BiomedReader_Setup_2.1_x64.exe',portable='BiomedReader_2.1_Portable_x64.zip',apple='BiomedReader_2.1_macOS12_AppleSilicon.dmg',intel='BiomedReader_2.1_macOS12_Intel.dmg')
expected_hashes = dict(windows='df57e6b6cdffdec06090bafb23f1232ab7fa6e76951c7ebf26d1c48d8621a023',portable='f63e3a9111efaca993e8d80451460d6cad288957a320510acda8a2481d272ad8',apple='860e1a11eb9c67c08514998d19620a68355a38e3efea724f0bc846bc8b0acce7',intel='b5ed1ad4c2ffcd0dd2315d364304b4d05abfb2016fd48a46d08326d579d34a23')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1s = 0
        self.quark = {}
        self.github = {}
        self.legacy_quark = {}
        self.legacy_github = {}
        self.hashes = {}
        self.hash_key = None
        self.chapters = []
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
        if values.get('data-legacy-quark'):
            self.legacy_quark[values['data-legacy-quark']] = values['href']
        if values.get('data-legacy-download'):
            self.legacy_github[values['data-legacy-download']] = values['href']
        if values.get('data-asset-hash'):
            self.hash_key = values['data-asset-hash']
            self.hashes[self.hash_key] = ''
        if tag == 'section' and values.get('class') == 'chapter':
            self.chapters.append(values['id'])

    def handle_endtag(self, tag):
        if tag == 'p': self.hash_key = None

    def handle_data(self, data):
        if self.hash_key: self.hashes[self.hash_key] += data.strip()


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
assert pages['downloads.html'].legacy_quark == expected_legacy_quark
for key,filename in filenames.items():
    repo = 'Biomedreader' if key in ('windows','portable') else 'Biomedreader_macos'
    prefix = 'https://github.com/amiba-xqq/' + repo + '/releases/download/'
    assert pages['downloads.html'].github[key] == prefix+'v2.1/'+filename
    assert pages['downloads.html'].legacy_github[key] == prefix+'v2.0/'+filename.replace('2.1','2.0')
assert pages['downloads.html'].hashes == expected_hashes
chapters = {'install', 'start', 'keywords', 'filters', 'ranking', 'refresh', 'browser',
            'views', 'hidden', 'details', 'favorites', 'journals', 'sharing', 'faq',
            'citations','batch-pdf','word-plugin','endnote-macos'}
assert chapters <= pages['guide.html'].ids
assert set(pages['guide.html'].chapters) == chapters
assert len(pages['guide.html'].chapters) == 18
assert 'batch-refresh' in pages['guide.html'].ids
sitemap = ET.parse(root / 'sitemap.xml')
locations = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == 3
assert all(link.startswith('https://amiba-xqq.github.io/Biomedreader/') for link in locations)
assert 'Sitemap: https://amiba-xqq.github.io/Biomedreader/sitemap.xml' in (root / 'robots.txt').read_text()
print('PASS: Jekyll rendered 3 pages, 18 chapters, all local links/assets/anchors, sitemap, 8 exact Quark links, 8 version-specific GitHub downloads and 4 SHA256 values.')
