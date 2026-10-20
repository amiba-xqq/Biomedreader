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
    document.querySelector('.search-result').textContent = term ? `找到 ${visible} 个相关章节` : '共 14 个章节，可搜索关键词或按目录跳转';
    document.querySelector('.empty-search').hidden = visible > 0;
  };
  search.addEventListener('input', applySearch);
  search.addEventListener('keydown', event => { if (event.key === 'Escape') { search.value = ''; applySearch(); } });
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
  // Public release metadata only. No GitHub token or visitor account is needed.
  // Embedded release snapshots keep working if GitHub's metadata API is limited.
  const repos = {windows:'amiba-xqq/Biomedreader',macos:'amiba-xqq/Biomedreader_macos'};
  const map = {windows:/^BiomedReader_Setup_.*_x64\.exe$/,portable:/^BiomedReader_.*_Portable_x64\.zip$/,apple:/^BiomedReader_.*_AppleSilicon\.dmg$/,intel:/^BiomedReader_.*_Intel\.dmg$/};
  async function updateRelease(platform) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6500);
    try {
      const response = await fetch(`https://api.github.com/repos/${repos[platform]}/releases/latest`, {signal:controller.signal,headers:{Accept:'application/vnd.github+json'}});
      if (!response.ok) throw new Error('Release metadata unavailable');
      const data = await response.json();
      if (data.draft || data.prerelease || !Array.isArray(data.assets) || !data.html_url?.startsWith(`https://github.com/${repos[platform]}/releases/`)) throw new Error('Invalid release');
      for (const [key, regex] of Object.entries(map)) {
        if ((platform === 'windows') !== ['windows','portable'].includes(key)) continue;
        const asset = data.assets.find(asset => regex.test(asset.name) && asset.state === 'uploaded');
        if (!asset || !asset.browser_download_url?.startsWith(`https://github.com/${repos[platform]}/releases/download/`)) continue;
        document.querySelectorAll(`[data-download="${key}"]`).forEach(link => { link.href = asset.browser_download_url; });
        const box = document.querySelector(`[data-package="${key}"]`);
        if (box) {
          box.querySelector('[data-version]').textContent = data.tag_name.replace(/^v/,'');
          box.querySelector('[data-size]').textContent = `${(asset.size / 1048576).toFixed(1)} MB`;
          const hash = box.querySelector('.hash');
          const validHash = /^sha256:[a-f0-9]{64}$/.test(asset.digest ?? '');
          box.querySelector('.integrity').hidden = !validHash;
          if (validHash) hash.textContent = asset.digest.slice(7);
        }
      }
      document.querySelectorAll(`[data-release="${platform}"]`).forEach(link => { link.href = data.html_url; });
      return true;
    } catch { return false; } finally { clearTimeout(timeout); }
  }
  Promise.all([updateRelease('windows'),updateRelease('macos')]).then(results => {
    document.querySelector('.release-status').textContent = results.every(Boolean)
      ? '已核对 GitHub 最新发布信息'
      : '显示已验证的 2.0 下载，最新信息请查看 GitHub';
  });
}
