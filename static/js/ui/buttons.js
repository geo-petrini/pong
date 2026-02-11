
export function createButtons(scene) {
  return scene.rexUI.add.buttons({
    x: 660,
    y: 300,
    orientation: 'y',
    buttons: [ createButton(scene, 'Crea', 'create'), scene.rexUI.add.space(), createButton(scene, 'Connetti', 'join') ]
  }).layout();
}

function createButton(scene, text, action) {
  return scene.rexUI.add.label({
    width: 140,
    height: 30,
    background: scene.rexUI.add.roundRectangle(0, 0, 0, 0, 2, scene.COLOR_MAIN),
    text: scene.add.text(0, 0, text, { fontSize: 18 }),
    align: 'center'
  }).setData('action', action);
}
