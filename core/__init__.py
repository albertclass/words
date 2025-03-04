import os
import sys

appendPaths = [
    "../ECDICT",
]
extendPaths = [os.path.abspath(os.path.join(os.path.dirname(__file__), path)) for path in appendPaths]
sys.path.extend(extendPaths)

from .database import Database, UserTable, BookTable
from .book import Book
from .word import Word, CharSequence

def LoadConfig(file: str | os.PathLike) -> None:
    pass

__all__ = ["Book", "Word", "CharSequence", "LoadConfig", "Database", "UserTable", "BookTable"]