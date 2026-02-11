
import { GAME_SETTINGS } from '../gameSettings.js';
import { setupGameSocketHandlers } from '../net/gameSocketHandlers.js';
import { socket } from '../net/socketClient.js';

export default class GameScene extends Phaser.Scene {
  constructor() { super({ key: 'GameScene' }); }

  init(data) {
    this.sessionId = data.sessionId;
    this.paddleSide = data.paddle;
    this.gameState = {};
  }

  preload() {
    const g = this.add.graphics();
    g.fillStyle(0xffffff);

    g.fillRect(0, 0, GAME_SETTINGS.paddleWidth, GAME_SETTINGS.paddleHeight);
    g.generateTexture('paddle', GAME_SETTINGS.paddleWidth, GAME_SETTINGS.paddleHeight);

    g.clear();
    g.fillRect(0, 0, GAME_SETTINGS.ballSize, GAME_SETTINGS.ballSize);
    g.generateTexture('ball', GAME_SETTINGS.ballSize, GAME_SETTINGS.ballSize);
    g.destroy();
  }

  create() {
    this.scale.resize(GAME_SETTINGS.width, GAME_SETTINGS.height);

    const border = this.add.graphics();
    border.lineStyle(4, 0xffffff).strokeRect(0, 0, this.scale.width, this.scale.height);

    this.paddleLeft = this.physics.add.image(GAME_SETTINGS.paddleOffset, this.scale.height / 2, 'paddle').setImmovable(true);
    this.paddleRight = this.physics.add.image(this.scale.width - GAME_SETTINGS.paddleOffset, this.scale.height / 2, 'paddle').setImmovable(true);

    this.ball = this.physics.add.image(this.scale.width / 2, this.scale.height / 2, 'ball').setCollideWorldBounds(true).setBounce(1);

    this.paddleLeft.body.collideWorldBounds = true;
    this.paddleRight.body.collideWorldBounds = true;

    this.cursors = this.input.keyboard.createCursorKeys();
    this.keys = this.input.keyboard.addKeys('W,S');

    setupGameSocketHandlers(this);

    this.paddleInfo = this.add.text(10, 10, '', { fontSize: 16, color: '#fff' });
    this.sessionInfo = this.add.text(10, 30, '', { fontSize: 16, color: '#fff' });
    this.roundInfo = this.add.text(10, 50, '', { fontSize: 16, color: '#fff' });
  }

  update() {
    if (this.paddleSide === 'spectator') { this.updateUI(); return; }

    let vel = 0;
    if (this.paddleSide === 'left') {
      if (this.keys.W.isDown) vel = -GAME_SETTINGS.paddleVelocity;
      else if (this.keys.S.isDown) vel = GAME_SETTINGS.paddleVelocity;
    }
    if (this.paddleSide === 'right') {
      if (this.cursors.up.isDown) vel = -GAME_SETTINGS.paddleVelocity;
      else if (this.cursors.down.isDown) vel = GAME_SETTINGS.paddleVelocity;
    }

    const paddle = (this.paddleSide === 'left') ? this.paddleLeft : this.paddleRight;
    paddle.body.setVelocityY(vel);

    const serverY = (this.paddleSide === 'left') ? this.gameState?.paddle?.left?.y : this.gameState?.paddle?.right?.y;

    if (Number.isFinite(serverY) && paddle.y !== serverY) {
      socket.emit('updatePaddle', { session_id: this.sessionId, paddle: this.paddleSide, paddleY: paddle.y });
    }

    this.updateUI();
  }

  syncGameFromServer() {
    const g = this.gameState;
    if (g?.paddle?.left) this.paddleLeft.y = g.paddle.left.y;
    if (g?.paddle?.right) this.paddleRight.y = g.paddle.right.y;
    if (g?.ball) { this.ball.x = g.ball.x; this.ball.y = g.ball.y; }
  }

  updateUI() {
    this.paddleInfo.setText(
      this.paddleSide === 'left' ? 'Stai controllando: Sinistra' :
      this.paddleSide === 'right' ? 'Stai controllando: Destra' : 'Spettatore'
    );
    this.sessionInfo.setText(`Sessione: ${this.sessionId} | Giocatore: ${socket.id}`);
    if (this.gameState?.current_round) this.roundInfo.setText(`Round: ${JSON.stringify(this.gameState.current_round)}`);
  }
}
