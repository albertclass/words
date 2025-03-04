import sqlite3
from typing import Any, Tuple

_is_table_exists_query = """
    SELECT name FROM sqlite_master WHERE type='table' AND name=?;
"""

_user_create_table = """
CREATE TABLE IF NOT EXISTS users (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL
);
"""

_user_insert = """
    INSERT OR REPLACE INTO users (name, password)
    VALUES (?, ?)
"""

_user_query = """
    SELECT name, password FROM users
"""

_book_create_table = """
CREATE TABLE IF NOT EXISTS {tablename} (
    word TEXT PRIMARY KEY,
    wrong INTEGER NOT NULL DEFAULT 0,
    right INTEGER NOT NULL DEFAULT 0,
    bingo INTEGER NOT NULL DEFAULT 0,    
    content TEXT DEFAULT NULL,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

_book_insert_word = """
    INSERT OR REPLACE INTO {tablename} (word)
    VALUES (?)
"""

# 选择?个新单词
_book_load_query = """
    SELECT word, wrong, right, bingo
    FROM {tablename}
    WHERE wrong = 0 AND right = 0
    LIMIT ?
"""

# 选择?个需要复习的单词
_book_review_query = """
    SELECT word, wrong, right, bingo
    FROM {tablename}
    WHERE wrong > right OR bingo < 3  -- 假设bingo小于3的单词需要复习
    ORDER BY wrong DESC, bingo ASC
    LIMIT ?;
"""

_book_update_wrong = """
    UPDATE {tablename} SET wrong = wrong + ? where word = ?
"""

_book_update_right = """
    UPDATE {tablename} SET right = right + ? where word = ?
"""

_book_update_bingo = """
    UPDATE {tablename} SET bingo = bingo + ? where word = ?
"""

class Database:
    def __init__(self, dbname: str):
        self._connection = sqlite3.connect(dbname)
        self._cursor = self._connection.cursor()

    def execute(self, query: str, params: Tuple[Any, ...] | list[Any] | dict[str, Any] = (), /):
        self._cursor.execute(query, params)
    
    def query(self, query: str, params: Tuple[Any, ...] | list[Any] | dict[str, Any] = (), /) -> list[Any]:
        self._cursor.execute(query, params)
        return self._cursor.fetchall()
    
    def commit(self):
        self._connection.commit()

class Table:
    def __init__(self, database: Database, tablename: str):
        self._database = database
        self._tablename = tablename

    def IsExists(self) -> bool:
        # Query to check if table exists
        return len(self._database.query(_is_table_exists_query, (self._tablename,)) or []) > 0
    
    @property
    def tablename(self):
        return self._tablename

class UserTable(Table):
    def __init__(self, database: Database):
        super().__init__(database, "users")

    def Create(self):
        self._database.execute(_user_create_table)
        self._database.commit()

    def Insert(self, name: str, password: str):
        self._database.execute(_user_insert, (name, password))
        self._database.commit()

    def QueryAll(self)->list[str]:
        return self._database.query(_user_query)

class BookTable(Table):
    def __init__(self, database: Database, tablename: str):
        super().__init__(database, tablename)

    def Create(self):
        self._database.execute(_book_create_table.format(tablename=self.tablename))
        self._database.commit()

    def Insert(self, words: list[str]):
        for word in words:
            try:
                self._database.execute(_book_insert_word.format(tablename=self.tablename), (word,))
            except Exception as e:
                print(e)

        self._database.commit()

    def IncWrong(self, word: str, count: int = 1):
        self._database.execute(_book_update_wrong.format(tablename=self.tablename), (count, word))
        self._database.commit()

    def IncRight(self, word: str, count: int = 1):
        self._database.execute(_book_update_right.format(tablename=self.tablename), (count, word))
        self._database.commit()

    def IncBingo(self, word: str, count: int = 1):
        self._database.execute(_book_update_bingo.format(tablename=self.tablename), (count, word))
        self._database.commit()

    def QueryNewWords(self, count: int) -> list[Any]:
        return self._database.query(_book_load_query.format(tablename=self.tablename), (count,))

    def QueryReviewWords(self, count: int) -> list[Any]:
        return self._database.query(_book_load_query.format(tablename=self.tablename), (count,))
