if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils

class WelcomeScene(utils.Scene):
    def __init__(self, size):
        super().__init__("Welcome", size)
        self._application : pygame.sprite.Group = pygame.sprite.Group()
        self.background_image = pygame.image.load("images/startup.png")
        
        font = utils.FontManager.GetFont("font/msyh.ttc", 64)
        text = font.render("我爱背单词", True, (153, 213, 240))
        # pygame.draw.rect(text, (128, 128, 128), (0, 0, text.get_width(), text.get_height()), 1, 5)
        
        pos_x = utils.CenterPosX(text, size)
        welcome = utils.Sprite(text, pos_x, 100)
        self._application.add(welcome)
        
        versionFont = utils.FontManager.GetFont("font/msyh.ttc", 16)
        versionText = versionFont.render("Ver 1.0.0", True, (255, 255, 0))

        versionSprite = utils.Sprite(versionText, size[0] - versionText.get_width() - 5, size[1] - versionFont.get_height() - 5)
        self._application.add(versionSprite)
        
        tipsFont = utils.FontManager.GetFont("华文楷体", 32)
        frame = 25
        self._tips = pygame.sprite.Group()
            
        tex = tipsFont.render("Press any key to continue ...", True, (0, 0, 0))

        self._tipsTex = pygame.Surface((tex.width, tex.height * frame))
        self._tipsTex.set_colorkey((0, 0, 0))

        for i in range(frame):
            color = 127 + i * (128 // frame)
            tex = tipsFont.render("Press any key to continue ...", True, (color, color, color))
            self._tipsTex.blit(tex, (0, i * tex.height))
        

        pos = utils.CenterPos(self._tipsTex, size)
        self._tipsTextAnim = utils.SpriteFrameAnim(self._tipsTex, 
            frame, # row
            1, # col
            mode = utils.SpriteFrameAnimMode.COL, # frame mode
            interval = 0.04
        )
        self._tipsTextAnim.MoveTo(pos[0], self.height - tex.height - 20)
        self._tipsTextAnim.Play(utils.SpriteFrameAnimPlayMode.REVERSE)

        self._tips_added = False
        
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        # utils.ResourceManager.add("phonetic/en.zip")
        pass
    
    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        print("Leave Welcome")
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if utils.ResourceManager.is_done():
            utils.SceneManager.Switch("Login")
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        print(f"Key Up: {event.key}")

    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        if utils.ResourceManager.is_done():
            utils.SceneManager.Switch("Login")
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass

    def _onUIEvent(self, event: pygame.Event) -> None:
        pass
    
    def Update(self, *args, **kwargs) -> bool:
        if not self._tips_added and utils.ResourceManager.is_done():
            self._tips_added = True
            self._tips.empty()
            self._tips.add(self._tipsTextAnim)
    
        self._tips.update(*args, **kwargs)

        return True

    def Draw(self, surface: pygame.Surface) -> None:
        self._application.draw(surface)
        self._tips.draw(surface)
        
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("兔哥背单词")
    scene = WelcomeScene((1280, 1024))
    
    utils.SceneManager.AddScene("Welcome", scene, True)
        
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)

        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
    
