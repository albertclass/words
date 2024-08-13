import os
import pygame
import utils
from dataclasses import dataclass, field

@dataclass
class Word:
    word: str = field(init=True)
    count: int = 0
    wrong: int = 0
    right: int = 0
    bingo: int = 0
    proficiency: int = 0
    content: dict[str,str] = field(default_factory=dict[str,str])
    sound: pygame.mixer.Sound | None = None
    delta: int = 100

    def play(self):
        if self.sound is None:
            filepath = os.path.join('phonetic', 'en', self.content["audio"])
            self.sound = utils.ResourceManager.loadSound(filepath)
            # if os.path.exists(filepath):
            #     self.sound = pygame.mixer.Sound(filepath)
            # elif os.path.exists(os.path.join('phonetic', 'en.zip')):
            #     with zipfile.ZipFile(os.path.join('phonetic', 'en.zip')) as zfile:
            #         with zfile.open(self.content["audio"] if sys.platform == "linux" else self.content["audio"].replace("\\", "/") ) as file:
            #             buffer = io.BytesIO(file.read())
            #             self.sound = pygame.mixer.Sound(buffer)
                
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
    def __init__(self, char: str, x = 0, y = 0, font: pygame.font.Font | str = "Calibri"):
        if type(font) == str:
            font = utils.FontManager.GetFont(font, 24)
        elif type(font) == pygame.font.Font:
            self.font = font

        super().__init__(self.font.render(char, True, [255,255,255]), x, y)
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
            self.UpdateSurface(self.font.render(char, True, [255,255,255]))

    def reset(self):
        self.set('_')
        
    def press(self, char):
        return self.set(char)

    def correct(self):
        return self.type == self.char

class CharSequence(pygame.sprite.Group):
    def __init__(self, word, x, y, font: pygame.font.Font | str = "Calibri"):
        super().__init__()
        self.sequence: list[Letter] = []
        self.judge = False
        self.complate = False

        self.x = x
        self.y = y

        self.__width = self.x
        self.__height = 0
        self.__word = word
        
        for char in word:
            letter = Letter(char, self.__width, self.y, font)
            self.sequence.append(letter)
            letter_size = letter.size()
            self.__width += letter_size[0] + 1

        # add to group
        for letter in self.sequence:
            self.__height = max(self.__height, letter.size()[1])
            self.add(letter)

        self.cursor = 0

    def __str__(self) -> str:
        return self.__word
    
    def press(self, char):
        if self.cursor < len(self.sequence) and ord(char) > ord(' ') and ord(char) < ord('~'):
            self.sequence[self.cursor].press(char if type(char) == str else chr(char))
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
