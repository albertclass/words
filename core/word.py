import os
import pygame
import utils

class Word:
    def __init__(self, word: str, content: dict[str, str] | None):
        self.word: str = word
        self.wrong: int = 0
        self.right: int = 0
        self.bingo: int = 0
        self.content: dict[str, str] = content or {}
        self.sound: pygame.mixer.Sound | None = None
        ret, sound = utils.SimpleTTS().load(self.word)
        if ret:
            self.sound = pygame.mixer.Sound(sound)
        
    def play(self):
        if self.sound is not None:
            self.sound.play(loops=0)

    def __str__(self) -> str:
        return self.word

class Pronunciation(pygame.sprite.Group):
    def __init__(self, phonetic, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        en = utils.Sprite(font.render(phonetic, True, [255,255,255]), x, y)
        self.add(en)

class Explain(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["explain"]:
            self.add(utils.Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

class Example(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["example"]:
            self.add(utils.Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

class Letter(utils.Sprite):
    '''
    单词拼写字母。
    '''
    def __init__(self, char: str, x = 0, y = 0, font: pygame.font.Font | str = "Consolas"):
        if type(font) is str:
            font = utils.FontManager.GetFont(font, 24)
        elif type(font) is pygame.font.Font:
            self.font = font

        super().__init__(self.font.render(char, True, [0,0,0]), x, y)
        self.char = char
        self.type = char
        self.last = 0
        self.set('_')
        
        self.__size = self.font.size(self.char)
        self.rect = pygame.Rect(x, y, self.__size[0], self.__size[1])
    
    def size(self):
        return self.__size
    
    def set(self, char):
        if char == None:
            return
        
        val = ord(char)
        if val >= ord(' ') and val <= ord('~'):
            self.type = char
            self.image = self.font.render(char, True, [0,0,0])

    def reset(self):
        self.set('_')
        
    def press(self, char):
        return self.set(char)

    def correct(self):
        return self.type == self.char
    
class CharSequence(pygame.sprite.Group):
    def __init__(self, word, x, y, font: pygame.font.Font):
        super().__init__()
        self.sequence: list[Letter] = []
        self.judge = False
        self.complate = False

        self.__max_character_width = 0
        self.__height = 0
        self.__character_span = 2
        self.font = font
        for char in word:
            self.__max_character_width = max(self.font.size(char)[0], self.__max_character_width)
            self.__height = max(self.font.size(char)[1], self.__height)
            
        self.__width  = self.__max_character_width * len(word) + (len(word) - 1) * self.__character_span
        self.x = x - self.__width // 2
        self.y = y - self.__height // 2

        self.__word = word
        
        for idx in range(len(word)):
            letter = Letter(word[idx], self.x + idx * (self.__max_character_width + self.__character_span), self.y, font)
            self.sequence.append(letter)
            letter_size = letter.size()
            self.__width += letter_size[0] + self.__character_span
            self.add(letter)

        self.cursor = 0

    def __str__(self) -> str:
        return self.__word
    
    def press(self, char):
        if self.cursor < len(self.sequence) and ord(char) > ord(' ') and ord(char) < ord('~'):
            self.sequence[self.cursor].press(char if type(char) is str else chr(char))
            self.cursor += 1

    def delete(self):
        if self.cursor >= 0 and self.cursor < len(self.sequence):
            self.sequence[self.cursor].reset()

    def backspace(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.delete()

    def check(self):
        if not self.judge:
            # judge word is correct
            for ch in self.sequence:
                if not ch.correct():
                    break
            else:
                self.judge = True
                self.complate = True

        return self.judge
    def is_empty(self):
        return self.cursor == 0
    
    def reset(self):
        for ch in self.sequence:
            ch.reset()
        self.judge = False
        self.complate = False
        self.cursor = 0
        
    def complated(self):
        return self.complate

    def width(self):
        return self.__width
    
    def height(self):
        return self.__height
    
    def moveto(self, x, y):
        self.x = x - self.__width // 2
        self.y = y - self.__height // 2
        
        for idx in range(len(self.sequence)):
            self.sequence[idx].MoveTo(self.x + idx * (self.__max_character_width + self.__character_span), self.y)
