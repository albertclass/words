import os
import random
import stardict
import logging
import hashlib
from . import database
from .word import Word

dictionary = stardict.StarDict("dict.db")

class Book:
    '''
    单词书，要背的单词都在单词书里面。会定期进行复习。
    '''
    
    def __init__(self):
        self.dirty = False
        self._words: list[Word] = []
        self._iter = 0
        self._round = 0
        self._db = database.Database("users.db")        
        self._table: database.BookTable | None = None

    def __tablename(self, user: str, pathname: str | os.PathLike) -> str:
        sha1 = hashlib.sha1()
        sha1.update(str(pathname).encode())
        return f'{user}_{sha1.hexdigest()}'

    def __new(self, user: str, pathname: str | os.PathLike, dictionary: stardict.StarDict)-> bool:
        '''
        从文件中新建单词书，单词每行一个，也可以是词组或固定搭配。
        '''
        if not os.path.exists(pathname):
            return False
        
        # transform the pathname to absolute path
        pathname = os.path.abspath(pathname)

        self._table = database.BookTable(self._db, self.__tablename(user, pathname))

        if self._table.IsExists():
            return True

        # create the database table
        self._table.Create()
        
        # initialize the book table
        with open(pathname, "r", encoding="utf-8") as f:
            try:
                lines = f.readlines()
                words = [ln[:-1] for ln in lines]
                self._table.Insert(words)
                
            except Exception as e:
                print(e)

        return True
    
    def isEmpty(self):
        return len(self._words) == 0
    
    def load(self, user: str, pathname: str, totalWordCount = 200, newWordCount: int = 50) -> bool:
        '''
        加载背过的单词书进行复习
        '''
        try:
            self.__new(user, pathname, dictionary)
            if self._table is None:
                return False
            
            newWords = self._table.QueryNewWords(newWordCount)
            reviewWords = self._table.QueryReviewWords(totalWordCount - len(newWords))
            # audios = {}
            for word in set([row[0] for row in newWords + reviewWords]):
                w = Word(word, dictionary.query(word))
                # info = 
                # if info is not None:
                #     if info["audio"] is None or info["audio"] == "":
                #         # download the audio
                #         path_rel = yd.path(w.word)
                #         yd.down(w.word, os.path.join('phonetic', 'en', path_rel))
                        
                #         # update the word info
                #         if os.path.exists(os.path.join('phonetic', 'en', path_rel)):
                #             info["audio"] = path_rel
                            
                #             # update the word info
                #             audios[w.word] = path_rel
                        
                #     w.content = info
                    
                self._words.append(w)
            # Update the audio to db if audio is not exists.
            # if len(audios) > 0:
            #     self.updateAudio(audios)
        except Exception as e:
            logging.error(f"{type(e)} - {e}")
            return False
        
        return True
    
    def right(self, word: Word):
        word.right += 1
        word.bingo += 1
        
    def wrong(self, word: Word):
        word.wrong += 1
        word.bingo = 0
        
    def __iter__(self):
        self._iter = 0
        return self

    def __next__(self):
        '''
        单词迭代，背会的单词会被从列表中剔除。
        '''
        
        if len(self._words) == 0:
            raise StopIteration

        if self._iter % len(self._words) == 0:
            self._round += 1
            words : list[Word] = []
            for idx, word in enumerate(self._words):
                if word.wrong < word.right:
                    if self._table is not None:
                        self._table.IncRight(word.word, word.right)
                        self._table.IncWrong(word.word, word.wrong)
                        self._table.IncBingo(word.word, 1)
                    continue
                
                words.append(word)
            
            self._words = words
            if len(self._words) == 0:
                raise StopIteration

        word = self._words[self._iter % len(self._words)]
        self._iter += 1
        return word
    
    def reset(self):
        self._iter = 0
        self._round = 0
        for word in self._words:
            word.right = 0
            word.wrong = 0
            word.bingo = 0
        # 重排顺序
        random.shuffle(self._words)
    
    def index(self):
        return self._iter % len(self._words)
    
    def length(self):
        return len(self._words)
    
    def round(self):
        return self._round
