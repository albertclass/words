if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils

class GameScene(utils.Scene):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__("Game", size, *args, **kwargs)

        charactor = pygame.image.load("images/CH00171.png")
        self.animates : list[utils.SpriteFrameAnim] = []
        self.scene: pygame.sprite.Group = pygame.sprite.Group()

        for i in range(8):
            way = charactor.subsurface((0, 1024 // 8 * i, 1024, 1024 // 8))
            anim = utils.SpriteFrameAnim(way, 1, 8)
            anim.SetMode(utils.SpriteFrameAnimMode.ROW)
            anim.SetFrame(0)
            anim.MoveTo(100 + 1024 // 8 * i, 100)
            anim.Play(utils.SpriteFrameAnimPlayMode.LINEAR)
            self.animates.append(anim)
            self.scene.add(anim)

    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        for anim in self.animates:
            anim.SetFrame(0)
    
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
        self.scene.update(*args, **kwargs)
        return True
    
    def Draw(self, screen: pygame.Surface) -> None:
        screen.fill((0,0,0))
        self.scene.draw(screen)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("游戏时间")
    scene = GameScene((1280, 1024))
    
    utils.SceneManager.AddScene("Welcome", scene, True)
        
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)

        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
    
