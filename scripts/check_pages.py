"""Validate the actual Jekyll output before it is deployed to GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = '/Biomedreader'
version = '2.2.3'
expected_quark = {'windows': 'https://pan.quark.cn/s/d17f3ee2e4e6',
 'portable': 'https://pan.quark.cn/s/4310b353ba48',
 'apple': 'https://pan.quark.cn/s/1c93ba257b68',
 'intel': 'https://pan.quark.cn/s/988a1ed0e995'}
expected_legacy_quark = {'windows': 'https://pan.quark.cn/s/d7308ecd7a92', 'portable': 'https://pan.quark.cn/s/3ad56e327034', 'apple': 'https://pan.quark.cn/s/31867e2dc3e0', 'intel': 'https://pan.quark.cn/s/4130cba6f1d1'}
filenames = {'windows': 'BiomedReader_Setup_2.2.3_x64.exe',
 'portable': 'BiomedReader_2.2.3_Portable_x64.zip',
 'apple': 'BiomedReader_2.2.3_macOS12_AppleSilicon.dmg',
 'intel': 'BiomedReader_2.2.3_macOS12_Intel.dmg'}
expected_hashes = {'windows': 'ae7bf61ff6e31adb28258506d4f0c627bb60f15b92c681ca1383dfe843570db6',
 'portable': 'd59d1d5fc56c2c126d0c48039ae00df1062d4d32a5b50ca89600177e77e5fe3e',
 'apple': 'f6f3a41c4f538eb4d2edb31332f7f17c8c4c2037d1655b18a396cbe294b035ec',
 'intel': '841f3e0c7bc093c6f5bd4ac69f073f79468190a42826a75f4099d7e5be931519'}
expected_sizes = {'windows': 199906924,
 'portable': 305018082,
 'apple': 453507133,
 'intel': 528491421}


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
        self.lesson_images = {}
        self.chapter = None
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
        if tag == 'section' and 'chapter' in values.get('class', '').split():
            self.chapter = values['id']
            self.chapters.append(self.chapter)
            self.lesson_images[self.chapter] = []
        if tag == 'img' and self.chapter:
            assert values['src'].startswith((base + '/assets/guide-222/', base + '/assets/guide-223/'))
            assert values.get('alt') and values.get('loading') == 'lazy'
            assert int(values['width']) > 0 and int(values['height']) > 0
            self.lesson_images[self.chapter].append(values['src'])

    def handle_endtag(self, tag):
        if tag == 'section': self.chapter = None
        if tag == 'p': self.hash_key = None

    def handle_data(self, data):
        if self.hash_key: self.hashes[self.hash_key] += data.strip()


pages = {name: Page(root / name) for name in ('index.html', 'downloads.html', 'guide.html', 'video.html')}
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
            'ai-deploy','ai-literature','research-assistant','scientific-questions','ai-reviewer','ai-find-articles','ai-figures','figures-images','figures-if','figures-data','figures-excel','ai-protocol','feedback'}
ddrimage_chapters = ('ddrimage', 'ddrimage-export', 'ddrimage-foci', 'ddrimage-intensity', 'ddrimage-fiber', 'ddrimage-colony', 'ddrimage-plot')
chapters.update(ddrimage_chapters)
assert chapters <= pages['guide.html'].ids
assert set(pages['guide.html'].chapters) == chapters
assert len(pages['guide.html'].chapters) == 41
guide = pages['guide.html']
assert all(guide.lesson_images.values()), {key for key, images in guide.lesson_images.items() if not images}
assert len(guide.lesson_images['ai-deploy']) == 11
assert any(src.endswith('/finder-result.webp') for src in guide.lesson_images['ai-find-articles'])
assert sum(map(len, guide.lesson_images.values())) == 80
assert all(any('/guide-223/' in src for src in guide.lesson_images[chapter]) for chapter in ddrimage_chapters)
assert base + '/guide.html#ddrimage' in pages['index.html'].links
guide_text = (root / 'guide.html').read_text(encoding='utf8')
assert '布尔表达式只适用于 PubMed' in guide_text and 'Biomni' not in guide_text
assert '默认 · biomedreader.cn' in guide_text and '备用入口 · workers.dev' in guide_text
assert guide_text.count('操作后核对：') == 35
assert {'lab-access', 'lab-management', 'finder-results'} <= guide.ids
assert 'batch-refresh' in pages['guide.html'].ids
sitemap = ET.parse(root / 'sitemap.xml')
locations = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == 4
assert all(link.startswith('https://amiba-xqq.github.io/Biomedreader/') for link in locations)
assert 'Sitemap: https://amiba-xqq.github.io/Biomedreader/sitemap.xml' in (root / 'robots.txt').read_text()
print('PASS: Jekyll rendered 4 pages, 41 illustrated chapters, all local links/assets/anchors, sitemap, 8 exact Quark links, 8 version-specific GitHub downloads and 4 SHA256 values.')

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
