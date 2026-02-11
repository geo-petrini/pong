
export function createSessionInput(scene) {
  scene.add.text(400 - 120, 200, 'ID sessione:', { fontSize: 18, color: '#fff' }).setOrigin(0, 0.5);
  if (!scene.rexUI || !scene.rexUI.add || typeof scene.rexUI.add.textEdit !== 'function') {
    console.warn('rexUI plugin not available on scene:', scene.rexUI);
    // Simple fallback: clickable text that opens prompt for session id
    const fallback = scene.add.text(400, 230, '[Click to enter session id]', { fontSize: 18, color: '#fff' }).setOrigin(0.5);
    fallback.setInteractive({ useHandCursor: true });
    fallback.on('pointerdown', () => {
      const txt = window.prompt('ID sessione:', scene.session_id || '');
      scene.session_id = (txt || '').trim();
      fallback.setText(scene.session_id ? `ID: ${scene.session_id}` : '[Click to enter session id]');
    });
    return;
  }

  try {
    const textObj = scene.add.text(0, 0, '', { fontSize: 18 });
    const input = scene.rexUI.add.textEdit(
      textObj,
      {
        x: 400,
        y: 230,
        width: 260,
        height: 40,
        background: scene.rexUI.add.roundRectangle(0, 0, 0, 0, 2, scene.COLOR_MAIN)
      }
    );

    if (typeof input.layout === 'function') input.layout();

    if (input && typeof input.on === 'function') {
      input.on('textchange', (txt) => {
        scene.session_id = (txt || '').trim();
      });
    } else if (input && input.textEdit && typeof input.textEdit.on === 'function') {
      input.textEdit.on('textchange', (txt) => {
        scene.session_id = (txt || '').trim();
      });
    }
  } catch (err) {
    console.error('Error creating rexUI textEdit:', err, 'scene.rexUI=', scene.rexUI);
    const fallback = scene.add.text(400, 230, '[Click to enter session id]', { fontSize: 18, color: '#fff' }).setOrigin(0.5);
    fallback.setInteractive({ useHandCursor: true });
    fallback.on('pointerdown', () => {
      const txt = window.prompt('ID sessione:', scene.session_id || '');
      scene.session_id = (txt || '').trim();
      fallback.setText(scene.session_id ? `ID: ${scene.session_id}` : '[Click to enter session id]');
    });
  }
}
