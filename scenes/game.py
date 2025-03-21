import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
import random

class GameScene(utils.Scene):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__("Game", size, *args, **kwargs)
        self._firework_lasttime = pygame.time.get_ticks()
        self._fireworks = utils.Fireworks()
        self._group = pygame.sprite.Group()
        self._defaultFont = utils.FontManager.GetFont("font/msyh.ttc", 24)
        self._font_color = (255,255,255)
        self._click_cnt = 0
        self._click_cps = 0
        self._click_cnt_tex = self._defaultFont.render(f"Click count: {self._click_cnt}", True, self._font_color)
        self._click_cps_tex = self._defaultFont.render(f"Clicks per second: {self._click_cps:.2f}", True, self._font_color)
        self.background_image = pygame.image.load("images/background-5.png")

    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        # 背完了，更新状态
        self._group.empty()
        congratulation = self._defaultFont.render("Congratulations! You have finished the exercise!", True, self._font_color)
        self._group.add(utils.Sprite(congratulation, (self.width - congratulation.width) // 2, (self.height - congratulation.height) // 2))

    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self._click_cnt = 0
            self._click_cps = 0
            self._click_cnt_tex = self._defaultFont.render(f"Click count: {self._click_cnt}", True, self._font_color)
            self._click_cps_tex = self._defaultFont.render(f"Clicks per second: {self._click_cps:.2f}", True, self._font_color)

            delattr(self, '_last_click_time')
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None: 
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        self._click_cnt += 1
        self._click_cnt_tex = self._defaultFont.render(f"Click count: {self._click_cnt}", True, self._font_color)
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.event.Event) -> None:
        pass
    
    def Update(self, *args, **kwargs) -> bool:
        # 全部背完了， 开始放烟花
        if self._firework_lasttime + 1000 < pygame.time.get_ticks():
            self._firework_lasttime = pygame.time.get_ticks()
            self._fireworks.add(
                random.randint(0, self.width), 
                random.randint(0, self.height // 4)
            )
        self._group.add()
        self._fireworks.update()

        # Calculate clicks per second (CPS)
        current_time = pygame.time.get_ticks()
        if not hasattr(self, '_last_click_time'):
            self._last_click_time = current_time
            self._click_cps = 0
        else:
            elapsed_time = (current_time - self._last_click_time) / 1000  # Convert to seconds
            if elapsed_time > 0:
                self._click_cps = self._click_cnt / elapsed_time
                self._click_cps_tex = self._defaultFont.render(f"Clicks per second: {self._click_cps:.2f}", True, self._font_color)
        return True
        
    def Draw(self, screen: pygame.Surface) -> None:        
        self._group.draw(screen)
        self._fireworks.draw(screen)
        screen.blit(self._click_cnt_tex, (self.width - self._click_cnt_tex.get_width() - 30, 10))
        screen.blit(self._click_cps_tex, (self.width - self._click_cps_tex.get_width() - 30, 40))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("游戏时间")
    scene = GameScene((1280, 1024))
    
    utils.SceneManager.AddScene("Game", scene, True)
        
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)

        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
    
