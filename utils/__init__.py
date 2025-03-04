from re import S
import pygame
from .tts import SimpleTTS
from .scene import Scene, SceneManager
from .fonts import FontManager
from .sprite import Sprite, SpriteFrameAnim
from .spider import youdao
from .resources import ResourceManager
from .fireworks import Fireworks
from .charactor import Charactor

def CenterPos(image: pygame.Surface, targetSize: tuple[int,int]) -> tuple[int,int]:
    image_rc = image.get_rect()
    return (targetSize[0] // 2 - image_rc.width // 2, targetSize[1] // 2 - image_rc.height // 2)

FontManager = FontManager()
SceneManager = SceneManager()
ResourceManager = ResourceManager()

SpriteFrameAnimMode = SpriteFrameAnim.Mode
SpriteFrameAnimPlayMode = SpriteFrameAnim.PlayMode
__all__ = [
    "Scene",
    "SceneManager",
    "FontManager",
    "ResourceManager",
    "Sprite",
    "SpriteFrameAnim",
    "Charactor",
    "CenterPos",
    "youdao",
    "Fireworks",
    "SimpleTTS",
]