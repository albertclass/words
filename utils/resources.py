from __future__ import annotations
import os
import io
import sys
import zipfile
import logging
import threading
import queue

import pygame


class ResourceManager:
    _instance = None
    def __new__(cls) -> ResourceManager:    
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self.__class__._instance is not self:
            raise Exception("不能直接创建新的实例，请使用现有单例")
        if hasattr(self, "__initilized"):
            return
        
        self._loading: list[threading.Thread] = []
        self._search_paths: list[tuple[str, zipfile.ZipFile]] = []
        self._search_queue: queue.Queue = queue.Queue(64)
        self.__initlized = True
    
    def _async_init(self, path: str | os.PathLike) -> threading.Thread:
        def _loading():
            try:
                zfile = zipfile.ZipFile(path)
                
                self._search_queue.put((os.path.abspath(path)[:-4], zfile))
            except Exception as e:
                return f"Error: {type(e)} - {e}"

        return threading.Thread(target=_loading)
        
    def add(self, path: str | os.PathLike) -> str | None:
        basename = os.path.basename(path)
        if not basename.endswith(".zip"):
            return "Invalid zip file"
            
        if not os.path.exists(path):
            return "File not found"
        
        loading = self._async_init(path)
        loading.start()
        self._loading.append(loading)
    
    def _update(self):
        # get result from search queue
        while not self._search_queue.empty():
            root, zfile = self._search_queue.get()
            self._search_paths.append((root, zfile))
        
    def _get(self, path: str | os.PathLike[str]) -> tuple[zipfile.ZipFile | None, str | None]:
        path = os.path.abspath(path)
        
        # check if the search paths are updated
        self._update()
        # search in search paths
        for root, zfile in self._search_paths:
            if not path.startswith(root) or len(str(path)) <= len(root):
                continue

            subpath = path[len(root)+1:]
            if sys.platform == "win32":
                subpath = subpath.replace("\\", "/")

            return zfile, subpath
            
        return None, None
            
    def is_done(self) -> bool:
        self._update()
        
        for loading in self._loading:
            if loading.is_alive():
                return False
        return True

    def loadSound(self, path: str | os.PathLike[str]) -> pygame.mixer.Sound | None:
        try:
            if not pygame.mixer.get_init():
                return None
            
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
            
            zfile, subpath = self._get(path)
            if zfile is None or subpath is None:
                return None
            
            with zfile.open(subpath) as file:
                buffer = io.BytesIO(file.read())
                return pygame.mixer.Sound(buffer)
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None
        
    def loadImage(self, path: str | os.PathLike[str]) -> pygame.Surface | None:
        try:
            if os.path.exists(path):
                return pygame.image.load(path)
            
            zfile, subpath = self._get(path)
            if zfile is None:
                return None
            
            with zfile.open(str(subpath)) as file:
                buffer = io.BytesIO(file.read())
                return pygame.image.load(buffer, str(subpath))
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None

if __file__ == "__main__":
    resMgr = ResourceManager()
    resMgr.add("phonetic/en.zip")
    
    sound = resMgr.loadSound("phonetic/en/abandon.mp3")
    if sound is not None:
        sound.play(loops=0)
    else:
        print("Sound not found")
    
    image = resMgr.loadImage("images/startup.png")
    if image is not None:
        pygame.display.set_mode(image.get_size())
        pygame.display.get_surface().blit(image, (0, 0))
        pygame.display.flip()
    else:
        print("Image not found")