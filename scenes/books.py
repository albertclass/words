from __future__ import annotations
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import utils

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

        self.__group: pygame.sprite.Group = pygame.sprite.Group()
        self.__subgroup: pygame.sprite.Group = pygame.sprite.Group()
        self.__icons = _Icons(["images/folder1.png", "images/folder2.png", "images/file.png"])
        self.__area: pygame.Rect = pygame.Rect(
            self._span * 2 + self._border, 
            self._span * 2 + self._border, 
            (self.width - self._span * 4 - self._border) // 2, 
            (self.height - self._span * 4 - self._border),
        )
        
        self.__rightArea: pygame.Rect = pygame.Rect(
            self.__area.x + self.__area.width + self._span * 2 + self._border, 
            self.__area.y, 
            self.__area.width, 
            self.__area.height
        )
        
        self.__root = Directory(bookPath, None, self.__icons, utils.FontManager.GetFont("SimHei", 32), self.__area.width)
        self.__currentDirectory = self.__root

        self.__page = 0 # 当前目录下的文件页数
        self.__index: int = 0 # 当前页中的索引
        self.__offset: int = 0 # 当前页
        self.__itemPrePage: int = self.__area.height // self.__root.Size()[1] # 每页显示的项目数
        
        self.__key_down_time: int = 0
        self.__key_dwon_interval: int = 100
        self.__key_down_event: pygame.event.Event | None = None
    
    def __nextItem(self) -> None:
        self.__index += 1

        try:
            # 如果当前页中的索引小于每页显示的项目数，或者当前页中的索引小于当前目录中的文件数减去偏移量
            if not self.__index >= min(self.__itemPrePage, len(self.__currentDirectory.Files) - self.__offset):
                return
            
            self.__index = min(self.__itemPrePage, len(self.__currentDirectory.Files) - self.__offset) - 1
            if not self.__offset + self.__itemPrePage < len(self.__currentDirectory.Files):
                return
            
            self.__offset += 1
            self.__updateDirectory(self.__currentDirectory)
        finally:
            self.__updateSubDirectory()

    def __prevItem(self) -> None:
        self.__index -= 1
        self.__updateSubDirectory()
        if not self.__index < 0:
            return
        
        self.__index = 0
        if not self.__offset > 0:
            return
        
        self.__offset -= 1
        self.__updateDirectory(self.__currentDirectory)

    def __nextPage(self) -> None:
        pass
    
    def __prevPage(self) -> None:
        pass
    
    def __updateDirectory(self, directory: Directory) -> None:
        if directory is not self.__currentDirectory:
            self.__currentDirectory = directory
            self.__index = 0
            self.__offset = 0
        
        self.__group.empty()
        for index, file in enumerate(self.__currentDirectory.Files[self.__offset : self.__offset + self.__itemPrePage]):
            file.MoveTo(self.__area.x, self.__area.y + index * file.Size()[1])
            self.__group.add(file)

    def __updateSubDirectory(self) -> None:
        self.__page = 0
        self.__subgroup.empty()
        
        selected = self.__currentDirectory.Files[self.__index]
        if isinstance(selected, Directory):
            for index, file in enumerate(selected.Files[self.__page * self.__itemPrePage : (self.__page + 1) * self.__itemPrePage]):
                file.MoveTo(self.__rightArea.x, self.__rightArea.y + index * file.Size()[1])
                self.__subgroup.add(file)
    
    def __leaveDirectory(self) -> None:
        self.__group.empty()
    
    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        self.__updateDirectory(self.__root)
    
    def _onLeave(self) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP:
            self.__prevItem()
        elif event.key == pygame.K_DOWN:
            self.__nextItem()
        elif event.key == pygame.K_PAGEUP:
            self.__prevPage()
        elif event.key == pygame.K_PAGEDOWN:
            self.__nextPage()
        elif event.key == pygame.K_RETURN:
            file = self.__currentDirectory.Files[self.__index + self.__offset]
            if isinstance(file, Directory):
                self.__updateDirectory(file)
            elif isinstance(file, ParentDirectory):
                self.__updateDirectory(file.directory())
            else:
                # select file
                self.__selectFile = file
                utils.SceneManager.Switch("Prepare")
        self.__key_down_time = pygame.time.get_ticks()
        self.__key_down_event = event
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        self.__key_down_event = None
        self.__key_down_time = 0
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.Event) -> None:
        pass
    
    def GetSelectedFile(self) -> str:
        return self.__selectFile.GetName()
    
    def Update(self, *args, **kwargs) -> bool:
        if self.__key_down_event is not None and pygame.time.get_ticks() - self.__key_down_time > self.__key_dwon_interval:
            self._onKeyDown(self.__key_down_event)
        
        self.__group.update(*args, **kwargs)
        return True
    
    def Draw(self, surface: pygame.Surface) -> None:
        surface.fill((0,0,0))
        pygame.draw.rect(surface, (255, 255, 255), (self._span, self._span, self.width - self._span * 2, self.height - self._span * 2), 1, 5)
        pygame.draw.line(surface, (255, 255, 255), (self.width // 2, self._span * 2 + 2), (self.width // 2, self.height - self._span * 2 - 2), 1)
        
        # draw current selected item
        pygame.draw.rect(surface, (255, 255, 0), (
                self.__area.x - 2, 
                self.__area.y + self.__index * self.__currentDirectory.Files[0].Size()[1] - 2, 
                self.__area.width - 4, 
                self.__currentDirectory.Files[0].Size()[1] + 4
            ), 1, 5
        )
        self.__group.draw(surface)
        self.__subgroup.draw(surface)
        
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
    
