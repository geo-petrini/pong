
import { GAME_SETTINGS, clamp } from "./gameSettings.js";

export async function loadServerConfig() {
  try {
    const res = await fetch('/config');
    if (!res.ok) return;
    const cfg = await res.json();

    const PW = cfg.PADDLE_WIDTH ?? cfg.PADDLE_WIDHT; // retrocompat

    GAME_SETTINGS.paddleWidth    = clamp(PW,                  2, 200,  GAME_SETTINGS.paddleWidth);
    GAME_SETTINGS.paddleHeight   = clamp(cfg.PADDLE_HEIGHT,  10, 600,  GAME_SETTINGS.paddleHeight);
    GAME_SETTINGS.ballSize       = clamp(cfg.BALL_SIZE,       2, 200,  GAME_SETTINGS.ballSize);
    GAME_SETTINGS.paddleVelocity = clamp(cfg.PADDLE_VELOCITY,50, 2000, GAME_SETTINGS.paddleVelocity);
    GAME_SETTINGS.ballVelocity   = clamp(cfg.BALL_VELOCITY,  50, 2000, GAME_SETTINGS.ballVelocity);
    GAME_SETTINGS.width          = clamp(cfg.GAME_WIDTH,    200, 4096, GAME_SETTINGS.width);
    GAME_SETTINGS.height         = clamp(cfg.GAME_HEIGHT,   200, 4096, GAME_SETTINGS.height);
    GAME_SETTINGS.paddleOffset   = clamp(cfg.PADDLE_OFFSET,   0,  400,  GAME_SETTINGS.paddleOffset);
  } catch (e) {
    console.warn('Config load failed, using defaults', e);
  }
}
