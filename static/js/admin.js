
async function load() {
  const res = await fetch('/config');
  return await res.json();
}

function createSlider(label, key, value, min=1, max=2000) {
  const container = document.createElement('div');
  container.className = 'mt-3';
  const lbl = document.createElement('label'); lbl.className = 'form-label'; lbl.textContent = label;
  const input = document.createElement('input'); input.type = 'range'; input.className='form-range'; input.min = String(min); input.max = String(max); input.value = String(value);
  const val = document.createElement('span'); val.className = 'ms-2'; val.textContent = String(value);
  input.addEventListener('input', ()=>{ val.textContent = input.value; });
  container.append(lbl, input, val);
  container.dataset.key = key;
  return container;
}

async function init() {
  const cfg = await load();
  const panel = document.querySelector('#config-panel');
  const fields = [
    ['Larghezza paddle', 'PADDLE_WIDHT', 2, 200],
    ['Altezza paddle',   'PADDLE_HEIGHT', 10, 600],
    ['Offset paddle',    'PADDLE_OFFSET', 0, 400],
    ['Velocità paddle',  'PADDLE_VELOCITY', 50, 2000],
    ['Dimensione palla', 'BALL_SIZE', 2, 200],
    ['Velocità palla',   'BALL_VELOCITY', 50, 2000],
    ['Larghezza gioco',  'GAME_WIDTH', 200, 4096],
    ['Altezza gioco',    'GAME_HEIGHT', 200, 4096],
  ];

  fields.forEach(([label, key, min, max]) => {
    const div = createSlider(label, key, cfg[key], min, max);
    panel.appendChild(div);
  });

  document.querySelector('#save').addEventListener('click', async () => {
    const newCfg = {};
    panel.childNodes.forEach(div => {
      const key = div.dataset.key;
      const input = div.querySelector('input');
      newCfg[key] = Number(input.value);
    });

    await fetch('/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newCfg) });
    alert('Configurazione aggiornata.');
  });
}

init();
