(() => {
  const video = document.querySelector('#tutorial-film');
  const buttons = [...document.querySelectorAll('.film-index button')];
  const start = document.querySelector('#film-start');
  const error = document.querySelector('#film-error');
  let current = -1;
  function updateChapter() {
    const i = buttons.reduce((found, button, index) =>
      video.currentTime + 0.001 >= Number(button.dataset.start) ? index : found, 0);
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
  const fail = () => { error.hidden = false; start.hidden = true; };
  video.addEventListener('error', fail);
  video.querySelector('source').addEventListener('error', fail);
  buttons.forEach(button => button.addEventListener('click', () => {
    video.currentTime = Number(button.dataset.start);
    updateChapter();
    play();
  }));
  ['loadedmetadata', 'timeupdate', 'seeking', 'seeked'].forEach(event => video.addEventListener(event, updateChapter));
  updateChapter();
})();
