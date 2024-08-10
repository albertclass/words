from abc import abstractclassmethod, abstractmethod
import pygame

class Scene:
    def __init__(self, title: str):
        self.title = title
        
    @abstractmethod
    def __onEnter(self, sceneFrom: Scene):
        pass
    
    def __onLevel(self):
        pass