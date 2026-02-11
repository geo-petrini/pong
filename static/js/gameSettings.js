
export const GAME_SETTINGS = {
  paddleWidth: 10,
  paddleHeight: 100,
  paddleOffset: 50,
  paddleVelocity: 300,
  ballVelocity: 200,
  width: 800,
  height: 600,
  ballSize: 10,
};

export const clamp = (v, min, max, fallback) => {
  const n = Number(v);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, n));
};
