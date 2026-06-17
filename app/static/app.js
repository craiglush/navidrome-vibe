const form = document.getElementById('vibe-form');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const goBtn = document.getElementById('go');

function renderResult(data) {
  resultEl.replaceChildren();

  const h2 = document.createElement('h2');
  h2.textContent = data.playlist_name;

  const meta = document.createElement('div');
  meta.textContent = `${data.track_count} tracks · ${data.reasoning || ''}`;

  resultEl.append(h2, meta);

  const tracks = data.tracks || [];
  if (tracks.length) {
    const ul = document.createElement('ul');
    for (const t of tracks) {
      const li = document.createElement('li');
      li.textContent = `${t.title} — ${t.artist}`;
      ul.appendChild(li);
    }
    resultEl.appendChild(ul);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  const count = parseInt(document.getElementById('count').value, 10) || 30;
  if (!prompt) return;

  goBtn.disabled = true;
  resultEl.hidden = true;
  statusEl.hidden = false;
  statusEl.classList.remove('error');
  statusEl.textContent = 'Thinking about your vibe…';

  try {
    const resp = await fetch('/api/vibe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, count }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Request failed');

    statusEl.hidden = true;
    resultEl.hidden = false;
    renderResult(data);
  } catch (err) {
    statusEl.classList.add('error');
    statusEl.textContent = err.message;
  } finally {
    goBtn.disabled = false;
  }
});
