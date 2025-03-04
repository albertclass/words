from __future__ import annotations
import os
import sys
import time
from typing import Iterable

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from core import Book, Word

class PrepareScene(utils.Scene):
    def __init__(self, size: tuple[int, int], span: int = 2, border: int = 1):
        super().__init__("Prepare", size, span, border)
        self._book: Book = Book()
        self._iter: Iterable[Word] | None = None
        self._defaultFont: pygame.font.Font = utils.FontManager.GetFont("font/msyh.ttc", 24)
        self._characterFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 48)
        self._informationFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 18)
        self._phoneticFont: pygame.font.Font = utils.FontManager.GetFont("calibri", 24)
        self._group: pygame.sprite.Group = pygame.sprite.Group()
        self._statusbar: pygame.sprite.Group = pygame.sprite.Group()
        self._font_color = (0,0,0)
        self._board_color = (0,0,0)
        self.background_image = pygame.image.load("images/background-3.png")

    def _onEnter(self, prevScene: utils.Scene | None, *params, **kwargs) -> None:
        book = utils.SceneManager.GetSceneProperty("Books", "book")
        if isinstance(book, Book):
            self._book = book
            self.Next()
    
    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE: 
            utils.SceneManager.Switch("Remember")
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.Next()
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.Event) -> None:
        pass
    
    def UpdateStatus(self) -> None:
        self._statusbar.empty()
        info = f"right {self.__currentWord.right} | wrong {self.__currentWord.wrong} | bingo: {self.__currentWord.bingo}"
        info_size = self._informationFont.size(info)
        
        info_x = self.width - info_size[0] - self._span * 2
        if info_x < 0 :
            info_x = 0
        
        # background = pygame.Surface((self.width - self._span * 2 - self._border * 2, info_size[1] + self._span * 2 - self._border * 2))
        # background.fill((0,0,200))
        
        # self._statusbar.add(utils.Sprite(background, self._span + self._border, self.height - info_size[1] - self._span * 3))
        self._statusbar.add(utils.Sprite(self._informationFont.render(info, True, [255,255,255]), info_x , self.height - info_size[1] - self._span * 2))

    def Update(self, *args, **kwargs) -> bool:
        if self._iter is None:
            self._group.empty()
            congratulation = self._defaultFont.render("Congratulations! You have finished the exercise!", True, [255,255,255])
            self._group.add(utils.Sprite(congratulation, (self.width - congratulation.width) // 2, (self.height - congratulation.height) // 2))
        
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self._board_color, (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        pygame.draw.line(surface,
            self._board_color,
            (0 + self._span, self.height - self._span * 2 - 24), 
            (self.width - self._span - self._border, self.height - self._span * 2 - 24), 
            1
        )
        
        self._group.draw(surface)
        self._statusbar.draw(surface)

    def Next(self) -> bool:
        if self._book is None:
            return False
        
        if self._iter is None:
            self._iter = iter(self._book)
        
        try:
            # get next word
            self.__currentWord = next(self._book)
            self.__currentWord.play()
            self._group.empty()
            
            self._group.add(utils.Sprite(self._phoneticFont.render(self.__currentWord.content["phonetic"], True, self._font_color), 150, 190))

            if "translation" in self.__currentWord.content \
                and self.__currentWord.content["translation"] is not None \
                and type(self.__currentWord.content["translation"]) is str:

                translations = self.__currentWord.content["translation"].split("\n")
                for i, translation in enumerate(translations):
                    self._group.add(utils.Sprite(self._defaultFont.render(translation, True, self._font_color), 150, 230 + i * 40))
                    
            answer = self._characterFont.render(self.__currentWord.word, True, [200,0,100])
            answer_rect = answer.get_rect()
            pos_x = (self.width - answer_rect.width) // 2
            pos_y = (self.height - answer_rect.height) // 2
            self._group.add(utils.Sprite(answer, pos_x, pos_y))

            progress = f"progress: {self._book.index()}/{self._book.length()} | round: {self._book.round()}"
            progress_size = self._informationFont.size(progress)
            
            progress_x = self.width - self._span * 2 - progress_size[0]
            progress_y = self._span * 2
            self._group.add(utils.Sprite(self._informationFont.render(progress, True, self._font_color), progress_x, progress_y))
            
            self.UpdateStatus()

        except StopIteration:
            self._iter = None
            
        return True

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("兔哥背单词")
    scene = PrepareScene((1280, 1024))

    utils.ResourceManager.add("phonetic/en.zip")
    utils.SceneManager.AddScene("Prepare", scene, True)
    
    while not utils.ResourceManager.is_done():
        print("Loading...")
        time.sleep(1)
    
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()