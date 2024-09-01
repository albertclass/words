from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from .fonts import FontManager

fonts = FontManager()

class Scene(ABC):
    def __init__(self, title: str, size: tuple[int, int], span: int = 2, border: int = 1):
        self._title = title
        self._size = size
        self._span = span
        self._border = border
    
    def width(self) -> int:
        return self._size[0]
    
    def height(self) -> int:
        return self._size[1]
    
    def title(self) -> str:
        return self._title
    
    def size(self) -> tuple[int,int]:
        return self._size
    
    def center(self) -> tuple[int,int]:
        return (self._size[0] // 2, self._size[1] // 2)
    
    @abstractmethod
    def _onEnter(self, prevScene: Scene | None) -> None:
        pass
    
    @abstractmethod
    def _onLeave(self) -> None:
        pass
    
    @abstractmethod
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def Update(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def Draw(self, screen: pygame.Surface) -> None:
        pass
    
class SceneManager:
    _instance = None
    
    def __new__(cls) -> SceneManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.__clock = pygame.time.Clock()
        
        if not hasattr(self, "scenes"):
            self.scenes : dict[str, Scene] = {}
            
        if not hasattr(self, "currentScene"):
            self.currentScene : Scene | None = None
    
    def AddScene(self, name: str, scene: Scene, switch: bool = False) -> None:
        self.scenes[name] = scene
        if switch:
            self.Switch(name)
    
    def Switch(self, name: str) -> None:
        if name not in self.scenes:
            return
        
        if self.currentScene is not None:
            self.currentScene._onLeave()
            
        previousScene = self.currentScene
        self.currentScene = self.scenes[name]
        self.currentScene._onEnter(previousScene)
    
    def Remove(self, name: str) -> None:
        if name in self.scenes:
            del self.scenes[name]
                            
    def Update(self, *args, **kwargs) -> bool:
        if self.currentScene is None:
            return False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.currentScene._onKeyDown(event)
            elif event.type == pygame.KEYUP:
                self.currentScene._onKeyUp(event)
            elif event.type == pygame.MOUSEMOTION:
                self.currentScene._onMouseMove(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.currentScene._onMouseButtonDown(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.currentScene._onMouseButtonUp(event)
                
        self.currentScene.Update(*args, **kwargs)
        return True
    
    def Draw(self, screen: pygame.Surface) -> None:
        if self.currentScene is None:
            return
        
        self.currentScene.Draw(screen)
        
        pygame.display.update()

                   
