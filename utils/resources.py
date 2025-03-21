from __future__ import annotations
from hashlib import sha1
import os
import io
import sys
import zipfile
import logging
import threading
import queue
import pygame
from .tts import SimpleTTS
from typing import Optional

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
        
        self._tts: SimpleTTS = SimpleTTS()
        self._loading: list[threading.Thread] = []
        self._search_paths: list[tuple[str, zipfile.ZipFile]] = []
        self._search_queue: queue.Queue = queue.Queue(64)
        self._fonts: dict[str, pygame.font.Font] = {}
        self._textures: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._files: dict[str, io.BytesIO] = {}

        self.__initlized = True
    
    def _async_init(self, path: str | os.PathLike) -> threading.Thread:
        def _loading():
            try:
                zfile = zipfile.ZipFile(path)
                
                # put absolute path and zip file object into search queue. 
                # when call _get method, it will visit the search queue to find the zip file object.
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
        # after the loading thread is done, it will put the zip file object into search queue
        # so we can get the zip file object from search queue
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

    def loadSound(self, path: str | os.PathLike[str], name: Optional[str] = None) -> pygame.mixer.Sound | None:
        try:
            if name is not None and name in self._sounds:
                return self._sounds[name]
            
            if not pygame.mixer.get_init():
                return None
            
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                if name is not None:
                    self._sounds[name] = sound
                return sound
            
            zfile, subpath = self._get(path)
            if zfile is None or subpath is None:
                return None
            
            with zfile.open(subpath) as file:
                buffer = io.BytesIO(file.read())
                sound = pygame.mixer.Sound(buffer)
                if name is not None:
                    self._sounds[name] = sound
                return sound
            
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None
    
    def getSound(self, name: str) -> pygame.mixer.Sound | None:
        return self._sounds.get(name, None)
    
    def loadImage(self, path: str | os.PathLike[str], name: Optional[str] = None) -> pygame.Surface | None:
        try:
            if name is not None and name in self._textures:
                return self._textures[name]
            
            if os.path.exists(path):
                tex = pygame.image.load(path)
                if name is not None:
                    self._textures[name] = tex
                return tex
            
            zfile, subpath = self._get(path)
            if zfile is None:
                return None
            
            with zfile.open(str(subpath)) as file:
                buffer = io.BytesIO(file.read())
                tex = pygame.image.load(buffer, str(subpath))
                if name is not None:
                    self._textures[name] = tex
                return tex
            
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None

    def getImage(self, name: str) -> pygame.Surface | None:
        return self._textures.get(name, None)
    
    def loadFile(self, path: str | os.PathLike[str], name: Optional[str] = None) -> io.BytesIO | None:
        try:
            if name is not None and name in self._files:
                return self._files[name]
            
            if os.path.exists(path):
                with open(path, "rb") as file:
                    file = io.BytesIO(file.read())
                    if name is not None:
                        self._files[name] = file
                    return file
            
            zfile, subpath = self._get(path)
            if zfile is None:
                return None
            
            with zfile.open(str(subpath)) as file:
                file = io.BytesIO(file.read())
                if name is not None:
                    self._files[name] = file
                return file
            
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None
    
    def getFile(self, name: str) -> io.BytesIO | None:
        return self._files.get(name, None)
    
    def loadFont(self, path: str | os.PathLike[str], size: int, name: Optional[str] = None) -> pygame.font.Font | None:
        try:
            if name is None:
                name = os.path.basename(path) + "-" + str(size)

            if name in self._fonts:
                return self._fonts[name]
            
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
                self._fonts[name] = font
                return font
            
            zfile, subpath = self._get(path)
            if zfile is None:
                return None
            
            with zfile.open(str(subpath)) as file:
                buffer = io.BytesIO(file.read())
                font = pygame.font.Font(buffer, size)
                self._fonts[name] = font
                return font
            
        except Exception as e:
            logging.error(f"Error: {type(e)} - {e}")
            return None
    
    def getFont(self, name: str) -> pygame.font.Font | None:
        return self._fonts.get(name, None)
    
    def defaultFont(self) -> pygame.font.Font | None:
        return self.loadFont("font/msyh.ttc", 16, "default")
    
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