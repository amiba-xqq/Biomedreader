(() => {
  const film = document.querySelector('#product-film');
  const video = film.querySelector('video');
  const cover = film.querySelector('.film-cover');
  const chapters = film.querySelector('.film-chapters');
  const error = film.querySelector('.film-error');
  let target = null;
  function seek() {
    if (target !== null && video.readyState >= 1) {
      video.currentTime = target;
      target = null;
    }
  }
  function start(at) {
    target = at;
    cover.hidden = true;
    error.hidden = true;
    seek();
    video.play().catch(e => { if (e.name !== 'AbortError') error.hidden = false; });
  }
  video.addEventListener('loadedmetadata', seek);
  video.addEventListener('error', () => { error.hidden = false; });
  cover.addEventListener('click', () => { start(null); video.focus(); });
  chapters.addEventListener('click', e => {
    const button = e.target.closest('[data-at]');
    if (button) start(Number(button.dataset.at));
  });
  cover.hidden = false;
  chapters.hidden = false;
})();
