from __future__ import annotations
from tkinter import N
import pygame
from enum import Enum

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, surface: pygame.Surface, x: int = 0, y: int = 0, *args, **kwargs):
        '''
        **kwargs: width: int, height: int, origin: tuple[int,int], surface_area: pygame.Rect, groups: list[pygame.sprite.Group]
        '''
        groups = []
        if "groups" in kwargs:
            groups = kwargs["groups"]
            del kwargs["groups"]
            
        super().__init__(*groups)
        self.__surface = surface

        if "surface_area" in kwargs and isinstance(kwargs["surface_area"], pygame.Rect):
            self._area: pygame.Rect = kwargs["surface_area"]
            
        if "origin" in kwargs and isinstance(kwargs["origin"], tuple):
            origin = kwargs["origin"]
            self._area: pygame.Rect = pygame.Rect(int(origin[0]), int(origin[1]), surface.get_width(), surface.get_height())
        else:
            self._area: pygame.Rect = pygame.Rect(0, 0, surface.get_width(), surface.get_height())
        
        self._stretch: bool = False
        width = 0
        if "width" in kwargs:
            width: int = kwargs["width"]
        else:
            width: int = self._area.width
            
        height = 0
        if "height" in kwargs:
            height: int = kwargs["height"]
        else:
            height: int = self._area.height

        self._size = (width, height)

        if self._size[0] != self._area.width or self._size[1] != self._area.height:
            self.image = pygame.transform.scale(surface.subsurface(self._area),(width, height))
        else:
            self.image = surface.subsurface(self._area)
        
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
        
    def UpdateView(self, origin: tuple[int,int], size: tuple[int,int] | None = None):
        size = size or self._area.size
        w, h = size
        if origin[0] + size[0] > self.__surface.get_width():
            w = self.__surface.get_width() - origin[0]
        
        if origin[1] + size[1] > self.__surface.get_height():
            h = self.__surface.get_height() - origin[1]
            
        self._area = pygame.Rect(origin[0], origin[1], w, h)
        self.image = self.__surface.subsurface(self._area)
        
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
        
class SpriteFrameAnim(Sprite):
    class Mode(Enum):
        ROW = 0
        COL = 1

    class PlayMode(Enum):
        MANUAL = 0
        LINEAR = 1
        REVERSE = 2
        
    def __init__(self, surface: pygame.Surface, x: int, y: int, row: int = 0, col: int = 0, *args, **kwargs):
        '''
        **kwargs: area: pygame.Rect, mode: int, interval: float
            mode: default ROW_LINEAR
                ROW_LINEAR - row first
                COL_LINEAR - col first
                ROW_REVERSE - reverse ROW_LINEAR
                COL_REVERSE - reverse COL_LINEAR
            interval: frame interval, default 1.0 / 30.0
        '''
        if "width" in kwargs:
            width = kwargs["width"]
        else:
            width = surface.get_width() // col
            
        if "height" in kwargs:
            height = kwargs["height"]
        else:
            height = surface.get_height() // row
            
        super().__init__(surface, x, y, width = width, height = height, *args, **kwargs)        
        if "mode" in kwargs:
            self.mode: SpriteFrameAnim.Mode = kwargs["mode"]
        else:
            self.mode: SpriteFrameAnim.Mode = SpriteFrameAnim.Mode.ROW
            
        if "play" in kwargs:
            self.play: SpriteFrameAnim.PlayMode = kwargs["play"]
        else:
            self.play: SpriteFrameAnim.PlayMode = SpriteFrameAnim.PlayMode.LINEAR
            
        if "interval" in kwargs:
            self.interval: float = kwargs["interval"]
        else:
            self.interval: float = 1.0 / 30.0 # 30fps

        self.tick = 0
        self.total_row = row
        self.total_col = col
        self.index = 0
        self.direction = 1
    
    def SetFrame(self, row: int, col: int):
        index = row % self.total_row * self.total_col + col % self.total_col
        if index >= self.total_row * self.total_col:
            return
        
        if row >= self.total_row:
            return
        
        if col >= self.total_col:
            return
        
        self.index = index
        self.UpdateView((row * self._size[0], col * self._size[1]))
    
    def NextFrame(self):
        if self.play == SpriteFrameAnim.PlayMode.REVERSE:
            # 往复播放
            self.index = self.index + self.direction
            if self.index <= 0:
                self.direction = -self.direction
            
            if self.index >= self.total_row * self.total_col - 1:
                self.direction = -self.direction
        elif self.play == SpriteFrameAnim.PlayMode.LINEAR:
            # 顺序播放
            self.index = (self.index + self.direction) % (self.total_row * self.total_col)
            if self.index < 0:
                self.index = self.total_row * self.total_col - 1
            
        row = 0
        col = 0    
        if self.mode == SpriteFrameAnim.Mode.COL:
            # 列优先
            row = self.index % self.total_row
            col = self.index // self.total_row
        else:
            # 行优先
            row = self.index // self.total_col
            col = self.index % self.total_col
        
        self.UpdateView((col * self._area.width, row * self._area.height))
        
    def update(self, *args, **kwargs):
        dt = 1000 if pygame.time.get_ticks() - self.tick > 1000 else pygame.time.get_ticks() - self.tick
        if dt > self.interval * 1000:
            self.tick += self.interval * 1000
            self.NextFrame()