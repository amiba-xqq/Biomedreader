const modal = document.querySelector('#image-lightbox');
if (modal && typeof modal.showModal === 'function') {
  const preview = modal.querySelector('img');
  let opener;
  document.querySelectorAll('[data-guide-zoom]').forEach(link => link.addEventListener('click', event => {
    if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    preview.src = link.href;
    preview.alt = link.querySelector('img').alt;
    modal.showModal();
  }));
  modal.querySelector('.lightbox-close').addEventListener('click', () => modal.close());
  modal.addEventListener('click', event => { if (event.target === modal) modal.close(); });
  modal.addEventListener('close', () => { preview.removeAttribute('src'); opener?.focus(); });
}
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
  const contents = document.querySelector('.toc');
  const desktop = window.matchMedia('(min-width: 771px)');
  const rail = document.querySelector('.chapter-rail');
  let current, scheduled = false;
  const updateCurrent = () => {
    scheduled = false;
    let section;
    for (const chapter of chapters) {
      if (chapter.hidden) continue;
      if (!section || chapter.getBoundingClientRect().top <= 140) section = chapter;
      else break;
    }
    if (current === section) return;
    current = section;
    const selected = section && toc.find(link => link.hash === '#' + section.id);
    toc.forEach(link => {
      if (link === selected) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (rail) {
      const title = rail.querySelector('[data-current-chapter]');
      title.textContent = selected?.textContent.trim() || '未找到匹配章节';
      const visible = toc.filter(link => !link.hidden);
      const index = visible.indexOf(selected);
      for (const [name, next] of [['previous', index > 0 ? visible[index - 1] : null], ['next', index >= 0 ? visible[index + 1] : null]]) {
        const link = rail.querySelector('[data-step="' + name + '"]');
        link.hidden = !next;
        if (next) {
          link.href = next.hash;
          link.setAttribute('aria-label', (name === 'previous' ? '上一节：' : '下一节：') + next.textContent.trim());
        }
      }
    }
    if (selected && desktop.matches) {
      const linkBox = selected.getBoundingClientRect();
      const listBox = contents.getBoundingClientRect();
      if (linkBox.top < listBox.top) contents.scrollTop -= listBox.top - linkBox.top + 6;
      else if (linkBox.bottom > listBox.bottom) contents.scrollTop += linkBox.bottom - listBox.bottom + 6;
    }
  };
  const queueChapter = () => {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(updateCurrent);
    }
  };
  window.addEventListener('scroll', queueChapter, {passive:true});
  window.addEventListener('resize', queueChapter, {passive:true});
  window.addEventListener('hashchange', queueChapter);
  function updateAfterFilter() { current = null; queueChapter(); }
  search.addEventListener('input', updateAfterFilter);
  search.addEventListener('keydown', updateAfterFilter);
  queueChapter();
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

if (typeof IntersectionObserver === 'function' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const reveal = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('reveal-in');
      reveal.unobserve(entry.target);
    }
  }, {rootMargin: '0px 0px -10px 0px', threshold: 0.08});
  document.querySelectorAll('.course, .package, .version-grid article, .guide-figure, .audience-grid, .cta-band').forEach(element => reveal.observe(element));
}