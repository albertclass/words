from __future__ import annotations
from tkinter import N
import pygame
from enum import Enum

class Sprite(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface, x: int = 0, y: int = 0, *args, **kwargs):
        '''
        **kwargs: 
            width: int      # sprite width
            height: int     # sprite height
            origin: tuple[int,int]  # start position of surface
            clip: pygame.Rect
            groups: list[pygame.sprite.Group]
        '''
        groups = []
        if "groups" in kwargs:
            groups = kwargs["groups"]
            del kwargs["groups"]
            
        super().__init__(*groups)

        self._stretch: bool = False
        width = 0
        if "width" in kwargs:
            width: int = kwargs["width"]
        else:
            width: int = surface.get_width()
            
        height = 0
        if "height" in kwargs:
            height: int = kwargs["height"]
        else:
            height: int = surface.get_height()

        self._size = (width, height)

        if "clip" in kwargs and isinstance(kwargs["clip"], pygame.Rect):
            self.image = surface.subsurface(kwargs["clip"])
        else:
            self.image = surface

        if "origin" in kwargs and isinstance(kwargs["origin"], tuple):
            origin = kwargs["origin"]
            self._area: pygame.Rect = pygame.Rect(int(origin[0]), int(origin[1]), min(width, surface.get_width() - origin[0]), min(height, surface.get_height() - origin[1]))
        else:
            self._area: pygame.Rect = pygame.Rect(0, 0, min(width, surface.get_width()), min(height, surface.get_height()))
        
        self.rect = pygame.Rect(x, y, width, height)
    
    def Size(self) -> tuple[int,int]:
        return self._size

    def MoveTo(self, x: int, y: int):
        if self.rect is not None:
            self.rect.x = x
            self.rect.y = y
        
    def Offset(self, dx: int, dy: int):
        if self.rect is not None:
            self.rect.move_ip(dx, dy)
        
    def UpdateSurface(self, surface: pygame.Surface, w: int = 0, h: int = 0):
        self.__surface = surface
        if w > 0:
            self._area.width = min(w, self._area.width)
        else:
            self._area.width = surface.get_width() - self._area.x
            
        if h > 0:
            self._area.height = min(h, self._area.height)
        else:
            self._area.height = surface.get_height() - self._area.y
            
        self.image = surface.subsurface(self._area)
        
class SpriteFrameAnim(pygame.sprite.Sprite):
    class Mode(Enum):
        ROW = 0
        COL = 1

    class PlayMode(Enum):
        MANUAL = 0
        LINEAR = 1
        REVERSE = 2
        
    def __init__(self, surface: pygame.Surface, row: int = 1, col: int = 1, mode: Mode = Mode.ROW, interval: float = 0.04, *args, **kwargs):
        '''
        **kwargs: area: pygame.Rect, mode: int, interval: float
            mode: default ROW_LINEAR
                ROW_LINEAR - row first
                COL_LINEAR - col first
                ROW_REVERSE - reverse ROW_LINEAR
                COL_REVERSE - reverse COL_LINEAR
            play: default LINEAR
                MANUAL - manual play
                LINEAR - linear play
                REVERSE - reverse play
            interval: frame interval, default 1.0 / 30.0
        '''
        super().__init__(*args, **kwargs)

        width  = surface.get_width()  // col
        height = surface.get_height() // row

        self.rect = pygame.Rect(0, 0, width, height)

        self.frames: list[pygame.Surface] = []
        self.frameIndex = 0
            
        self.mode: SpriteFrameAnim.Mode = mode
        self.play: SpriteFrameAnim.PlayMode = SpriteFrameAnim.PlayMode.MANUAL

        if self.mode == SpriteFrameAnim.Mode.ROW:
            for i in range(row):
                for j in range(col):
                    frame = surface.subsurface(pygame.Rect(j * width, i * height, width, height))
                    self.frames.append(frame)
        else:
            for i in range(col):
                for j in range(row):
                    frame = surface.subsurface(pygame.Rect(i * width, j * height, width, height))
                    self.frames.append(frame)


        self.interval: float = interval
        self.tick = 0
        self.index = 0
        self.direction = 1
    
    def SetInterval(self, interval: float):
        self.interval = interval

    def SetMode(self, mode: SpriteFrameAnim.Mode):
        self.mode = mode
    
    def Play(self, mode: SpriteFrameAnim.PlayMode, direction: int = 1):
        self.direction = direction
        self.play = mode

    def Stop(self):
        self.play = SpriteFrameAnim.PlayMode.MANUAL

    def SetFrame(self, index: int):
        if index < 0:
            index = len(self.frames) + index % len(self.frames)

        if index >= len(self.frames):
            index = index % len(self.frames)
        
        self.index = index
        self.image = self.frames[index]
    
    def NextFrame(self):
        if self.play == SpriteFrameAnim.PlayMode.REVERSE:
            # 往复播放
            self.index = self.index + self.direction
            if self.index <= 0:
                self.direction = -self.direction
            
            if self.index >= len(self.frames) - 1:
                self.direction = -self.direction
        elif self.play == SpriteFrameAnim.PlayMode.LINEAR:
            # 顺序播放
            self.index = (self.index + self.direction) % len(self.frames)
            
        self.image = self.frames[self.index]

    def MoveTo(self, x: int, y: int):
        if self.rect is not None:
            self.rect.x = x
            self.rect.y = y
        
    def Offset(self, dx: int, dy: int):
        if self.rect is not None:
            self.rect.move_ip(dx, dy)

    def update(self, *args, **kwargs):
        dt = 1000 if pygame.time.get_ticks() - self.tick > 1000 else pygame.time.get_ticks() - self.tick
        if dt > self.interval * 1000:
            self.tick += self.interval * 1000
            self.NextFrame()