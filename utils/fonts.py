from __future__ import annotations
import pygame
import hashlib
from typing import Hashable, Iterable

class FontManager:
    '''
    management of fonts
    '''
    _instance = None
    def __new__(cls) -> FontManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.fonts : dict[str, pygame.font.Font] = {}
    
    def __FontSign(self, name: str | bytes | Iterable[str | bytes] | None, size: int, bold: Hashable, italic: Hashable) -> str:
        '''
        get font sign
        '''
        if name is None:
            name = "Arial"
        elif isinstance(name, bytes):
            name = name.decode()
        elif isinstance(name, Iterable):
            names: list[str] = []
            for n in name:
                if isinstance(n, bytes):
                    names.append(n.decode())
                elif isinstance(n, str):
                    names.append(n)
                    
            name = ":".join(names)
        
        signString = f"{name}-{size}-{bold}-{italic}"
        # md5sum signString
        md5 = hashlib.md5()
        md5.update(signString.encode())
        return md5.hexdigest()
    
    def GetFont(self, name: str | bytes | Iterable[str | bytes] | None, size: int, bold: Hashable = False, italic: Hashable = False) -> pygame.font.Font:
        '''
        get font
        '''
        sign = self.__FontSign(name, size, bold, italic)
        if name not in self.fonts:
            self.fonts[sign] = pygame.font.SysFont(name, size, bold, italic)
            
        return self.fonts[sign]
    
    def AddFont(self, name: str | bytes | Iterable[str | bytes] | None, size: int, bold: Hashable = False, italic: Hashable = False) -> None:
        '''
        add font
        '''
        sign = self.__FontSign(name, size, bold, italic)
        if sign not in self.fonts:
            self.fonts[sign] = pygame.font.SysFont(name, size, bold, italic)