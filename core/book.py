import os
import sqlite3
import random
import stardict
import utils
import logging
import hashlib
from .word import Word

# Connect to the SQLite database
connection = sqlite3.connect('users.db')
cursor = connection.cursor()

class Book:
    '''
    单词书，要背的单词都在单词书里面。会定期进行复习。
    '''
    __book_create_table = """
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

    __book_insert_word = """
        INSERT OR REPLACE INTO {tablename} (word, count, wrong, right, proficiency, content)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    __book_load_query = """
        SELECT word, count, wrong, right, bingo, proficiency, content FROM {tablename}
    """
    
    __book_update_wrong = """
        UPDATE {tablename} SET count = count + 1, wrong = wrong + 1, proficiency = ?, bingo = 0 where word = ?
    """
    
    __book_update_right = """
        UPDATE {tablename} SET count = count + 1, right = right + 1, proficiency = ?, bingo = bingo + 1 where word = ?
    """
    
    __dict_update_audio = """
        UPDATE stardict SET audio = ? WHERE word = ?
    """
    
    def __init__(self, user: str):
        self.dirty = False
        self.__words: list[Word] = []
        self.__user = user
        self.__iter = 0
        self.__round = 0
    
    def __new(self, pathname: str | os.PathLike, dictionary: stardict.StarDict):
        '''
        从文件中新建单词书，单词每行一个，也可以是词组或固定搭配。
        '''
        f = open(pathname, "r", encoding="utf-8")
        try:
            cursor.execute(self.__book_create_table.format(tablename=self.__tablename))
            lines = f.readlines()
            words = [ln[:-1] for ln in lines]
            # shuffle the list
            random.shuffle(words)
            for word in words:
                info = dictionary.query(word)
                if info is not None:
                    cursor.execute(self.__book_insert_word.format(tablename=self.__tablename), (word, 0, 0, 0, 0, ""))
            
            connection.commit()
            
        except Exception as e:
            print(e)

    def isEmpty(self):
        return len(self.__words) == 0
    
    def updateAudio(self, audios: dict[str,str]):
        connection = sqlite3.connect('dict.db')
        cursor = connection.cursor()
        for word, audio in audios.items():
            cursor.execute(self.__dict_update_audio, (audio, word))
        connection.commit()
        
    def exists(self, tablename: str) -> bool:
        # Query to check if table exists
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor.execute(query, (tablename,))
        
        result = cursor.fetchone()
        
        # If result is not None, the table exists
        return result is not None
    
    def getTablename(self, pathname: str| os.PathLike | None = None) -> str | None:
        if hasattr(self, "__tablename") and self.__tablename is not None:
            return self.__tablename
        
        if pathname is None:
            return None

        sha1 = hashlib.sha1()
        sha1.update(str(pathname).encode())
        self.__tablename = f'{self.__user}_{sha1.hexdigest()}'
        return self.__tablename
    
    def load(self, pathname: str, dictionary: stardict.StarDict) -> bool:
        '''
        加载背过的单词书进行复习
        '''
        try:
            tablename = self.getTablename(pathname)
            if tablename is None:
                return False
            
            if not self.exists(tablename):
                self.__new(pathname, dictionary)
            
            yd = utils.youdao()
            
            cursor.execute(self.__book_load_query.format(tablename=self.__tablename))
            
            audios = {}
            for row in cursor.fetchall():
                w = Word(*row)
                w.bingo = 0
                w.delta = 50
                w.proficiency = 0 if w.totalCount == 0 else int(100 * (w.totalRight / w.totalCount))
                if w.proficiency > 95:
                    print(f"Skip word: {w.word}, Proficiency: {w.proficiency}")
                    continue
                info = dictionary.query(w.word)
                if info is not None:
                    if info["audio"] is None or info["audio"] == "":
                        # download the audio
                        path_rel = yd.path(w.word)
                        yd.down(w.word, os.path.join('phonetic', 'en', path_rel))
                        
                        # update the word info
                        if os.path.exists(os.path.join('phonetic', 'en', path_rel)):
                            info["audio"] = path_rel
                            
                            # update the word info
                            audios[w.word] = path_rel
                        
                    w.content = info
                    
                self.__words.append(w)
            # Update the audio to db if audio is not exists.
            if len(audios) > 0:
                self.updateAudio(audios)
        except Exception as e:
            logging.error(f"{type(e)} - {e}")
            return False
        
        return True
    
    def right(self, word: Word):
        word.totalCount += 1
        word.totalRight += 1
        word.right += 1
        word.bingo = max(0, word.bingo) + 1
        word.proficiency += max(5, int(word.delta * 1.00) + word.bingo * 5) # less than 5 point to inc
        word.delta += max(5, 5*word.bingo)
        cursor.execute(self.__book_update_right.format(tablename=self.__tablename), (word.proficiency, word.word))
        connection.commit()
        
    def wrong(self, word: Word):
        word.totalCount += 1
        word.totalWrong += 1
        word.wrong += 1
        word.bingo = min(0, word.bingo) - 1
        word.proficiency -= max(5, int(word.delta * 1.05) + word.bingo * 5) # more than 5 point to dec
        word.proficiency = max(0, word.proficiency) # 熟练度最小为0
        word.delta += max(-5, 5*word.bingo)
        cursor.execute(self.__book_update_wrong.format(tablename=self.__tablename), (word.proficiency, word.word))
        connection.commit()
        
    def __iter__(self):
        self.__iter = 0
        return self

    def __next__(self):
        '''
        单词迭代，背会的单词会被从列表中剔除。
        '''
        
        if len(self.__words) == 0:
            raise StopIteration

        if self.__iter % len(self.__words) == 0:
            self.__round += 1
            words : list[Word] = []
            for idx, word in enumerate(self.__words):
                if word.proficiency > 100:
                    continue
                
                words.append(word)
            
            self.__words = words
            if len(self.__words) == 0:
                raise StopIteration

        word = self.__words[self.__iter % len(self.__words)]
        self.__iter += 1
        return word
        
    def index(self):
        return self.__iter % len(self.__words)
    
    def length(self):
        return len(self.__words)
    
    def round(self):
        return self.__round
