from __future__ import annotations
import os
import sys
import random
from typing import Iterable

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from scenes import PrepareScene
from core import Book, Word, CharSequence
import stardict

dictionary = stardict.StarDict("dict.db")
class RememberScene(utils.Scene):
    def __init__(self, size: tuple[int, int]):
        super().__init__("Remember", size, 5, 1)
        
        self.__book: Book = Book("xuchenhao")
        self.__iter: Iterable[Word] | None = None
        self.__defaultFont: pygame.font.Font = utils.FontManager.GetFont("font/msyh.ttc", 24)
        self.__CharacterFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 24)
        self.__informationFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 18)
        self.__phoneticFont: pygame.font.Font = utils.FontManager.GetFont("calibri", 24)
        self.__group: pygame.sprite.Group = pygame.sprite.Group()
        self.__statusbar: pygame.sprite.Group = pygame.sprite.Group()
        self.__wrong: int = 0
        self.__crack: bool = False
        self.__word_waiting_from: int = 0
        self.__word_status: int = 0 # 0: enter， 1：right， 2：waiting for next
        self.__currentSequence = None
        self.__firework_lasttime = pygame.time.get_ticks()
        self.__fireworks = utils.Fireworks()
        
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        selectedFile = "books/test.txt"
        if isinstance(prevScene, PrepareScene):
            selectedFile = prevScene.GetSelectedFile()
        
        if selectedFile is None or selectedFile == "":
            return
        
        if self.__book.load(selectedFile, dictionary):
            self.Next()

    def _onLeave(self) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if self.__currentSequence is None:
            utils.SceneManager.Switch("Books")
            return

        # 只有在输入状态下才能输入
        if self.__word_status != 0:
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
    
    def _onUIEvent(self, event: pygame.Event) -> None:
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
            # 显示音标
            pron = utils.Sprite(self.__phoneticFont.render(self.__currentWord.content["phonetic"], True, [255,255,255]), 10, 40)
            self.__group.add(pron)
            # 播放单词发音
            self.__currentWord.play()
            # 回答正确，正确次数 +1
            self.__book.right(self.__currentWord)
            self.__word_status = 1
        else:
            self.__crack = False
            self.__wrong = 0
            self.__word_status = 1
            
        self.UpdateStatus()

    
    def Next(self) -> bool:
        if self.__book is None:
            return False
        
        if self.__iter is None:
            self.__iter = iter(self.__book)
        
        try:
            # get next word
            self.__currentWord = next(self.__book)
            self.__wrong = 0
            self.__word_status = 0
            self.__group.empty()
            
            if "translation" in self.__currentWord.content \
                and self.__currentWord.content["translation"] is not None \
                and type(self.__currentWord.content["translation"]) is str:
                    
                translations = self.__currentWord.content["translation"].split("\n")
                for i, translation in enumerate(translations):
                    self.__group.add(utils.Sprite(self.__defaultFont.render(translation, True, [255,255,255]), 10, 70 + i * 30))
                    
            self.__currentSequence = CharSequence(self.__currentWord.word, self.width // 2, self.height - 100, self.__CharacterFont)
            self.__group.add(self.__currentSequence)

            progress = f"progress: {self.__book.index()}/{self.__book.length()} | round: {self.__book.round()}"
            progress_size = self.__informationFont.size(progress)
            
            progress_x = self.width - self._span * 2 - progress_size[0]
            progress_y = self._span * 2
            self.__group.add(utils.Sprite(self.__informationFont.render(progress, True, [255,255,255]), progress_x, progress_y))
            
            self.UpdateStatus()

        except StopIteration:
            self.__currentSequence = None
            return False
            
        return True
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
        if self.__currentSequence is None:
            self.__group.empty()
            congratulation = self.__defaultFont.render("Congratulations! You have finished the exercise!", True, [255,255,255])
            self.__group.add(utils.Sprite(congratulation, (self.width - congratulation.width) // 2, (self.height - congratulation.height) // 2))
            
            if self.__firework_lasttime + 1000 < pygame.time.get_ticks():
                self.__firework_lasttime = pygame.time.get_ticks()
                self.__fireworks.add(
                    random.randint(self.width // 4, self.width // 4 * 3), 
                    random.randint(self.height // 4, self.height // 2)
                )
                
            self.__fireworks.update()
            
        
        if self.__word_status == 1:
            self.__word_status = 2
            self.__word_waiting_from = pygame.time.get_ticks()
            
        if self.__word_status == 2 and pygame.time.get_ticks() - self.__word_waiting_from > 1000:
            self.Next()

        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        if self.__currentSequence is not None:
            pygame.draw.line(surface,
                (255, 255, 255),
                (0 + self._span, self.height - self._span * 2 - self.__currentSequence.height()), 
                (self.width - self._span - self._border, self.height - self._span * 2 - self.__currentSequence.height()), 
                1
            )
        
        self.__group.draw(surface)
        self.__statusbar.draw(surface)
        self.__fireworks.draw(surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("兔哥背单词")
    scene = RememberScene((800, 600))
    
    utils.SceneManager.AddScene("Remember", scene, True)

    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
