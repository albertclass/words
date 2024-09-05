import pygame
from scenes.prepare import PrepareScene
from scenes.remember import RememberScene
import utils
from scenes import WelcomeScene, BooksScene, PrepareScene, RememberScene

_screen_size = (1280, 1024)
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(_screen_size)
    pygame.display.set_caption("兔哥背单词")
    
    utils.SceneManager.AddScene("Welcome", WelcomeScene(_screen_size), True)
    utils.SceneManager.AddScene("Books", BooksScene(_screen_size, "books"))
    utils.SceneManager.AddScene("Prepare", PrepareScene(_screen_size))
    utils.SceneManager.AddScene("Remember", RememberScene(_screen_size))
    clock = pygame.time.Clock()
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        clock.tick(60)
        
    pygame.quit()
    
