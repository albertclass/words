import os
import sys
import math
import pygame
import sqlite3
import logging
import phonetic

from dataclasses import dataclass, field

logging.basicConfig(filename='word.log', level=logging.DEBUG)
sys.path.append(os.path.abspath('./ECDICT/'))
import stardict
if not os.path.exists("dict.db") and os.path.exists("./ECDICT/ecdict.csv"):
    stardict.convert_dict("dict.db", "./ECDICT/ecdict.csv")

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
    bingo: int = 0
    proficiency: int = 0
    content: dict[str,str] = field(default_factory=dict[str,str])
    sound: pygame.mixer.Sound | None = None
    delta: int = 100

    def play(self):
        if self.sound is None:
            filepath = os.path.join(os.path.abspath("./"), self.content["audio"])
            self.sound = pygame.mixer.Sound(filepath)

        self.sound.play(loops=0)
        
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
        bingo INTEGER NOT NULL DEFAULT 0,
        proficiency INTEGER NOT NULL DEFAULT 0,
        content TEXT
    );
    """

    book_insert_word = """
        INSERT OR REPLACE INTO {tablename} (word, count, wrong, right, proficiency, content)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    book_load_query = """
        SELECT word, count, wrong, right, bingo, proficiency, content FROM {tablename}
    """
    
    book_update_wrong = """
        UPDATE {tablename} SET count = count + 1, wrong = wrong + 1, proficiency = ?, bingo = 0 where word = ?
    """
    
    book_update_right = """
        UPDATE {tablename} SET count = count + 1, right = right + 1, proficiency = ?, bingo = bingo + 1 where word = ?
    """
    
    dict_update_audio = """
        UPDATE stardict SET audio = ? WHERE word = ?
    """
    
    def __init__(self, user:str, name:str, dictionary: stardict.StarDict):
        self.dirty = False
        self.words: list[Word] = []
        self.user = user
        self.name = name
        self.tablename = f"{self.user}_{self.name}"
        self.iter = 0
        self.dictionary = dictionary
        
    def __new(self):
        '''
        从文件中新建单词书，单词每行一个，也可以是词组或固定搭配。
        '''
        f = open(os.path.join("book", self.name + ".txt"))
        try:
            cursor.execute(self.book_create_table.format(tablename=self.tablename))
            lines = f.readlines()
            words = [ln[:-1] for ln in lines]
            for word in words:
                info = self.dictionary.query(word)
                if info is not None:
                    cursor.execute(self.book_insert_word.format(tablename=self.tablename), (word, 0, 0, 0, 0, ""))
            
            connection.commit()
            
        except Exception as e:
            print(e)

    def isEmpty(self):
        return len(self.words) == 0
    
    def updateAudio(self, audios: dict[str,str]):
        connection = sqlite3.connect('dict.db')
        cursor = connection.cursor()
        for word, audio in audios.items():
            cursor.execute(self.dict_update_audio, (audio, word))
        connection.commit()
        
    def exists(self) -> bool:
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
            
            yd = phonetic.youdao()
            
            cursor.execute(self.book_load_query.format(tablename=self.tablename))
            
            audios = {}
            for row in cursor.fetchall():
                w = Word(*row)
                w.bingo = 0
                w.delta = 50 if w.count == 0 else int(100 * (w.right / w.count))
                w.proficiency = 0 if w.count == 0 else int(100 * (w.right / w.count))
                if w.proficiency > 95:
                    continue
                info = self.dictionary.query(w.word)
                if info is not None:
                    if info["audio"] is None or info["audio"] == "":
                        phoneticPath = yd.down(w.word)
                        info["audio"] = phoneticPath
                        # update the word info
                        audios[w.word] = phoneticPath
                        
                    w.content = info
                    self.words.append(w)
            # Update the audio to db if audio is not exists.
            self.updateAudio(audios)
        except Exception as e:
            logging.error(f"{type(e)} - {e}")
            return False
        
        return True
    
    def right(self, word: Word):
        word.count += 1
        word.right += 1
        word.bingo = max(0, word.bingo) + 1
        word.proficiency += max(5, int(word.delta * 1.00) + word.bingo * 5) # less than 5 point to inc
        word.delta = int(100 * (w.right / w.count))
        cursor.execute(self.book_update_right.format(tablename=self.tablename), (word.proficiency, word.word))
        connection.commit()
        
    def wrong(self, word: Word):
        word.count += 1
        word.wrong += 1
        word.bingo = min(0, word.bingo) - 1
        word.proficiency -= max(5, int(word.delta * 1.25) + word.bingo * 5) # more than 5 point to dec
        word.proficiency = max(0, word.proficiency) # 熟练度最小为0
        word.delta = int(100 * (w.right / w.count))
        cursor.execute(self.book_update_wrong.format(tablename=self.tablename), (word.proficiency, word.word))
        connection.commit()
        
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
        self.char = char
        self.type = char
        self.last = 0
        self.rect = (x, y, letter_w, letter_h)
        self.set('_')
    
    def set(self, char):
        if char == None:
            return
        
        ch = ord(char)
        if ch >= ord(' ') and ch <= ord('~'):
            self.type = char

            ch -= ord(' ')
            self.image = letters_image.subsurface((ch * letter_w, 0, letter_w, letter_h))

    def reset(self):
        self.set('_')
        
    def press(self, char):
        return self.set(char)

    def correct(self):
        return self.type == self.char

class CharSequence(pygame.sprite.Group):
    def __init__(self, word, size: tuple[int, int]):
        pygame.sprite.Group.__init__(self)
        self.sequence: list[Letter] = []
        self.judge = False
        self.complate = False

        self.x = (size[0] - len(word) * (letter_w + 1) - 1) // 2
        self.y = (size[1] - letter_h - 60)

        x = self.x
        for ch in word:
            self.sequence.append(Letter(ch, x, self.y))
            x += letter_w + 1

        # add to group
        for letter in self.sequence:
            self.add(letter)

        self.cursor = 0

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
    pygame.font.SysFont(["Microsoft YaHei", "SimHei", "Lucida Sans Unicode", "dejavusans"], 24),
    pygame.font.SysFont("SimHei", 32), # Arial,Helvetica,Sans-Serif
    pygame.font.SysFont("Calibri", 24),
    pygame.font.SysFont("Microsoft YaHei", 32),
]

# Calc the letter weight and height
letters=""
for i in range(32, 126):
    letters += chr(i)

letters_image = fonts[1].render(letters, True, [255,255,255])
letters_image_rc = letters_image.get_rect()
letter_w = letters_image_rc.width // 94
letter_h = letters_image_rc.height

# load book and prepare the data
b = Book('xuchenhao', '20240810', dictionary)
b.load()

running = True

mp3 = ""

# 关闭输入法
pygame.key.stop_text_input()

# 开始背单词
for w in b:
    s = CharSequence(w.word, screen.get_size())
    g = pygame.sprite.Group()
    # show the phonetic
    # g.add(Sprite(fonts[2].render(w.content["phonetic"], True, [255,255,255]), 10, 40))
    # show the explain
    if "translation" in w.content \
        and w.content["translation"] is not None \
        and type(w.content["translation"]) is str:
            
        translations = w.content["translation"].split("\n")
        for i, translation in enumerate(translations):
            g.add(Sprite(fonts[0].render(translation, True, [255,255,255]), 10, 70 + i * 30))

    wrong = 0
    # wait = pygame.time.get_ticks()
    crack = False
    while running and not s.complated():
        tick = pygame.time.get_ticks()
            
        for event in pygame.event.get():
            # print(event.type, event.dict)

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.TEXTINPUT:
                pygame.key.stop_text_input()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    s.backspace()
                elif event.key == pygame.K_DELETE:
                    s.delete()
                elif event.key == pygame.K_RETURN:
                    if s.is_empty():
                        crack = True
                        # show correct spelling, if wrong more than 3 times
                        answer = fonts[3].render(w.word, True, [200,0,100])
                        answer_rect = answer.get_rect()
                        pos_x = (800 - answer_rect.width) // 2
                        pos_y = (600 - answer_rect.height) // 2
                        g.add(Sprite(answer, pos_x, pos_y))
                        s.reset()
                        w.play()
                    elif s.check() == False:
                        # 回答错误，错误次数 +1
                        wrong += 1
                        b.wrong(w)
                        s.reset()
                        
                        if wrong == 1:
                            # play the pronunciation, if wrong more than 1 times
                            w.play()
                        if wrong == 2:
                            # show the phonetic symbol, if wrong more than 2 times
                            g.add(Pronunciation(w.content["phonetic"], 10, 40, fonts[2]))
                        if wrong == 3:
                            # show correct spelling, if wrong more than 3 times
                            answer = fonts[3].render(w.word, True, [200,0,100])
                            answer_rect = answer.get_rect()
                            pos_x = (800 - answer_rect.width) // 2
                            pos_y = (600 - answer_rect.height) // 2
                            g.add(Sprite(answer, pos_x, pos_y))
                            break
                    elif not crack:
                        # 回答正确，正确次数 +1
                        b.right(w)
                        pygame.time.wait(1000)
                # elif event.mod & pygame.KMOD_SHIFT:
                #     s.press(event.key)
                elif len(event.unicode) > 0:
                    s.press(event.unicode)
                    
        screen.fill((0,0,0))

        screen.blit(fonts[0].render(f"评价：{w.proficiency:1f} 分", True, (255,255,255)), (300, 10))
        screen.blit(fonts[0].render(f"用时：{tick/1000:5.2f} 秒", True, (255,255,255)), (580, 10))
        
        s.update(tick)
        s.draw(screen)

        g.update(tick)
        g.draw(screen)

        pygame.display.update()
        pygame.display.flip()

    if not running:
        break
else:
    print("finished.")
    pass