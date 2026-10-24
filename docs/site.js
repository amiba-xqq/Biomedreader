const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => {
  const open = document.querySelector('.nav').classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
  menu.textContent = open ? '关闭菜单' : '菜单';
});
document.querySelectorAll('.zoom-image').forEach(button => button.addEventListener('click', () => {
  const modal = document.querySelector('#image-lightbox');
  const img = button.querySelector('img');
  modal.querySelector('img').src = img.src;
  modal.querySelector('img').alt = img.alt;
  modal.showModal();
}));
const modal = document.querySelector('#image-lightbox');
modal?.querySelector('.lightbox-close').addEventListener('click', () => modal.close());
modal?.addEventListener('click', event => { if (event.target === modal) modal.close(); });

const search = document.querySelector('#guide-search');
if (search) {
  const chapters = [...document.querySelectorAll('.chapter')];
  const toc = [...document.querySelectorAll('.toc a')];
  const applySearch = () => {
    const term = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    chapters.forEach(chapter => {
      const match = !term || chapter.textContent.toLocaleLowerCase().includes(term);
      chapter.hidden = !match;
      const link = toc.find(link => link.hash === '#' + chapter.id);
      if (link) link.hidden = !match;
      if (match) visible++;
    });
    document.querySelector('.search-result').textContent = term ? `找到 ${visible} 个相关章节` : `共 ${chapters.length} 个章节，可搜索关键词或按目录跳转`;
    document.querySelector('.empty-search').hidden = visible > 0;
  };
  search.addEventListener('input', applySearch);
  search.addEventListener('keydown', event => { if (event.key === 'Escape') { search.value = ''; applySearch(); } });
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => {
    const chapter = document.getElementById(decodeURIComponent(link.hash.slice(1)))?.closest('.chapter');
    if (chapter?.hidden) { search.value = ''; applySearch(); }
  }));
  applySearch();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) {
      toc.forEach(link => link.classList.toggle('active', link.hash === '#' + entry.target.id));
    }});
  }, {rootMargin: '-110px 0px -60% 0px', threshold: 0});
  chapters.forEach(chapter => observer.observe(chapter));
}

function toast(message) {
  let element = document.querySelector('.toast');
  if (!element) { element = document.createElement('div'); element.className = 'toast'; element.role = 'status'; document.body.append(element); }
  element.textContent = message; element.hidden = false;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => { element.hidden = true; }, 2500);
}
document.querySelectorAll('[data-copy-hash]').forEach(button => button.addEventListener('click', async () => {
  const code = button.closest('.integrity').querySelector('.hash');
  try { await navigator.clipboard.writeText(code.textContent.trim()); toast('已复制 SHA256 校验值'); }
  catch { const range = document.createRange(); range.selectNodeContents(code); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); toast('请复制已选中的校验值'); }
}));

if (document.body.dataset.page === 'downloads') {
  const system = navigator.platform.toLowerCase();
  const card = system.includes('win') ? document.querySelector('[data-package="windows"]') : null;
  if (card) { card.classList.add('recommended'); card.querySelector('.recommendation').hidden = false; }
  // Pin both channels to 2.1. The historical 2.0 links use separate attributes.
  // Public metadata only; embedded links remain usable if GitHub limits its API.
  const version = document.querySelector('[data-current-version]').dataset.currentVersion;
  const repos = {windows:'amiba-xqq/Biomedreader',macos:'amiba-xqq/Biomedreader_macos'};
  const map = {windows:`BiomedReader_Setup_${version}_x64.exe`,portable:`BiomedReader_${version}_Portable_x64.zip`,apple:`BiomedReader_${version}_macOS12_AppleSilicon.dmg`,intel:`BiomedReader_${version}_macOS12_Intel.dmg`};
  async function updateRelease(platform) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6500);
    try {
      const response = await fetch(`https://api.github.com/repos/${repos[platform]}/releases/tags/v${version}`, {signal:controller.signal,headers:{Accept:'application/vnd.github+json'}});
      if (!response.ok) throw new Error('Release metadata unavailable');
      const data = await response.json();
      if (data.draft || data.prerelease || data.tag_name !== `v${version}` || !Array.isArray(data.assets) || data.html_url !== `https://github.com/${repos[platform]}/releases/tag/v${version}`) throw new Error('Invalid release');
      for (const [key, filename] of Object.entries(map)) {
        if ((platform === 'windows') !== ['windows','portable'].includes(key)) continue;
        const asset = data.assets.find(asset => asset.name === filename && asset.state === 'uploaded');
        if (!asset || asset.browser_download_url !== `https://github.com/${repos[platform]}/releases/download/v${version}/${filename}`) throw new Error('Missing expected package');
        document.querySelectorAll(`[data-download="${key}"]`).forEach(link => { link.href = asset.browser_download_url; });
        document.querySelectorAll(`[data-asset-size="${key}"]`).forEach(label => { label.textContent = `${(asset.size / 1000000).toFixed(1)} MB`; });
        const box = document.querySelector(`[data-package="${key}"]`);
        if (box) box.querySelector('[data-version]').textContent = version;
        if (/^sha256:[a-f0-9]{64}$/.test(asset.digest ?? '')) {
          document.querySelectorAll(`[data-asset-hash="${key}"]`).forEach(hash => { hash.textContent = asset.digest.slice(7); });
        }
      }
      document.querySelectorAll(`[data-release="${platform}"]`).forEach(link => { link.href = data.html_url; });
      return true;
    } catch { return false; } finally { clearTimeout(timeout); }
  }
  Promise.all([updateRelease('windows'),updateRelease('macos')]).then(results => {
    document.querySelector('.release-status').textContent = results.every(Boolean)
      ? `已核对 GitHub ${version} 发布信息`
      : `显示已核对的 ${version} 下载快照，发布详情请查看 GitHub`;
  });
}
