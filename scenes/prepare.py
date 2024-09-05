from __future__ import annotations
import os
import sys
import time
from typing import Iterable

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from scenes import BooksScene
from core import Book, Word
import stardict

dictionary = stardict.StarDict("dict.db")

class PrepareScene(utils.Scene):
    def __init__(self, size: tuple[int, int], span: int = 2, border: int = 1):
        super().__init__("Prepare Scene", size, span, border)
        self.__book: Book = Book("xuchenhao")
        self.__iter: Iterable[Word] | None = None
        self.__defaultFont: pygame.font.Font = utils.FontManager.GetFont("font/msyh.ttc", 24)
        self.__CharacterFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 48)
        self.__informationFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 18)
        self.__phoneticFont: pygame.font.Font = utils.FontManager.GetFont("calibri", 24)
        self.__group: pygame.sprite.Group = pygame.sprite.Group()
        self.__statusbar: pygame.sprite.Group = pygame.sprite.Group()
        self.__selectedFile: str = ""
        
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        self.__selectedFile = 'books/中考考纲词汇【自动】/0001-0050.txt'
        if isinstance(prevScene, BooksScene):
            self.__selectedFile = prevScene.GetSelectedFile()

        if self.__selectedFile is None or self.__selectedFile == "":
            return
        
        if self.__book.load(self.__selectedFile, dictionary):
            self.Next()
    
    def _onLeave(self) -> None:
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
        self.__statusbar.empty()
        info = f"right {self.__currentWord.totalWrong} | wrong {self.__currentWord.totalRight} | bingo: {self.__currentWord.bingo} | proficiency: {self.__currentWord.proficiency} | delta: {self.__currentWord.delta}"
        info_size = self.__informationFont.size(info)
        
        info_x = self.width - info_size[0] - self._span * 2
        if info_x < 0 :
            info_x = 0
        
        background = pygame.Surface((self.width - self._span * 2 - self._border * 2, info_size[1] + self._span * 2 - self._border * 2))
        background.fill((0,0,200))
        
        self.__statusbar.add(utils.Sprite(background, self._span + self._border, self.height - info_size[1] - self._span * 3))
        self.__statusbar.add(utils.Sprite(self.__informationFont.render(info, True, [255,255,255]), info_x , self.height - info_size[1] - self._span * 2))

    def Update(self, *args, **kwargs) -> bool:
        if self.__iter is None:
            self.__group.empty()
            congratulation = self.__defaultFont.render("Congratulations! You have finished the exercise!", True, [255,255,255])
            self.__group.add(utils.Sprite(congratulation, (self.width - congratulation.width) // 2, (self.height - congratulation.height) // 2))
        
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        pygame.draw.line(surface,
            (255, 255, 255),
            (0 + self._span, self.height - self._span * 2 - 24), 
            (self.width - self._span - self._border, self.height - self._span * 2 - 24), 
            1
        )
        
        self.__group.draw(surface)
        self.__statusbar.draw(surface)

    def Next(self) -> bool:
        if self.__book is None:
            return False
        
        if self.__iter is None:
            self.__iter = iter(self.__book)
        
        try:
            # get next word
            self.__currentWord = next(self.__book)
            self.__currentWord.play()
            self.__group.empty()
            
            self.__group.add(utils.Sprite(self.__phoneticFont.render(self.__currentWord.content["phonetic"], True, [255,255,255]), 10, 40))

            if "translation" in self.__currentWord.content \
                and self.__currentWord.content["translation"] is not None \
                and type(self.__currentWord.content["translation"]) is str:

                translations = self.__currentWord.content["translation"].split("\n")
                for i, translation in enumerate(translations):
                    self.__group.add(utils.Sprite(self.__defaultFont.render(translation, True, [255,255,255]), 10, 70 + i * 30))
                    
            answer = self.__CharacterFont.render(self.__currentWord.word, True, [200,0,100])
            answer_rect = answer.get_rect()
            pos_x = (self.width - answer_rect.width) // 2
            pos_y = (self.height - answer_rect.height) // 2
            self.__group.add(utils.Sprite(answer, pos_x, pos_y))

            progress = f"progress: {self.__book.index()}/{self.__book.length()} | round: {self.__book.round()}"
            progress_size = self.__informationFont.size(progress)
            
            progress_x = self.width - self._span * 2 - progress_size[0]
            progress_y = self._span * 2
            self.__group.add(utils.Sprite(self.__informationFont.render(progress, True, [255,255,255]), progress_x, progress_y))
            
            self.UpdateStatus()

        except StopIteration:
            self.__iter = None
            
        return True

    def GetSelectedFile(self) -> str:
        return self.__selectedFile

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