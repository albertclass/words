import os
import sys
import pygame
import pygame_gui as gui
import pygame_gui.elements as ele

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utils

class LoginScene(utils.Scene):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__("Login", size, 2, 1, *args, **kwargs)
        center_x = (size[0] - 100) // 2
        center_y = (size[1] - 50) // 2
        self.__button = ele.UIButton(
            relative_rect=pygame.Rect((center_x, center_y), (100, 50)),
            text='Say Hello',
            manager=self._uimanager)

    
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        pass
    
    def _onLeave(self) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.event.Event) -> None:
        pass
    
    def Update(self, *args, **kwargs) -> bool:
        return True
    
    def Draw(self, screen: pygame.Surface) -> None:
        pass
    
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("兔哥背单词")
    scene = LoginScene((1280, 1024))

    utils.SceneManager.AddScene("Login", scene, True)
    clock = pygame.time.Clock()

    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        clock.tick(100)
        
    pygame.quit()