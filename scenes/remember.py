from __future__ import annotations
import os
import sys
from typing import Iterable
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from scenes import BooksScene
from core import Book, CharSequence
import stardict

dictionary = stardict.StarDict("dict.db")
class RememberScene(utils.Scene):
    def __init__(self, width: int, height: int):
        super().__init__("Remember", width, height)
        
        self.__span = 5
        self.__book: Book = Book("xuchenhao")
        self.__iter: Iterable | None = None
        self.__defaultFont: pygame.font.Font = pygame.font.SysFont(["Microsoft YaHei", "Lucida Sans Unicode"], 24)
        self.__phoneticFont: pygame.font.Font = pygame.font.SysFont("Calibri", 24)
        self.__group: pygame.sprite.Group = pygame.sprite.Group()
        self.__wrong: int = 0
        self.__crack: bool = False
        self.__currentSequence = None
        
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        if not isinstance(prevScene, BooksScene):
            return
        
        selectedFile = prevScene.GetSelectedFile()
        if selectedFile is None:
            return
        
        if self.__book.load(selectedFile.GetName(), dictionary):
            self.Next()

    def _onLeave(self) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if self.__currentSequence is None:
            utils.SceneManager.Switch("Books")
            return

        if event.key == pygame.K_BACKSPACE: 
            self.__currentSequence.backspace()
        elif event.key == pygame.K_DELETE:
            self.__currentSequence.delete()
        elif event.key == pygame.K_RETURN:
            self._onReturn()
        elif len(event.unicode) > 0:
            self.__currentSequence.press(event.unicode)
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onReturn(self) -> None:
        if self.__currentSequence is None:
            return
        
        if self.__currentSequence.is_empty():
            self.__crack = True
            # show correct spelling, if wrong more than 3 times
            answer = self.__defaultFont.render(str(self.__currentSequence), True, [200,0,100])
            answer_rect = answer.get_rect()
            pos_x = (800 - answer_rect.width) // 2
            pos_y = (600 - answer_rect.height) // 2
            self.__group.add(utils.Sprite(answer, pos_x, pos_y))
            self.__currentSequence.reset()
            self.__currentWord.play()
        elif self.__currentSequence.check() == False:
            # 回答错误，错误次数 +1
            self.__wrong += 1
            self.__book.wrong(self.__currentWord)
            self.__currentSequence.reset()
            
            if self.__wrong == 1:
                # play the pronunciation, if wrong more than 1 times
                self.__currentWord.play()
            if self.__wrong == 2:
                # show the phonetic symbol, if wrong more than 2 times
                pron = utils.Sprite(self.__phoneticFont.render(self.__currentWord.content["phonetic"], True, [255,255,255]), 10, 40)
                self.__group.add(pron)
            if self.__wrong == 3:
                # show correct spelling, if wrong more than 3 times
                answer = self.__defaultFont.render(self.__currentWord.word, True, [200,0,100])
                answer_rect = answer.get_rect()
                pos_x = (800 - answer_rect.width) // 2
                pos_y = (600 - answer_rect.height) // 2
                self.__group.add(utils.Sprite(answer, pos_x, pos_y))
                self.__crack = True
        elif not self.__crack:
            # 回答正确，正确次数 +1
            self.__book.right(self.__currentWord)
            self.__wrong = 0
            self.Next()
        else:
            self.__crack = False
            self.__wrong = 0
            self.Next()

    
    def Next(self) -> bool:
        if self.__book is None:
            return False
        
        if self.__iter is None:
            self.__iter = iter(self.__book)
        
        try:
            # get next word
            self.__currentWord = next(self.__iter)
            self.__group.empty()
            
            x = (self.width() - self.__defaultFont.size(self.__currentWord.word)[0] - len(self.__currentWord.word)) // 2
            self.__currentSequence = CharSequence(self.__currentWord.word, x, self.height() - 100, self.__defaultFont)
            
            if "translation" in self.__currentWord.content \
                and self.__currentWord.content["translation"] is not None \
                and type(self.__currentWord.content["translation"]) is str:
                    
                translations = self.__currentWord.content["translation"].split("\n")
                for i, translation in enumerate(translations):
                    self.__group.add(utils.Sprite(self.__defaultFont.render(translation, True, [255,255,255]), 10, 70 + i * 30))
            
            self.__group.add(self.__currentSequence)

        except StopIteration:
            self.__currentSequence = None
            return False
            
        return True

    def Update(self, *args, **kwargs) -> bool:
        if self.__currentSequence is None:
            self.__group.empty()
            congratulation = self.__defaultFont.render("Congratulations! You have finished the exercise!", True, [255,255,255])
            self.__group.add(utils.Sprite(congratulation, (self.width() - congratulation.width) // 2, (self.height() - congratulation.height) // 2))
        
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (self.__span, self.__span, self.width() - self.__span * 2, self.height() - self.__span * 2), 1, 5)
        self.__group.draw(surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("兔哥背单词")
    scene = RememberScene(800, 600)
    
    utils.SceneManager.AddScene("Remember", scene, True)

    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
