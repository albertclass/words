from __future__ import annotations
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils
from core import Book

class _Icons:
    def __init__(self, files: list[str] | None = None) -> None:
        if files is not None and len(files) > 0:
            images = [pygame.image.load(s) for s in files if os.path.isfile(s)]
            w = max([i.get_width() for i in images])
            h = max([i.get_height() for i in images])
            
            self.__icons = pygame.Surface((w, h * len(images)))
            for i in range(len(images)):
                rc = images[i].get_rect()
                self.__icons.blit(images[i], (w // 2 - rc.centerx, i * h + (h - rc.height) // 2))
                
            self._width = w
            self._height = h

    def GetIcon(self, index: int) -> pygame.Surface:
        rc = self.__icons.get_rect()
        return self.__icons.subsurface((0, index * self._height, rc.width, self._height))
    
    def height(self) -> int:
        return self._height
    
    def width(self) -> int:
        return self._width
    
class File(utils.Sprite):
    def __init__(self, filename: str, parent: Directory | None, *args):
        self.__name = filename
        self.__parent = parent
        
        if parent is not None:
            self.__icons: _Icons = parent.__icons
            self.__font: pygame.font.Font = parent.__font
            self.__width: int = parent.__width
        else:
            if len(args) > 0:
                self.__icons: _Icons = args[0]
            
            if len(args) > 1:
                self.__font: pygame.font.Font = args[1]
                
            if len(args) > 2:
                self.__width: int = args[2]
                    
        height = max(self.__font.get_height(), self.__icons.height())
        surface = pygame.Surface((self.__width, height))
        surface.set_colorkey((0, 0, 0))
        surface.fill((0,0,0))
        
        # 图标和文件名都居中显示
        icon = self.__icons.GetIcon(2) if os.path.isfile(filename) else self.__icons.GetIcon(0)
        surface.blit(icon, (0, height // 2 - self.__icons.height() // 2))
        text = self.__font.render(os.path.basename(filename), True, (255, 255, 255))
        surface.blit(text, (self.__icons.width(), height // 2 - text.get_height() // 2))
        
        # 调用父类构造函数
        super().__init__(surface, 0, 0)

    def __str__(self) -> str:
        return self.__name
    
    def GetName(self) -> str:
        return self.__name
    
    def GetParent(self) -> Directory | None:
        return self.__parent
    
class Directory(File):
    def __init__(self, pathname: str, parent: Directory | None, *args):
        super().__init__(pathname, parent, *args)
        if parent is not None:
            self.Files: list[File] = [ParentDirectory(parent, *args)]
        else:
            self.Files: list[File] = []
            
        
        # 遍历目录，初始化子目录和文件
        for name in os.listdir(pathname):
            fullname = os.path.join(pathname, name)
            if os.path.isdir(fullname):
                self.Files.append(Directory(fullname, self, *args))
            
            if os.path.isfile(fullname) and name.endswith(".txt"):
                self.Files.append(File(fullname, self))
    
class ParentDirectory(File):
    def __init__(self, ref: Directory, *args):
        super().__init__("..", ref.GetParent(), *args)
        self.__ref = ref
        
    def directory(self) -> Directory:
        return self.__ref
        
class BooksScene(utils.Scene):
    def __init__(self, size: tuple[int, int], bookPath: str):
        super().__init__("Books", size, 5, 1)

        self._book = None
        self._group: pygame.sprite.Group = pygame.sprite.Group()
        self._subgroup: pygame.sprite.Group = pygame.sprite.Group()
        self._icons = _Icons(["images/folder1.png", "images/folder2.png", "images/file.png"])
        self._area: pygame.Rect = pygame.Rect(
            self._span * 2 + self._border, 
            self._span * 2 + self._border, 
            (self.width - self._span * 4 - self._border) // 2, 
            (self.height - self._span * 4 - self._border),
        )
        
        self._rightArea: pygame.Rect = pygame.Rect(
            self._area.x + self._area.width + self._span * 2 + self._border, 
            self._area.y, 
            self._area.width, 
            self._area.height
        )
        
        self._root = Directory(bookPath, None, self._icons, utils.FontManager.GetFont("SimHei", 32), self._area.width)
        self._currentDirectory = self._root

        self._page = 0 # 当前目录下的文件页数
        self._index: int = 0 # 当前页中的索引
        self._offset: int = 0 # 当前页
        self._itemPrePage: int = self._area.height // self._root.Size()[1] # 每页显示的项目数
        
        self._key_down_time: int = 0
        self._key_dwon_interval: int = 100
        self._key_down_event: pygame.event.Event | None = None
    
    def __nextItem(self) -> None:
        self._index += 1

        try:
            # 如果当前页中的索引小于每页显示的项目数，或者当前页中的索引小于当前目录中的文件数减去偏移量
            if not self._index >= min(self._itemPrePage, len(self._currentDirectory.Files) - self._offset):
                return
            
            self._index = min(self._itemPrePage, len(self._currentDirectory.Files) - self._offset) - 1
            if not self._offset + self._itemPrePage < len(self._currentDirectory.Files):
                return
            
            self._offset += 1
            self.__updateDirectory(self._currentDirectory)
        finally:
            self.__updateSubDirectory()

    def __prevItem(self) -> None:
        self._index -= 1
        self.__updateSubDirectory()
        if not self._index < 0:
            return
        
        self._index = 0
        if not self._offset > 0:
            return
        
        self._offset -= 1
        self.__updateDirectory(self._currentDirectory)

    def __nextPage(self) -> None:
        pass
    
    def __prevPage(self) -> None:
        pass
    
    def __updateDirectory(self, directory: Directory) -> None:
        if directory is not self._currentDirectory:
            self._currentDirectory = directory
            self._index = 0
            self._offset = 0
        
        self._group.empty()
        for index, file in enumerate(self._currentDirectory.Files[self._offset : self._offset + self._itemPrePage]):
            file.MoveTo(self._area.x, self._area.y + index * file.Size()[1])
            self._group.add(file)

    def __updateSubDirectory(self) -> None:
        self._page = 0
        self._subgroup.empty()
        
        selected = self._currentDirectory.Files[self._index]
        if isinstance(selected, Directory):
            for index, file in enumerate(selected.Files[self._page * self._itemPrePage : (self._page + 1) * self._itemPrePage]):
                file.MoveTo(self._rightArea.x, self._rightArea.y + index * file.Size()[1])
                self._subgroup.add(file)
        elif isinstance(selected, ParentDirectory):
            pass
        elif isinstance(selected, File):
            with open(selected.GetName(), "r", encoding="utf-8") as f:
                lines = f.readlines()
                for index, line in enumerate(lines[self._page * self._itemPrePage : (self._page + 1) * self._itemPrePage]):
                    text = utils.FontManager.GetFont("SimHei", 32).render(line, True, (255, 255, 255))
                    self._subgroup.add(utils.Sprite(text, self._rightArea.x, self._rightArea.y + index * selected.Size()[1]))
    
    def __leaveDirectory(self) -> None:
        self._group.empty()
    
    def _onEnter(self, prevScene: utils.Scene | None, *params, **kwargs) -> None:
        self.__updateDirectory(self._root)
        self.__updateSubDirectory()
    
    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        selectedFile = self._currentDirectory.Files[self._index + self._offset]

        if type(selectedFile) is not File:
            return
        
        if nextScene is None or nextScene.title not in ["Prepare", "Remember"]:
            return
        
        user = utils.SceneManager.GetProperty("user")
        if user is None or user == "":
            return
        
        self._book = Book()
        self._book.load(user, selectedFile.GetName())
        self.SetProperty("book", self._book)
        self._key_down_event = None
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        self._key_down_time = pygame.time.get_ticks()
        self._key_down_event = event

        if event.key == pygame.K_UP:
            self.__prevItem()
        elif event.key == pygame.K_DOWN:
            self.__nextItem()
        elif event.key == pygame.K_PAGEUP:
            self.__prevPage()
        elif event.key == pygame.K_PAGEDOWN:
            self.__nextPage()
        elif event.key == pygame.K_RETURN:
            file = self._currentDirectory.Files[self._index + self._offset]
            if isinstance(file, Directory):
                self.__updateDirectory(file)
                self.__updateSubDirectory()
            elif isinstance(file, ParentDirectory):
                self.__updateDirectory(file.directory())
                self.__updateSubDirectory()
            else:
                # select file
                utils.SceneManager.Switch("Prepare")
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        self._key_down_event = None
        self._key_down_time = 0
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.Event) -> None:
        pass
    
    def Update(self, *args, **kwargs) -> bool:
        if self._key_down_event is not None and pygame.time.get_ticks() - self._key_down_time > self._key_dwon_interval:
            self._onKeyDown(self._key_down_event)
        
        self._group.update(*args, **kwargs)
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        surface.fill((0,0,0))
        pygame.draw.rect(surface, (255, 255, 255), (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        pygame.draw.line(surface, (255, 255, 255), (self.width // 2, self._span * 2 + 2), (self.width // 2, self.height - self._span * 2 - 2), 1)
        
        # draw current selected item
        pygame.draw.rect(surface, (255, 255, 0), (
                self._area.x - 2, 
                self._area.y + self._index * self._currentDirectory.Files[0].Size()[1] - 2, 
                self._area.width - 4, 
                self._currentDirectory.Files[0].Size()[1] + 4
            ), 1, 5
        )
        self._group.draw(surface)
        self._subgroup.draw(surface)
        
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("兔哥背单词")
    scene = BooksScene((800, 600), "books")
    
    utils.SceneManager.AddScene("Books", scene, True)
        
    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        pygame.time.delay(1000 // 60)
        
    pygame.quit()
    
