
import { loadServerConfig } from "./configLoader.js";
import { GAME_SETTINGS } from "./gameSettings.js";
import LobbyScene from "./scenes/LobbyScene.js";
import GameScene from "./scenes/GameScene.js";

(async () => {
  await loadServerConfig();
  const config = {
    type: Phaser.AUTO,
    pixelArt: true,
    roundPixels: true,
    parent: "phaser-content",
    width: GAME_SETTINGS.width,
    height: GAME_SETTINGS.height,
    physics: { default: "arcade", arcade: { debug: false } },
    scene: [LobbyScene, GameScene]
  };
  new Phaser.Game(config);
})();
