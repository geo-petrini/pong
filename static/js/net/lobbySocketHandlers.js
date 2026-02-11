
import { socket } from './socketClient.js';

export function setupLobbySocketHandlers(scene) {
  socket.on('sessionCreated', (resp) => {
    if (resp && resp.to === socket.id) {
      socket.emit('joinSession', { session_id: resp.session_id });
    }
  });

  socket.on('sessionJoined', (resp) => {
    if (resp && resp.to === socket.id) {
      scene.scene.start('GameScene', { sessionId: resp.session_id, paddle: resp.paddle });
    }
  });

  socket.on('sessionError', (err) => {
    scene.showError(err?.message || 'Errore di sessione');
  });

  scene.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
    socket.off('sessionCreated');
    socket.off('sessionJoined');
    socket.off('sessionError');
  });
}
