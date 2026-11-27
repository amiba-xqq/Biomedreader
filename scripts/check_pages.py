"""Validate the actual Jekyll output before it is deployed to GitHub Pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site')
base = '/Biomedreader'
version = '2.3.0'
history_versions = ('2.2.3', '2.1', '2.0')
expected_quark = {'windows': 'https://pan.quark.cn/s/8aea04fdb365',
 'portable': 'https://pan.quark.cn/s/d74d615a6e02',
 'apple': 'https://pan.quark.cn/s/843f4c05f924',
 'intel': 'https://pan.quark.cn/s/e655eea55bb2'}
filenames = {'windows': 'BiomedReader_Setup_2.3.0_x64.exe',
 'portable': 'BiomedReader_2.3.0_Portable_x64.zip',
 'apple': 'BiomedReader_2.3.0_macOS12_AppleSilicon.dmg',
 'intel': 'BiomedReader_2.3.0_macOS12_Intel.dmg'}
expected_hashes = {'windows': '767da179a6973fafb18808359a83a2d9b4f988bbf232cb5f487953a1fe21bb9c',
 'portable': '2ba836341679a17bbad6be48595b74ffb653367a75cff21186abd197c037acfa',
 'apple': '2bb0eaafd8f906d434a11109217137df032767d686083ed00696a13e93cec442',
 'intel': '3ad069b03dc842ca98ae4d0af20226035ec0c8b8543da1581fe5035954d10960'}
expected_sizes = {'windows': 199996767,
 'portable': 305095987,
 'apple': 453301115,
 'intel': 528603377}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1s = 0
        self.quark = {}
        self.github = {}
        self.history = {}
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
        if values.get('data-history-version'):
            key = values['data-history-version'],values['data-history-package']
            assert key not in self.history, key
            self.history[key] = values['href']
        if values.get('data-asset-hash'):
            self.hash_key = values['data-asset-hash']
            self.hashes[self.hash_key] = ''
        if tag == 'section' and 'chapter' in values.get('class', '').split():
            self.chapter = values['id']
            self.chapters.append(self.chapter)
            self.lesson_images[self.chapter] = []
        if tag == 'img' and self.chapter:
            assert values['src'].startswith(tuple(base + '/assets/guide-' + v + '/' for v in ('222','223','230')))
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
assert sorted(link for link in pages['downloads.html'].links if urlsplit(link).netloc=='pan.quark.cn') == sorted(expected_quark.values())
assert set(pages['downloads.html'].history) == {(v,key) for v in history_versions for key in filenames}
for key,filename in filenames.items():
    repo = 'Biomedreader' if key in ('windows','portable') else 'Biomedreader_macos'
    prefix = 'https://github.com/amiba-xqq/' + repo + '/releases/download/'
    assert pages['downloads.html'].github[key] == prefix+f'v{version}/'+filename
    for old in history_versions:
        assert pages['downloads.html'].history[old,key] == prefix+f'v{old}/'+filename.replace(version,old)
assert pages['downloads.html'].hashes == expected_hashes
chapters = {'install', 'start', 'keywords', 'filters', 'ranking', 'refresh', 'browser',
            'views', 'hidden', 'details', 'favorites', 'journals', 'sharing', 'faq',
            'citations','batch-pdf','word-plugin','endnote-macos','favorite-search','bulk-unfavorite','software-update',
            'ai-deploy','ai-literature','research-assistant','scientific-questions','ai-reviewer','ai-find-articles','ai-figures','figures-images','figures-if','figures-data','figures-excel','ai-protocol','feedback'}
ddrimage_chapters = ('ddrimage', 'ddrimage-export', 'ddrimage-foci', 'ddrimage-intensity', 'ddrimage-fiber', 'ddrimage-colony', 'ddrimage-plot')
chapters.update(ddrimage_chapters)
skin_chapters = ('skins','skin-local','skin-ai','skin-packs')
chapters.update(skin_chapters)
assert chapters <= pages['guide.html'].ids
assert set(pages['guide.html'].chapters) == chapters
assert len(pages['guide.html'].chapters) == 45
guide = pages['guide.html']
assert all(guide.lesson_images.values()), {key for key, images in guide.lesson_images.items() if not images}
assert len(guide.lesson_images['ai-deploy']) == 11
assert any(src.endswith('/finder-result.webp') for src in guide.lesson_images['ai-find-articles'])
assert sum(map(len, guide.lesson_images.values())) == 86
assert all(any('/guide-223/' in src for src in guide.lesson_images[chapter]) for chapter in ddrimage_chapters)
assert all(any('/guide-230/' in src for src in guide.lesson_images[chapter]) for chapter in (*skin_chapters,'favorites'))
assert base + '/guide.html#ddrimage' in pages['index.html'].links
guide_text = (root / 'guide.html').read_text(encoding='utf8')
assert '布尔表达式只适用于 PubMed' in guide_text and 'Biomni' not in guide_text
assert '默认 · biomedreader.cn' in guide_text and '备用入口 · workers.dev' in guide_text
assert guide_text.count('操作后核对：') == 39
assert {'lab-access', 'lab-management', 'finder-results'} <= guide.ids
assert 'batch-refresh' in pages['guide.html'].ids
sitemap = ET.parse(root / 'sitemap.xml')
locations = [node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locations) == 4
assert all(link.startswith('https://amiba-xqq.github.io/Biomedreader/') for link in locations)
assert 'Sitemap: https://amiba-xqq.github.io/Biomedreader/sitemap.xml' in (root / 'robots.txt').read_text()
print('PASS: Jekyll rendered 4 pages, 45 illustrated chapters, all local links/assets/anchors, sitemap, 4 Quark links, 16 GitHub downloads and 4 SHA256 values.')

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
