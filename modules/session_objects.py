from typing import Optional, List
from flask import current_app
from dataclasses import dataclass, asdict, field, fields, is_dataclass, InitVar
from datetime import datetime
from uuid import UUID
from enum import Enum

@dataclass
class Base:
    def to_dict(self):
        return _serialize(self)

def _serialize(obj):
    # 1️⃣ None
    if obj is None:
        return None

    # Dataclass
    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            result[f.name] = _serialize(value)
        return result

    # Oggetti con .to_dict() personalizzato
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()

    # Liste e tuple
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(item) for item in obj]

    # Dizionari
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}

    # datetime → ISO8601
    if isinstance(obj, datetime):
        return obj.isoformat()

    # UUID → stringa
    if isinstance(obj, UUID):
        return str(obj)

    # Enum → valore
    if isinstance(obj, Enum):
        return obj.value

    # Oggetti non serializzabili → stringa
    if not _is_json_primitive(obj):
        return str(obj)

    # Primitive JSON-safe
    return obj

def _is_json_primitive(value):
    return isinstance(value, (str, int, float, bool))

@dataclass
class Velocity(Base):
    x: float
    y: float

@dataclass
class Ball(Base):
    x: float
    y: float
    velocity: Velocity

@dataclass
class Paddle(Base):
    x: float
    y: float

    

@dataclass
class Paddles(Base):
    left: Paddle
    right: Paddle

@dataclass
class Players(Base):
    left: Optional[str] = None
    right: Optional[str] = None

from dataclasses import dataclass


@dataclass
class Round:
    start_countdown: InitVar[float] = 3.0  #usato nel costruttore
    _start_countdown: float = field(default=3.0, repr=False, init=False) #usato internamente
    winner: str | None = None

    @property
    def countdown(self) -> float:
        return self._start_countdown

    @countdown.setter
    def countdown(self, value: float):
        self._start_countdown = max(0.0, value)


@dataclass
class GameState(Base):
    paddle: Paddles
    ball: Ball
    rounds: list[Round] = field(default_factory=list)
    current_round: object = None

@dataclass
class SessionData(Base):
    players: Players
    game_state: GameState
    last_update_time: float = 0    