
import { GAME_SETTINGS } from '../gameSettings.js';
import { socket } from '../net/socketClient.js';
import { setupLobbySocketHandlers } from '../net/lobbySocketHandlers.js';
import { createSessionInput } from '../ui/sessionInput.js';
import { createButtons } from '../ui/buttons.js';
import { createSlider } from '../ui/sliders.js';
import { setupPreview } from '../ui/preview.js';

export default class LobbyScene extends Phaser.Scene {
  COLOR_MAIN = 0x505050;
  COLOR_LIGHT = 0x606060;
  COLOR_DARK = 0x707070;

  constructor() { super({ key: 'LobbyScene' }); }

  preload() {
    this.load.scenePlugin(
      {
        key: 'rexuiplugin',
        url: '/static/js/rexuiplugin.min.js',
        sceneKey: 'rexUI'
      }
    );
    this.session_id = '';
  }

  create() {
    createSessionInput(this);

    this.localCfg = { ...GAME_SETTINGS };

    createSlider(this, 20, 310, 'Larghezza paddle', 'paddleWidth', 2, 50);
    createSlider(this, 20, 350, 'Altezza paddle', 'paddleHeight', 10, 600);
    createSlider(this, 20, 390, 'Dimensione palla', 'ballSize', 2, 100);

    createSlider(this, 20, 430, 'Velocità paddle', 'paddleVelocity', 50, 2000);
    createSlider(this, 20, 470, 'Velocità palla', 'ballVelocity', 50, 2000);

    createSlider(this, 20, 510, 'Larghezza schermo', 'width', 200, 4096);
    createSlider(this, 20, 560, 'Altezza schermo', 'height', 200, 4096);

    setupPreview(this, 480, 310);

    const btns = createButtons(this);
    btns.on('button.click', (btn) => {
      const action = btn.getData('action');
      if (!this.session_id) return this.showError('Inserisci un ID sessione.');

      Object.assign(GAME_SETTINGS, this.localCfg);

      if (action === 'create') socket.emit('createSession', { session_id: this.session_id });
      if (action === 'join') socket.emit('joinSession', { session_id: this.session_id });
    });

    setupLobbySocketHandlers(this);
  }

  showError(msg) { alert(msg); }
}
