const cards = [...document.querySelectorAll('.record-card')];
const status = document.querySelector('#room-status');
const requested = new URLSearchParams(location.search).get('track');
let active = null;
function setFace(card, flipped) {
  card.classList.toggle('is-flipped', flipped);
  const front = card.querySelector('.sleeve');
  const back = card.querySelector('.player-face');
  front.inert = flipped;
  front.setAttribute('aria-expanded', String(flipped));
  front.setAttribute('aria-hidden', String(flipped));
  back.inert = !flipped;
  back.setAttribute('aria-hidden', String(!flipped));
}
function showMessage(card, text) { card.querySelector('.player-message').textContent = text; }
function start(card) {
  for (const other of cards) {
    if (other === card) continue;
    other.querySelector('video').pause();
    setFace(other, false);
  }
  active = card;
  cards.forEach(c => c.classList.remove('is-selected'));
  setFace(card, true);
  const video = card.querySelector('video');
  video.muted = false;
  card.querySelector('.retry').hidden = true;
  showMessage(card, 'Dropping the needle…');
  // Start playback in the click event, before the flip finishes, to preserve browser user activation.
  const play = video.play();
  card.querySelector('.close-player').focus({preventScroll:true});
  if (play) play.catch(() => {
    if (active !== card || !card.classList.contains('is-flipped')) return;
    showMessage(card, 'Press play to start the track.');
    card.querySelector('.retry').hidden = false;
    status.textContent = 'READY WHEN YOU ARE.';
  });
  history.replaceState(null, '', '?track=' + encodeURIComponent(card.dataset.track));
}
for (const card of cards) {
  const video = card.querySelector('video');
  card.querySelector('.sleeve').addEventListener('click', () => start(card));
  card.querySelector('.retry').addEventListener('click', () => start(card));
  card.querySelector('.close-player').addEventListener('click', () => {
    video.pause(); setFace(card, false); active = null;
    status.textContent = 'THE AUX IS YOURS.';
    card.querySelector('.sleeve').focus({preventScroll:true});
  });
  video.addEventListener('play', () => {
    for (const other of cards) if (other !== card) other.querySelector('video').pause();
    active = card; card.classList.add('is-playing');
    card.querySelector('.retry').hidden = true;
    showMessage(card, 'Now playing. Stay a while.');
    status.textContent = 'ON THE AUX: ' + card.querySelector('h2').textContent.toUpperCase();
  });
  video.addEventListener('pause', () => {
    card.classList.remove('is-playing');
    showMessage(card, 'Paused. Your place is saved.');
    if (active === card) status.textContent = 'PAUSED / ' + card.querySelector('h2').textContent.toUpperCase();
  });
  video.addEventListener('ended', () => {
    showMessage(card, 'One more time?');
    if (active === card) status.textContent = 'THAT WAS A GOOD ONE.';
  });
  video.addEventListener('error', () => {
    showMessage(card, 'Couldn’t load this track. Try again.');
    card.querySelector('.retry').hidden = false;
  });
}
const selection = cards.find(c => c.dataset.track === requested);
if (selection) {
  selection.classList.add('is-selected');
  status.textContent = 'QUEUED: ' + selection.querySelector('h2').textContent.toUpperCase();
  if (matchMedia('(max-width: 700px)').matches) selection.scrollIntoView({block:'center'});
}
