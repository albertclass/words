from __future__ import annotations
import os
import sys
import random
from typing import Iterable

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from core import Book, Word, CharSequence
import stardict

dictionary = stardict.StarDict("dict.db")
class RememberScene(utils.Scene):
    def __init__(self, size: tuple[int, int]):
        super().__init__("Remember", size, 5, 1)
        
        self._book: Book = Book()
        self._iter: Iterable[Word] | None = None
        self._defaultFont: pygame.font.Font = utils.FontManager.GetFont("font/msyh.ttc", 24)
        self._charactorFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 48)
        self._informationFont: pygame.font.Font = utils.FontManager.GetFont("Consolas", 18)
        self._phoneticFont: pygame.font.Font = utils.FontManager.GetFont("calibri", 24)
        self._group: pygame.sprite.Group = pygame.sprite.Group()
        self._statusbar: pygame.sprite.Group = pygame.sprite.Group()
        self._wrong: int = 0
        self._crack: bool = False
        self._word_waiting_from: int = 0
        self._word_status: int = 0 # 0: enter， 1：right， 2：waiting for next
        self._currentSequence = None
        self._firework_lasttime = pygame.time.get_ticks()
        self._fireworks = utils.Fireworks()
        self._font_color = (0,0,0)
        self._border_color = (0,0,0)
        self._statusbar_color = (50, 50, 178)

        self.background_image = pygame.image.load("images/background-3.png")

        charactor = pygame.image.load("images/CH00171.png")
        actions: dict[str, utils.SpriteFrameAnim] = {
            "left":      utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 0, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "upleft":    utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 1, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "up":        utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 2, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "upright":   utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 3, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "right":     utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 4, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "downright": utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 5, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "down":      utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 6, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
            "downleft":  utils.SpriteFrameAnim(charactor.subsurface((0, 1024 // 8 * 7, 1024, 1024 // 8)), 1, 8, utils.SpriteFrameAnim.Mode.ROW, interval=0.125),
        }

        self._charactor: utils.Charactor = utils.Charactor("Albert", 2, actions = actions)
        self._charactor.setAction("down")
        self._charactor.hotspot = (int(self._charactor.width // 2), int(self._charactor.height // 2))
        self._charactor.speed = 2
        self._charactor.move(0, 0)

    def _onEnter(self, prevScene: utils.Scene | None, *params, **kwargs) -> None:
        book = utils.SceneManager.GetSceneProperty("Books", "book")
        if isinstance(book, Book):
            self._book = book
            self.Next()

        self._charactor.move(0, 300)

    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if self._currentSequence is None:
            utils.SceneManager.Switch("Books")
            return

        # 只有在输入状态下才能输入
        if self._word_status != 0:
            return
        
        if event.key == pygame.K_ESCAPE: 
            utils.SceneManager.Switch("Books")
        if event.key == pygame.K_BACKSPACE: 
            self._currentSequence.backspace()
        elif event.key == pygame.K_DELETE:
            self._currentSequence.delete()
        elif event.key == pygame.K_RETURN:
            self._onReturn()
        elif len(event.unicode) > 0:
            self._currentSequence.press(event.unicode)
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        self._charactor.walk(event.pos[0], event.pos[1])
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.Event) -> None:
        pass
    
    def _onReturn(self) -> None:
        if self._currentSequence is None:
            return
        
        if self._currentSequence.is_empty():
            self._crack = True
            # show correct spelling, if wrong more than 3 times
            answer = self._charactorFont.render(str(self._currentSequence), True, (200,0,100))
            answer_rect = answer.get_rect()
            pos_x = (self.width - answer_rect.width) // 2
            pos_y = (self.height - answer_rect.height) // 2
            self._group.add(utils.Sprite(answer, pos_x, pos_y))
            self._currentSequence.reset()
            self.__currentWord.play()
        elif not self._currentSequence.check():
            # 回答错误，错误次数 +1
            self._wrong += 1
            self._book.wrong(self.__currentWord)
            self._currentSequence.reset()
            
            if self._wrong == 1:
                # play the pronunciation, if wrong more than 1 times
                self.__currentWord.play()
            if self._wrong == 2:
                # show the phonetic symbol, if wrong more than 2 times
                pron = utils.Sprite(self._phoneticFont.render(self.__currentWord.content["phonetic"], True, self._font_color), 150, 190)
                self._group.add(pron)
            if self._wrong == 3:
                # show correct spelling, if wrong more than 3 times
                answer = self._charactorFont.render(self.__currentWord.word, True, (200,0,100))
                answer_rect = answer.get_rect()
                pos_x = (self.width - answer_rect.width) // 2
                pos_y = (self.height - answer_rect.height) // 2
                self._group.add(utils.Sprite(answer, pos_x, pos_y))
                self._crack = True
        elif not self._crack:
            # 显示音标
            pron = utils.Sprite(self._phoneticFont.render(self.__currentWord.content["phonetic"], True, self._font_color), 150, 190)
            self._group.add(pron)
            # 播放单词发音
            self.__currentWord.play()
            # 回答正确，正确次数 +1
            self._book.right(self.__currentWord)
            self._word_status = 1
        else:
            self._crack = False
            self._wrong = 0
            self._word_status = 1
            
        self.UpdateStatus()

    
    def Next(self) -> bool:
        if self._book is None:
            return False
        
        if self._iter is None:
            self._iter = iter(self._book)
        
        try:
            # get next word
            self.__currentWord = next(self._book)
            self._wrong = 0
            self._word_status = 0
            self._group.empty()
            
            if "translation" in self.__currentWord.content \
                and self.__currentWord.content["translation"] is not None \
                and type(self.__currentWord.content["translation"]) is str:
                    
                translations = self.__currentWord.content["translation"].split("\n")
                for i, translation in enumerate(translations):
                    self._group.add(utils.Sprite(self._defaultFont.render(translation, True, self._font_color), 150, 230 + i * 40))
                    
            self._currentSequence = CharSequence(self.__currentWord.word, self.width // 2, self.height - 100, self._charactorFont)
            self._group.add(self._currentSequence)

            progress = f"progress: {self._book.index()}/{self._book.length()} | round: {self._book.round()}"
            progress_size = self._informationFont.size(progress)
            
            progress_x = self.width - self._span * 2 - progress_size[0]
            progress_y = self._span * 2
            self._group.add(utils.Sprite(self._informationFont.render(progress, True, self._font_color), progress_x, progress_y))
            
            self.UpdateStatus()

        except StopIteration:
            self._currentSequence = None
            return False
            
        return True
    
    def UpdateStatus(self) -> None:
        self._statusbar.empty()
        info = f"right {self.__currentWord.right} | wrong {self.__currentWord.wrong} | bingo: {self.__currentWord.bingo}"
        info_size = self._informationFont.size(info)
        
        info_x = self.width - info_size[0] - self._span * 2
        if info_x < 0 :
            info_x = 0
        
        # background = pygame.Surface((self.width - self._span * 2 - self._border * 2, info_size[1] + self._span * 2 - self._border * 2))
        # background.fill(self._statusbar_color)
        
        # self._statusbar.add(utils.Sprite(background, self._span + self._border, self.height - info_size[1] - self._span * 3))
        self._statusbar.add(utils.Sprite(self._informationFont.render(info, True, self._font_color), info_x , self.height - info_size[1] - self._span * 2))

    def Update(self, *args, **kwargs) -> bool:
        if self._currentSequence is None:
            # 全部背完了， 开始放烟花
            if self._firework_lasttime + 1000 < pygame.time.get_ticks():
                self._firework_lasttime = pygame.time.get_ticks()
                self._fireworks.add(
                    random.randint(self.width // 4, self.width // 4 * 3), 
                    random.randint(self.height // 4, self.height // 2)
                )
                
            self._fireworks.update()
            
        
        if self._word_status == 1:
            self._word_status = 2
            self._word_waiting_from = pygame.time.get_ticks()
            
        if self._word_status == 2 and pygame.time.get_ticks() - self._word_waiting_from > 1000:
            self.Next()
            if self._currentSequence is None:
                # 背完了，更新状态
                self._group.empty()
                congratulation = self._defaultFont.render("Congratulations! You have finished the exercise!", True, self._font_color)
                self._group.add(utils.Sprite(congratulation, (self.width - congratulation.width) // 2, (self.height - congratulation.height) // 2))

        self._charactor.update()
        self._group.update()
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self._border_color, (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        if self._currentSequence is not None:
            pygame.draw.line(surface,
                self._border_color,
                (0 + self._span, self.height - self._span * 2 - self._currentSequence.height()), 
                (self.width - self._span - self._border, self.height - self._span * 2 - self._currentSequence.height()), 
                1
            )
        
        self._group.draw(surface)
        self._charactor.draw(surface)
        self._statusbar.draw(surface)
        self._fireworks.draw(surface)


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
