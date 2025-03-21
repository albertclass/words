from __future__ import annotations
import os
import sys
from datetime import datetime
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pkg_resources import ResourceManager
import pygame
import utils

class BooksScene(utils.Scene):
    def __init__(self, size: tuple[int, int], bookPath: str, **kwargs):
        super().__init__("Books", size, 5, 1, **kwargs)

        self._book = None
        self._root = bookPath
        self.background_image = utils.ResourceManager.loadImage("images/background-6.png", "background.book")
        listStyle: utils.ListBoxStyle = utils.ListBoxStyle()
        itemStyle: utils.ListItemStyle = utils.ListItemStyle()

        listStyle.borderColor = (255, 255, 255)
        listStyle.borderSize = 1
        listStyle.borderRoundCorner = 5
        itemStyle.normalColor = pygame.Color(109, 232, 232, 127)
        itemStyle.normalTextColor = pygame.Color(0, 0, 0)
        itemStyle.borderColor = pygame.Color(255, 0, 120)
        itemStyle.borderSize = 0
        itemStyle.selectedTextColor = pygame.Color(255, 255, 255)
        itemStyle.hoverTextColor = pygame.Color(0, 167, 205)
        itemStyle.iconSize = (32, 32)
        itemStyle.iconPadding = 10
        itemStyle.align = "left"
        itemStyle.padding = (1, 4)

        self._listbox: utils.ListBox = utils.ListBox((0, 0, self.width // 2 - 2, self.height), 30, [], listStyle, itemStyle)
        self._rightArea: pygame.Rect = pygame.Rect(self.width // 2, 0, self.width, self.height)
        
        # 遍历目录，初始化子目录和文件
        for name in os.listdir(self._root):
            fullname = os.path.join(self._root, name)
            if os.path.isdir(fullname):
                self._listbox.append((name, utils.ResourceManager.loadImage("images/folder1.png", "folder"), fullname))
            
            if os.path.isfile(fullname) and name.endswith(".txt"):
                self._listbox.append((name, utils.ResourceManager.loadImage("images/file.png", "file"), fullname))

        self._listbox.connect(utils.ListBox.LISTBOX_LDBLCLICK, self._onListboxDbClick)

    def _onListboxDbClick(self, event: utils.Event):
        utils.SceneManager.Switch("Prepare")
        pass

    def _updateList(self, directory: str) -> None:
        self._listbox.clear()

        # 遍历目录，初始化子目录和文件
        for name in os.listdir(directory):
            fullname = os.path.join(directory, name)
            if os.path.isdir(fullname):
                self._listbox.append((name, utils.ResourceManager.loadImage("images/folder.png", "folder"), fullname))
            
            if os.path.isfile(fullname) and name.endswith(".txt"):
                self._listbox.append((name, utils.ResourceManager.loadImage("images/file.png", "file"), fullname))

    def _updateContent(self) -> None:
        pass
    
    def _onEnter(self, prevScene: utils.Scene | None, *params, **kwargs) -> None:
        self._updateList(self._root)
        self._updateContent()
    
    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        selected = self._listbox.selected
        if selected is None:
            return
        
        if type(selected) is not int:
            return
        
        item = self._listbox.item(selected)
        if item is None:
            return
        
        if type(item.data) is not str:
            return
        
        if nextScene is None or nextScene.title not in ["Prepare", "Remember"]:
            return
        
        user = utils.SceneManager.GetProperty("user")
        if user is None or user == "":
            return
        
        self.SetProperties({
            "round": 0,
            "loadargs": [
                [user, item.data, 5, 5, datetime.now()], # 50 new words
                [user, item.data, 5, 5, datetime.now()], # 50 new words
                [user, item.data, 5, 0, datetime.now()], # 50 review words
            ]
        })
        self._key_down_event = None

    def _onEvent(self, event: pygame.event.Event) -> bool:
        return self._listbox.process(event)
    
    def Update(self, *args, **kwargs) -> bool:
        self._listbox.update()
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        self._listbox.draw(surface)
        
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("兔哥背单词")
    scene = BooksScene((1280, 1024), "books", theme_path="themes.json")
    
    utils.SceneManager.AddScene("Books", scene, True)
        
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
    
