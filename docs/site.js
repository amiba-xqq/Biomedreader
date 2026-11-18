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
  const directory = document.querySelector('.guide-directory');
  if (directory && window.matchMedia('(max-width: 770px)').matches) directory.open = false;
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
