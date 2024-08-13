import pygame
from scenes.remember import RememberScene
import utils
from scenes import WelcomeScene, BooksScene, RememberScene

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("兔哥背单词")
    
    utils.SceneManager.AddScene("Welcome", WelcomeScene(800, 600), True)
    utils.SceneManager.AddScene("Books", BooksScene(800, 600, "books"))
    utils.SceneManager.AddScene("Remember", RememberScene(800, 600))
    clock = pygame.time.Clock()
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        clock.tick(60)
        
    pygame.quit()
    
