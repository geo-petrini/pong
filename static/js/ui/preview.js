
export function setupPreview(scene, x = 500, y = 80) {
  scene.preview = scene.add.graphics();
  scene.redrawPreview = () => drawPreview(scene, x, y);
  drawPreview(scene);
}

function drawPreview(scene, x = 500, y = 80) {
  const g = scene.preview;
  g.clear();

  const bx = x, by = y, bw = 320, bh = 200;
  g.lineStyle(2, 0xffffff).strokeRect(bx, by, bw, bh);

  const scaleX = bw / Math.max(scene.localCfg.width, 1);
  const scaleY = bh / Math.max(scene.localCfg.height, 1);

  const pw = scene.localCfg.paddleWidth * scaleX;
  const ph = scene.localCfg.paddleHeight * scaleY;

  g.fillStyle(0x00ffcc);
  g.fillRect(bx + 20, by + (bh - ph) / 2, pw, ph);
  g.fillRect(bx + bw - pw - 20, by + (bh - ph) / 2, pw, ph);

  const bs = scene.localCfg.ballSize;
  g.fillStyle(0xffcc00);
  g.fillRect(
    bx + (bw - bs * scaleX) / 2,
    by + (bh - bs * scaleY) / 2,
    bs * scaleX,
    bs * scaleY
  );

  scene.add.text(bx, by - 20, 'Anteprima configurazione', { fontSize: 14, color: '#fff' });
}
