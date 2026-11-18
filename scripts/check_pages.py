"""Validate the actual Jekyll output before it is deployed to GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = '/Biomedreader'
version = '2.2.2'
expected_quark = {'windows': 'https://pan.quark.cn/s/083dd1cd8541', 'portable': 'https://pan.quark.cn/s/3c0ada60108b', 'apple': 'https://pan.quark.cn/s/0286e143c7fe', 'intel': 'https://pan.quark.cn/s/c21cc37271b0'}
expected_legacy_quark = {'windows': 'https://pan.quark.cn/s/d7308ecd7a92', 'portable': 'https://pan.quark.cn/s/3ad56e327034', 'apple': 'https://pan.quark.cn/s/31867e2dc3e0', 'intel': 'https://pan.quark.cn/s/4130cba6f1d1'}
filenames = {'windows': 'BiomedReader_Setup_2.2.2_x64.exe', 'portable': 'BiomedReader_2.2.2_Portable_x64.zip', 'apple': 'BiomedReader_2.2.2_macOS12_AppleSilicon.dmg', 'intel': 'BiomedReader_2.2.2_macOS12_Intel.dmg'}
expected_hashes = {'windows': 'b3709404d6193f9ba6c9837c6e1ca10a5b9e41474958e010aa59d1beeaa1daaf', 'portable': 'e60c2c19271bdd8fe3d285f34ca98becc4c447a3b3552b606be140f8cab5917b', 'apple': '44d7aee5f47396458362f036ef2e6d4a21c178002532f41948de6d827ce06b3b', 'intel': 'f0bede9410224059eadc33c752a859710e4be2e3fa03f84a19751cedfb18fe4b'}
expected_sizes = {'windows': 183551905, 'portable': 277781906, 'apple': 393252853, 'intel': 444567002}


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
    assert pages['downloads.html'].github[key] == prefix+f'v{version}/'+filename
    assert pages['downloads.html'].legacy_github[key] == prefix+'v2.0/'+filename.replace(version,'2.0')
assert pages['downloads.html'].hashes == expected_hashes
chapters = {'install', 'start', 'keywords', 'filters', 'ranking', 'refresh', 'browser',
            'views', 'hidden', 'details', 'favorites', 'journals', 'sharing', 'faq',
            'citations','batch-pdf','word-plugin','endnote-macos','favorite-search','bulk-unfavorite','software-update',
            'ai-deploy','ai-literature','research-assistant','ai-figures','figures-images','figures-data','ai-protocol','feedback'}
assert chapters <= pages['guide.html'].ids
assert set(pages['guide.html'].chapters) == chapters
assert len(pages['guide.html'].chapters) == 29
assert 'batch-refresh' in pages['guide.html'].ids
sitemap = ET.parse(root / 'sitemap.xml')
locations = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == 3
assert all(link.startswith('https://amiba-xqq.github.io/Biomedreader/') for link in locations)
assert 'Sitemap: https://amiba-xqq.github.io/Biomedreader/sitemap.xml' in (root / 'robots.txt').read_text()
print('PASS: Jekyll rendered 3 pages, 29 chapters, all local links/assets/anchors, sitemap, 8 exact Quark links, 8 version-specific GitHub downloads and 4 SHA256 values.')

# The desktop updater consumes the same version and hashes as the download page.
import json
update=json.loads((root/'app-update.json').read_text(encoding='utf8'))
assert update['schema']==1 and update['application']=='BiomedReader' and update['version']==version
for label,key in [('windows-x64','windows'),('macos-arm64','apple'),('macos-intel','intel')]:
    package=update['packages'][label]
    assert package['filename']==filenames[key]
    assert package['url']==pages['downloads.html'].github[key]
    assert package['sha256']==expected_hashes[key] and package['bytes']==expected_sizes[key]
print('PASS: desktop update manifest agrees with the published packages.')
