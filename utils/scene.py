from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
import pygame_gui

events = [
    pygame_gui.UI_BUTTON_PRESSED,
    pygame_gui.UI_BUTTON_START_PRESS,
    pygame_gui.UI_BUTTON_DOUBLE_CLICKED,
    pygame_gui.UI_BUTTON_ON_HOVERED,
    pygame_gui.UI_BUTTON_ON_UNHOVERED,
    pygame_gui.UI_TEXT_BOX_LINK_CLICKED,
    pygame_gui.UI_TEXT_ENTRY_CHANGED,
    pygame_gui.UI_TEXT_ENTRY_FINISHED,
    pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
    pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
    pygame_gui.UI_2D_SLIDER_MOVED,
    pygame_gui.UI_SELECTION_LIST_NEW_SELECTION,
    pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION,
    pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION,
    pygame_gui.UI_FORM_SUBMITTED,
    pygame_gui.UI_WINDOW_CLOSE,
    pygame_gui.UI_WINDOW_MOVED_TO_FRONT,
    pygame_gui.UI_WINDOW_RESIZED,
    pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
    pygame_gui.UI_FILE_DIALOG_PATH_PICKED,
    pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED,
    pygame_gui.UI_COLOUR_PICKER_COLOUR_CHANNEL_CHANGED,
    pygame_gui.UI_CONSOLE_COMMAND_ENTERED,
    pygame_gui.UI_TEXT_EFFECT_FINISHED,
]

class Scene(ABC):
    def __init__(self, title: str, size: tuple[int, int], span: int = 2, border: int = 1, *args, **kwargs):
        self._title = title
        self._size = size
        self._span = span
        self._border = border
        self._show_ui = True
        self._uimanager = pygame_gui.UIManager(size, **kwargs)
    
    @property
    def width(self) -> int:
        return self._size[0]

    @property
    def height(self) -> int:
        return self._size[1]
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def size(self) -> tuple[int,int]:
        return self._size
    
    @property
    def show_ui(self) -> bool:
        return self._show_ui
    
    @show_ui.setter
    def show_ui(self, show: bool = True) -> None:
        self._show_ui = show
        
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
    def _onUIEvent(self, event: pygame.event.Event) -> None:
        pass
    
    @abstractmethod
    def Update(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def Draw(self, screen: pygame.Surface) -> None:
        pass
    
    def DrawUI(self, screen: pygame.Surface) -> None:
        self._uimanager.draw_ui(screen)
    
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
            if event.type in events:
                self.currentScene._onUIEvent(event)
            elif isinstance(self.currentScene._uimanager, pygame_gui.UIManager) and self.currentScene.show_ui:
                # Process events for the UI manager if the scene has UI
                if self.currentScene._uimanager.process_events(event):
                    continue

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
        self.currentScene._uimanager.update(self.__clock.tick(60) / 1000.0)
        return True
    
    def Draw(self, screen: pygame.Surface) -> None:
        if self.currentScene is None:
            return
        
        self.currentScene.Draw(screen)
        if self.currentScene.show_ui:
            self.currentScene.DrawUI(screen)
        
        pygame.display.update()
