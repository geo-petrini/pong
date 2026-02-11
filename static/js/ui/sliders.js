
export function createSlider(scene, x, y, label, key, min, max) {
  scene.add.text(x, y, label, { fontSize: 16, color: '#fff' });

  const initial = scene.localCfg[key];
  const valueNorm = (initial - min) / (max - min);

  const slider = scene.rexUI.add.slider({
    x: x + 290,
    y: y + 5,
    width: 200,
    height: 20,
    orientation: 0,
    track: scene.rexUI.add.roundRectangle(0, 0, 0, 0, 10, scene.COLOR_DARK),
    thumb: scene.rexUI.add.roundRectangle(0, 0, 0, 0, 10, 0xffffff),
    value: valueNorm
  }).layout();

  const valueText = scene.add.text(x + 430, y, String(initial), { fontSize: 16, color: '#fff' });

  slider.on('valuechange', (value) => {
    const real = Math.round(min + value * (max - min));
    scene.localCfg[key] = real;
    valueText.setText(String(real));
    scene.redrawPreview();
  });
}
