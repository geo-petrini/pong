
import { socket } from './socketClient.js';

export function setupGameSocketHandlers(scene) {
  scene._onGameState = (resp) => {
    if (!resp || resp.session_id !== scene.sessionId) return;
    scene.gameState = resp.state;
    scene.syncGameFromServer();
  };

  socket.on('gameState', scene._onGameState);

  scene.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
    socket.off('gameState', scene._onGameState);
  });
}
