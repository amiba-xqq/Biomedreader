(() => {
  const video = document.querySelector('#tutorial-film');
  const buttons = [...document.querySelectorAll('.film-index button')];
  const start = document.querySelector('#film-start');
  const error = document.querySelector('#film-error');
  let current = -1;
  const status = document.querySelector('#film-status');
  let pending = null;
  let timer = 0;
  function showChapter(i) {
    if (i === current) return;
    if (current >= 0) buttons[current].removeAttribute('aria-current');
    current = i;
    const button = buttons[i];
    button.setAttribute('aria-current', 'true');
    document.querySelector('#film-number').textContent = button.querySelector('.film-num').textContent + ' / 13';
    document.querySelector('#film-title').textContent = button.querySelector('.film-name').textContent;
    const list = button.closest('ol');
    const gap = button.getBoundingClientRect().top - list.getBoundingClientRect().top;
    if (gap < 0 || gap + button.offsetHeight > list.clientHeight) list.scrollTop += gap - list.clientHeight / 2 + button.offsetHeight / 2;
  }
  function play() {
    video.play().catch(e => { if (e.name === 'NotSupportedError') error.hidden = false; });
  }
  start.hidden = false;
  start.addEventListener('click', play);
  video.addEventListener('play', () => { start.hidden = true; });
  const fail = () => { clearTimeout(timer); pending = null; status.textContent = ''; error.hidden = false; start.hidden = true; };
  video.addEventListener('error', fail);
  video.querySelector('source').addEventListener('error', fail);
  function seek() {
    timer = 0;
    if (pending === null || video.readyState < 1) return;
    video.currentTime = pending;
    pending = null;
  }
  buttons.forEach((button, index) => button.addEventListener('click', () => {
    clearTimeout(timer);
    pending = Number(button.dataset.start);
    showChapter(index);
    status.textContent = '正在定位…';
    timer = setTimeout(seek, 100);
    play();
  }));
  video.addEventListener('loadedmetadata', () => { if (!timer) seek(); });
  function updateChapter() {
    if (pending !== null || video.seeking) return;
    status.textContent = '';
    showChapter(buttons.reduce((found, button, index) =>
      video.currentTime + 0.001 >= Number(button.dataset.start) ? index : found, 0));
  }
  ['timeupdate', 'playing', 'seeked'].forEach(event => video.addEventListener(event, updateChapter));
  updateChapter();
})();
