import json
import os
import sys
from xmlrpc.client import boolean
import pygame
import sqlite3
import logging

from dataclasses import dataclass, field

logging.basicConfig(filename='word.log', level=logging.DEBUG)
sys.path.append(os.path.abspath('../ECDICT/'))
import stardict
if not os.path.exists("dict.db"):
    stardict.convert_dict("dict.db", "../ECDICT/ecdict.csv")

dictionary = stardict.StarDict("dict.db")
# Connect to the SQLite database
connection = sqlite3.connect('users.db')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

create_user = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    book TEXT NOT NULL,
);
"""

@dataclass
class Word:
    word: str = field(init=True)
    count: int = 0
    wrong: int = 0
    right: int = 0
    proficiency: int = 0
    content: dict[str,str] = field(default_factory=dict[str,str])
    
class Book:
    '''
    单词书，要背的单词都在单词书里面。会定期进行复习。
    '''
    book_create_table = """
    CREATE TABLE IF NOT EXISTS {tablename} (
        word TEXT PRIMARY KEY,
        count INTEGER NOT NULL DEFAULT 0,
        wrong INTEGER NOT NULL DEFAULT 0,
        right INTEGER NOT NULL DEFAULT 0,
        proficiency INTEGER NOT NULL DEFAULT 100,
        content TEXT
    );
    """

    book_insert_word = """
        INSERT OR REPLACE INTO {tablename} (word, count, wrong, right, proficiency, content)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    book_load_query = """
        SELECT word, count, wrong, right, proficiency, content FROM {tablename} where proficiency < 100
    """
    
    book_update_wrong = """
        UPDATE {tablename} SET wrong = wrong + 1, proficiency = proficiency + ? where word = ?
    """
    
    book_update_right = """
        UPDATE {tablename} SET right = right + 1, proficiency = proficiency + ? where word = ?
    """
    
    def __init__(self, user:str, name:str, dictionary: stardict.StarDict):
        self.dirty = False
        self.words: list[Word] = []
        self.user = user
        self.name = name
        self.tablename = f"{self.user}-{self.name}"
        self.iter = 0
        self.dictionary = dictionary
        
    def __new(self):
        '''
        从文件中新建单词书，单词每行一个，也可以是词组或固定搭配。
        '''
        f = open(os.path.join("book", self.name + ".txt"))
        try:
            lines = f.readlines()
            words = [ln[:-1] for ln in lines]
            for word in words:
                info = self.dictionary.query(word)
                if info is not None:
                    cursor.execute(self.book_insert_word.format(tablename=self.tablename), (info.word, 0, 0, 0, 0, ""))
            
            connection.commit()
            
        except Exception as e:
            print(e)

    def isEmpty(self):
        return len(self.words) == 0
    
    def exists(self) -> bool:
        if not self.tablename.isalnum():
            raise ValueError("Table name must be alphanumeric")
        
        # Query to check if table exists
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (self.tablename,))
        
        result = cursor.fetchone()
        
        # If result is not None, the table exists
        return result is not None
    
    def load(self) -> bool:
        '''
        加载背过的单词书进行复习
        '''
        try:
            if not self.exists():
                self.__new()
            
            cursor.execute(self.book_load_query.format(tablename=self.tablename))
            for row in cursor.fetchall():
                w = Word(*row)
                info = self.dictionary.query(w.word)
                if info is not None:
                    w.content = info
                    self.words.append(w)

        except Exception as e:
            logging.error(f"{type(e)} - {e}")
            return False
        
        return True
    
    def __iter__(self):
        self.iter = 0
        return self

    def __next__(self):
        '''
        单词迭代，背会的单词会被从列表中剔除。
        '''
        if len(self.words) == 0:
            raise StopIteration
        
        while len(self.words):
            word = self.words[self.iter % len(self.words)]
            if word.proficiency > 100:
                del self.words[self.iter % len(self.words)] 
            else:
                self.iter += 1
                return word
        else:
            raise StopIteration

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x = 0, y = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(x, y, self.image.get_rect().width, self.image.get_rect().height)
    
    def height(self):
        return self.rect.height

    def width(self):
        return self.rect.width

class Letter(pygame.sprite.Sprite):
    '''
    单词拼写字母。
    '''
    def __init__(self, char: str="", x = 0, y = 0):
        pygame.sprite.Sprite.__init__(self)
        index = ord(char)
        self.char = char
        self.type = char
        self.last = 0
        self.texture = image
        self.rect = (x, y, letter_w, letter_h)
        self.set('_')
    
    def set(self, char):
        if char == None:
            return
        
        ch = ord(char)
        if ch >= ord(' ') and ch <= ord('~'):
            self.type = char

            ch -= ord(' ')
            self.image = self.texture.subsurface((ch * letter_w, 0, letter_w, letter_h))

    def reset(self):
        self.set('_')
        
    def press(self, char):
        self.set(char)

    def correct(self):
        return self.type == self.char

class CharSequence(pygame.sprite.Group):
    def __init__(self, word, x, y):
        pygame.sprite.Group.__init__(self)
        self.sequence = []
        self.x = x - len(word) * (letter_w + 1) / 2
        self.y = y - letter_h / 2
        self.judge = False
        self.complate = False

        for ch in word:
            self.sequence.append(Letter(ch, x, y))
            x += letter_w + 1

        # add to group
        for letter in self.sequence:
            self.add(letter)

        self.cursor = 0

    def press(self, char):
        if self.cursor < len(self.sequence):
            self.sequence[self.cursor].press(char if type(char) == "str" else chr(char))
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

    def complated(self):
        return self.complate

class Pronunciation(pygame.sprite.Group):
    def __init__(self, phonetic, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        en = Sprite(font.render(phonetic, True, [255,255,255]), x, y)
        self.add(en)

class Explain(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["explain"]:
            self.add(Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

class Example(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["example"]:
            self.add(Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

# define the screen wight and height
screen = pygame.display.set_mode((800, 600), 0, 32)
# load font to display
fonts = [
    pygame.font.SysFont(["Microsoft YaHei", "SimHei", "Lucida Sans Unicode", "sans-serif"], 20),
    pygame.font.SysFont("SimHei", 32), # Arial,Helvetica,Sans-Serif
    pygame.font.SysFont("Arial", 24),
    pygame.font.SysFont("Microsoft YaHei", 24),
]

# Calc the letter weight and height
str=""
for i in range(32, 126):
    str += chr(i)

image = fonts[1].render(str, True, [255,255,255])
image_rect = image.get_rect()
letter_w = image_rect.width / 94
letter_h = image_rect.height

# load book and prepare the data
b = Book('xuchenhao', 'M1U1', dictionary)
b.load()

running = True

mp3 = ""

for w in b:
    s = CharSequence(w.word, 400, 540)
    w.count += 1
    factor = 0.1

    g = pygame.sprite.Group()
    g.add(Sprite(fonts[0].render(w.content["phonetic"], True, [255,255,255]), 10, 10))
    g.add(Sprite(fonts[0].render(w.content["translation"], True, [255,255,255]), 10, 70))

    # mp3 = "./pronunciation/" + sound + "/" + w.word + ".mp3"
    # if os.path.exists(mp3):
    #     pygame.mixer.music.load(mp3)
    #     pygame.mixer.music.play()
    
    while running and not s.complated():
        tick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    s.backspace()
                elif event.key == pygame.K_DELETE:
                    s.delete()
                elif event.key == pygame.K_RETURN:
                    s.check()
                else:
                    s.press(event.key)

        screen.fill((0,0,0))
        # y = 100
        # for img in uniimg:
        #     screen.blit(img, (0, y))
        #     y += 30

        screen.blit(fonts[0].render("评价：%.1f 分" % (w.proficiency), True, (255,255,255)), (300, 10))
        screen.blit(fonts[0].render("用时：%5.2f 秒" % (tick/1000), True, (255,255,255)), (580, 10))
        
        s.update(tick)
        s.draw(screen)

        g.update(tick)
        g.draw(screen)

        pygame.display.update()
        pygame.display.flip()

    if not running:
        break

    if s.check():
        w.right += 1
        w.proficiency += 1
    else:
        w.wrong += 1
else:
    print("finished.")
    pass