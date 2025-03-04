from __future__ import annotations
from xmlrpc.client import boolean
import pygame
from .sprite import SpriteFrameAnim

class Charactor:
    def __init__(self, name: str, speed: float = 0.0, actions: dict[str, SpriteFrameAnim] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._actions: dict[str, SpriteFrameAnim] = actions or {}
        self._action: SpriteFrameAnim | None = None
        self._target: tuple[int, int] = (0, 0)

        self._name = name
        self._speed: float = 0
        self._x: float | int = 0
        self._y: float | int = 0
        self._hotspot: tuple[int, int] = (0, 0)

    def addAction(self, key: str, action: SpriteFrameAnim):
        self._actions[key] = action
        
    def setAction(self, key: str)-> bool:
        if key not in self._actions or self._action == self._actions[key]:
            return False
        
        self._action = self._actions[key]
        self._action.Play(SpriteFrameAnim.PlayMode.LINEAR)
        self._action.SetFrame(0)

        return True
    
    def update(self):
        if self._action is None:
            return
        
        # 根据当前位置和目标位置，计算移动方向
        dx = self._target[0] - self.x
        dy = self._target[1] - self.y
        tx: float = self.x
        ty: float = self.y

        if dx == 0 and dy > 0:
            # 向下移动
            self.setAction("down")
            ty = self.y + min(abs(dy), self._speed)
        elif dx == 0 and dy < 0:
            # 向上移动
            self.setAction("up")
            ty = self.y - min(abs(dy), self._speed)
        elif dx > 0 and dy == 0:
            # 向右移动
            self.setAction("right")
            tx = self.x + min(abs(dx), self._speed)
        elif dx < 0 and dy == 0:
            # 向左移动
            self.setAction("left")
            tx = self.x - min(abs(dx), self._speed)
        elif dx > 0 and dy > 0:
            # 向右下移动
            self.setAction("downright")
            tx = self.x + min(abs(dx), self._speed / 1.414)
            ty = self.y + min(abs(dy), self._speed / 1.414)
        elif dx > 0 and dy < 0:
            # 向右上移动
            self.setAction("upright")
            tx = self.x + min(abs(dx), self._speed / 1.414)
            ty = self.y - min(abs(dy), self._speed / 1.414)
        elif dx < 0 and dy > 0:
            # 向左下移动
            self.setAction("downleft")
            tx = self.x - min(abs(dx), self._speed / 1.414)
            ty = self.y + min(abs(dy), self._speed / 1.414)
        elif dx < 0 and dy < 0:
            # 向左上移动
            self.setAction("upleft")
            tx = self.x - min(abs(dx), self._speed / 1.414)
            ty = self.y - min(abs(dy), self._speed / 1.414)
        else:
            self.setAction("down")
            self.stop()

        self.move(tx, ty)
        self._action.update()

    @property
    def rect(self) -> pygame.Rect | pygame.FRect | None:
        return self._rect if self._rect is not None else (self._action.rect if self._action is not None else None)
    
    @rect.setter
    def rect(self, rect: pygame.Rect | pygame.FRect):
        self._rect = rect

    @property
    def speed(self) -> float:
        return self._speed
    
    @speed.setter
    def speed(self, speed: float):
        self._speed = speed

    @property
    def target(self) -> tuple[int, int]:
        return self._target
    
    @target.setter
    def target(self, target: tuple[int, int]):
        self._target = target

    @property
    def hotspot(self) -> tuple[int, int]:
        return self._hotspot
    
    @hotspot.setter
    def hotspot(self, hotspot: tuple[int, int]):
        self._hotspot = hotspot

    @property
    def x(self) -> float | int:
        return self._x
    
    @property
    def y(self) -> float | int:
        return self._y
    
    @property
    def width(self) -> int:
        if self._action is None:
            return 0
        
        return self._action.width
    
    @property
    def height(self) -> int:
        if self._action is None:
            return 0
        
        return self._action.height
    
    def stop(self):
        if self._action is not None:
            self._action.Stop()

    def move(self, x: float | int, y: float | int):
        self._x, self._y = x, y

    def walk(self, x: int, y: int):
        self._target = (x - self._hotspot[0], y - self._hotspot[1])

    def draw(self, surface: pygame.Surface):
        if self._action is None:
            return
        
        if self._action.image is None:
            return
        
        surface.blit(self._action.image, (self.x, self.y)) 
            
