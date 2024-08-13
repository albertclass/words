from __future__ import annotations
import pygame
from enum import Enum

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, surface: pygame.Surface, x: int = 0, y: int = 0, *args, **kwargs):
        '''
        **kwargs: width: int, height: int
        '''
        groups = []
        if "groups" in kwargs:
            groups = kwargs["groups"]
            del kwargs["groups"]
            
        super().__init__(*groups)
        self.surface = surface

        if "origin" in kwargs:
            self.origin: tuple[int,int] = kwargs["origin"]
        else:
            self.origin: tuple[int,int] = (0, 0)
            
        if "width" in kwargs:
            self.width: int = min(kwargs["width"], surface.get_width() - self.origin[0])
        else:
            self.width: int = surface.get_width() - self.origin[0]
            
        if "height" in kwargs:
            self.height: int = min(kwargs["height"], surface.get_height() - self.origin[1])
        else:
            self.height: int = surface.get_height() - self.origin[1]

        self.image = surface.subsurface(pygame.Rect(self.origin[0], self.origin[1], self.width, self.height))
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def Size(self) -> tuple[int,int]:
        return (self.height, self.width)

    def MoveTo(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
        
    def Offset(self, dx: int, dy: int):
        self.rect.move_ip(dx, dy)
        
    def UpdateView(self, origin: tuple[int,int]):
        self.origin = origin
        self.image = self.surface.subsurface(pygame.Rect(self.origin[0], self.origin[1], self.width, self.height))
        
    def UpdateSurface(self, surface: pygame.Surface, w: int = 0, h: int = 0):
        self.surface = surface
        if w > 0:
            self.width = min(w, self.width)
        else:
            self.width = surface.get_width() - self.origin[0]
            
        if h > 0:
            self.height = min(h, self.height)
        else:
            self.height = surface.get_height() - self.origin[1]
            
        self.image = surface.subsurface(pygame.Rect(self.origin[0], self.origin[1], self.width, self.height))
        
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
        self.UpdateView((row * self.width, col * self.height))
    
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
        
        self.UpdateView((col * self.width, row * self.height))
        
    def update(self, *args, **kwargs):
        dt = 1000 if pygame.time.get_ticks() - self.tick > 1000 else pygame.time.get_ticks() - self.tick
        if dt > self.interval * 1000:
            self.tick += self.interval * 1000
            self.NextFrame()