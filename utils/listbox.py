if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from typing import Any, Optional, Callable
from enum import Enum
import pygame
import utils

class Padding(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

class ListItemStyle:
    def __init__(self) -> None:
        self._borderSize: int = 1
        self._borderRoundCorner: int = 0
        self._borderColor: Optional[pygame.Color] = None
        self._focusColor: Optional[pygame.Color] = pygame.Color(255,255,255)
        self._hoverColor: Optional[pygame.Color] = None
        self._hoverTextColor: Optional[pygame.Color] = pygame.Color(0,0,0)
        self._normalColor: Optional[pygame.Color] = None
        self._normalTextColor: Optional[pygame.Color] = pygame.Color(0,0,0)
        self._selectedColor: Optional[pygame.Color] = None
        self._selectedTextColor: Optional[pygame.Color] = pygame.Color(255,255,255)
        self._iconSize = (16,16)
        self._iconPadding = 4
        self._padding: tuple[int,int,int,int] = (0,0,0,0) # top, right, bottom, left
        self._align = "left"

        self.updateStyle()
    @property
    def borderColor(self) -> Optional[pygame.Color]:
        return self._borderColor
    
    @borderColor.setter
    def borderColor(self, value: pygame.Color) -> None:
        self._borderColor = value

    @property
    def borderSize(self) -> int:
        return self._borderSize
    
    @borderSize.setter
    def borderSize(self, value: int) -> None:
        self._borderSize = value

    @property
    def borderRoundCorner(self) -> int:
        return self._borderRoundCorner
    
    @borderRoundCorner.setter
    def borderRoundCorner(self, value: int) -> None:
        self._borderRoundCorner = value

    @property
    def normalTextColor(self) -> Optional[pygame.Color]:
        return self._normalTextColor
    
    @normalTextColor.setter
    def normalTextColor(self, value: Optional[pygame.Color]) -> None:
        self._normalTextColor = value

    @property
    def selectedColor(self) -> Optional[pygame.Color]:
        return self._selectedColor
    
    @selectedColor.setter
    def selectedColor(self, value: Optional[pygame.Color]) -> None:
        self._selectedColor = value

    @property
    def focusColor(self) -> Optional[pygame.Color]:
        return self._focusColor
    
    @focusColor.setter
    def focusColor(self, value: Optional[pygame.Color]) -> None:
        self._focusColor = value

    @property
    def hoverColor(self) -> Optional[pygame.Color]:
        return self._hoverColor
    
    @hoverColor.setter
    def hoverColor(self, value: Optional[pygame.Color]) -> None:
        self._hoverColor = value

    @property
    def normalColor(self) -> Optional[pygame.Color]:
        return self._normalColor
    
    @normalColor.setter
    def normalColor(self, value: Optional[pygame.Color]) -> None:
        self._normalColor = value

    @property
    def hoverTextColor(self) -> Optional[pygame.Color]:
        return self._hoverTextColor
    
    @hoverTextColor.setter
    def hoverTextColor(self, value: Optional[pygame.Color]) -> None:
        self._hoverTextColor = value

    @property
    def selectedTextColor(self) -> Optional[pygame.Color]:
        return self._selectedTextColor
    
    @selectedTextColor.setter
    def selectedTextColor(self, value: Optional[pygame.Color]) -> None:
        self._selectedTextColor = value

    @property
    def iconSize(self) -> tuple[int,int]:
        return self._iconSize
    
    @iconSize.setter
    def iconSize(self, value: tuple[int,int]) -> None:
        self._iconSize = value

    @property
    def iconPadding(self) -> int:
        return self._iconPadding
    
    @iconPadding.setter
    def iconPadding(self, value: int) -> None:
        self._iconPadding = value

    @property
    def align(self) -> str:
        return self._align
    
    @align.setter
    def align(self, value: str) -> None:
        self._align = value

    @property
    def padding(self) -> tuple[int,int,int,int]:
        return self._padding
    
    @padding.setter
    def padding(self, value: int | tuple[int,int] | tuple[int,int,int,int]) -> None:
        if type(value) is int:
            self._padding = (value, value, value, value)
        elif type(value) is tuple and len(value) == 2:
            self._padding = (value[0], value[1], value[0], value[1])
        elif type(value) is tuple and len(value) == 4:
            self._padding = (value[0], value[1], value[2], value[3])
        else:
            raise TypeError("padding must be int or tuple of 2 or 4 integers")

    def updateStyle(self) -> None:
        pass

class ListBoxStyle:
    def __init__(self):
        self._backgroundImage: pygame.Surface | None = None
        self._backgroundColor: tuple[int,int,int] = (0,0,0)
        self._borderRoundCorner: int = 0
        self._borderColor: tuple[int,int,int] = (255,255,255)
        self._borderSize: int = 1
        self._multiSelect: bool = False

    @property
    def backgroundImage(self) -> pygame.Surface | None:
        return self._backgroundImage
    
    @backgroundImage.setter
    def backgroundImage(self, value: pygame.Surface | None) -> None:
        self._backgroundImage = value

    @property
    def backgroundColor(self) -> tuple[int,int,int]:
        return self._backgroundColor
    
    @backgroundColor.setter
    def backgroundColor(self, value: tuple[int,int,int]) -> None:
        self._backgroundColor = value

    @property
    def borderColor(self) -> tuple[int,int,int]:
        return self._borderColor
    
    @borderColor.setter
    def borderColor(self, value: tuple[int,int,int]) -> None:
        self._borderColor = value

    @property
    def borderRoundCorner(self) -> int:
        return self._borderRoundCorner
    
    @borderRoundCorner.setter
    def borderRoundCorner(self, value: int) -> None:
        self._borderRoundCorner = value

    @property
    def borderSize(self) -> int:
        return self._borderSize
    
    @borderSize.setter
    def borderSize(self, value: int) -> None:
        self._borderSize = value

    @property
    def multiSelect(self) -> bool:
        return self._multiSelect
    
    @multiSelect.setter
    def multiSelect(self, value: bool) -> None:
        self._multiSelect = value

class ListItem(pygame.sprite.Group):
    def __init__(self, parent: 'ListBox', width: int, height: int, text: str, icon: pygame.Surface | None = None, data: Any = None) -> None:
        super().__init__()
        self._parent = parent
        self._width = width
        self._height = height
        self._text: str = text
        self._icon: pygame.Surface | None = icon
        self._data: Any = data
        self._focus: bool = False

        self.text = text

    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def icon(self) -> pygame.Surface | None:
        return self._icon
    
    @icon.setter
    def icon(self, value: pygame.Surface | None) -> None:
        self._icon = value
    
    @property
    def data(self) -> Any:
        return self._data
    
    @data.setter
    def data(self, value: Any) -> None:
        self._data = value

    @property
    def selected(self) -> bool:
        return self._focus
    
    @selected.setter
    def selected(self, value: bool) -> None:
        self._focus = value

class Event:
    def __init__(self, type: int, data: Any = None, **kwArgs):
        self._type = type
        self._data = data
        
        for key, value in kwArgs.items():
            setattr(self, key, value)
    
    @property
    def type(self) -> int:
        return self._type
    
    @property
    def data(self) -> Any:
        return self._data

class ListBox(pygame.sprite.Group):
    LISTBOX_LCLICK = 0
    LISTBOX_LDBLCLICK = 1
    LISTBOX_SCORLL_CHANGED = 2
    LISTBOX_SELECT_CHANGED = 3
    LISTBOX_FOCUS_CHANGED = 4

    def __init__(self
            , rect: pygame.Rect | tuple[int,int,int,int]
            , itemHeight: int
            , items: list[str | tuple[str, pygame.Surface | None] | tuple[str, pygame.Surface | None, Any]] | None
            , style: ListBoxStyle | None = None
            , itemStyle: ListItemStyle | None = None
            , **kwargs):
        '''
        width: ListBox width
        height: ListBox height
        itemHeight: ListBox item height
        items: ListBox items
        font: font or font name
        fontsize: font size
        '''

        super().__init__()
        self._rect: pygame.Rect = pygame.Rect(rect)
        self._itemHeight = itemHeight
        self._items = []
        self._iconset: dict[pygame.Surface, pygame.Surface] = {}
        self._focus = -1
        self._selected = -1
        self._scroll = 0
        self._background: pygame.Surface | None = None
        self._font = utils.ResourceManager.defaultFont() or pygame.font.Font(None, 16)
        self._style: ListBoxStyle
        self._itemStyle: ListItemStyle
        self._click_tick = 0
        self._click_nums = 0

        from typing import Callable
        self._eventHandlers: dict[int, list[Callable]] = {}
        if kwargs.get("font") is not None:
            self._font = kwargs["font"]
        
        # set listbox style
        self.style = style or ListBoxStyle()
        self.itemStyle = itemStyle or ListItemStyle()

        if items is not None:
            self.append(*items)

    @property
    def width(self) -> int:
        return self._rect.width
    
    @property
    def height(self) -> int:
        return self._rect.height
    
    @property
    def style(self) -> ListBoxStyle:
        return self._style
    
    @style.setter
    def style(self, value: ListBoxStyle) -> None:
        if value.backgroundImage is not None:
            backgroundImageSize = value.backgroundImage.get_size()
            if backgroundImageSize != self._rect.size:
                value._backgroundImage = pygame.transform.scale(value.backgroundImage, self._rect.size)

        self._style = value
        
    @property
    def itemStyle(self) -> ListItemStyle:
        return self._itemStyle
    
    @itemStyle.setter
    def itemStyle(self, value: ListItemStyle) -> None:
        self._itemStyle = value

    def _shared_icon(self, icon: pygame.Surface) -> pygame.Surface:
        if icon not in self._iconset:
            self._iconset[icon] = pygame.transform.scale(icon, self._itemStyle.iconSize)

        if self._iconset[icon].get_size() != self._itemStyle.iconSize:
            self._iconset[icon] = pygame.transform.scale(icon, self._itemStyle.iconSize)

        return self._iconset[icon]

    def connect(self, event: int, callback: Callable) -> None:
        if event not in self._eventHandlers:
            self._eventHandlers[event] = []
        
        self._eventHandlers[event].append(callback)

    def post(self, event: Event) -> None:
        if event.type not in self._eventHandlers:
            return
        
        for handler in self._eventHandlers[event.type]:
            handler(event)

    def append(self, *items: str | tuple[str, pygame.Surface | None] | tuple[str, pygame.Surface | None, Any] | None) -> None:
        if items is None:
            return
        
        for item in items:
            if type(item) is str:
                self._items.append(ListItem(self, self._rect.width, self._itemHeight, item))
            elif type(item) is tuple and len(item) == 2 and type(item[0]) is str and isinstance(item[1], pygame.Surface):
                text, icon = item
                self._items.append(ListItem(self, self._rect.width, self._itemHeight, text, icon))
            elif type(item) is tuple and len(item) == 3 and type(item[0]) is str and isinstance(item[1], pygame.Surface):
                text, icon, data = item
                self._items.append(ListItem(self, self._rect.width, self._itemHeight, text, icon, data))
            else:
                raise TypeError("item must be str or tuple of str or (str, pygame.Surface) or (str, pygame.Surface, Any)")


    def insert(self, index: int, *items: str | tuple[str, pygame.Surface | None] | tuple[str, pygame.Surface | None, Any] | None) -> None:
        if items is None:
            return
        
        for item in items:
            if type(item) is str:
                self._items.insert(index, ListItem(self, self._rect.width, self._itemHeight, item))
            elif type(item) is tuple and len(item) == 2 and type(item[0]) is str and isinstance(item[1], pygame.Surface):
                text, icon = item
                self._items.insert(index, ListItem(self, self._rect.width, self._itemHeight, text, icon))
            elif type(item) is tuple and len(item) == 3 and type(item[0]) is str and isinstance(item[1], pygame.Surface):
                text, icon, data = item
                self._items.insert(index, ListItem(self, self._rect.width, self._itemHeight, text, icon, data))
            else:
                raise TypeError("item must be str or tuple of str or (str, pygame.Surface) or (str, pygame.Surface, Any)")
    
    def remove(self, index: int) -> None:
        self._items.pop(index)

    def clear(self) -> None:
        self._items.clear()

    @property
    def selected(self) -> int | list[int] | None:
        if self._style.multiSelect:
            return [i for i, item in enumerate(self._items) if item.selected]
        else:
            return self._selected if self._selected >= 0 else None
            
    @selected.setter
    def selected(self, value: int | list[int]) -> None:
        if self._style.multiSelect:
            if type(value) is int:
                if value < 0 or value >= len(self._items):
                    return
                
                self._items[value].selected = True
            elif type(value) is list:
                for i in value:
                    if i < 0 or i >= len(self._items):
                        continue
                    
                    self._items[i].selected = True
        else:
            if type(value) is int and value >= 0 and value < len(self._items):
                old = self._selected
                self._items[self._selected].selected = False
                self._selected = value
                self._items[self._selected].selected = True
                self.post(Event(ListBox.LISTBOX_SELECT_CHANGED, old=old, new=self._selected))

    def item(self, index: int ) -> ListItem | None:
        if index < 0 or index >= len(self._items):
            return None
        
        return self._items[index]

    def items(self, indexes: Optional[list[int]] = None) -> list[ListItem]:
        if indexes is None:
            return self._items
        
        return [self._items[i] for i in indexes]
    
    def process(self, event: pygame.event.Event) -> bool:
        showCount = self._rect.height // self._itemHeight

        if event.type == pygame.KEYDOWN:
            adjustScroll = True
            if event.key == pygame.K_UP:
                self._focus = max(0, self._focus - 1)
            elif event.key == pygame.K_DOWN:
                self._focus = min(len(self._items) - 1, self._focus + 1)
            elif event.key == pygame.K_PAGEUP:
                self._focus = max(0, self._focus - 5)
            elif event.key == pygame.K_PAGEDOWN:
                self._focus = min(len(self._items) - 1, self._focus + 5)
            elif event.key == pygame.K_HOME:
                self._focus = 0
            elif event.key == pygame.K_END:
                self._focus = len(self._items) - 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.selected = self._focus
                self.post(Event(ListBox.LISTBOX_LCLICK, index=self.selected))
            else:
                adjustScroll = False

            if adjustScroll:
                if self._focus < self._scroll:
                    self.post(Event(ListBox.LISTBOX_SCORLL_CHANGED, scroll=self._focus))
                    self._scroll = self._focus
                elif self._focus >= self._scroll + showCount:
                    self.post(Event(ListBox.LISTBOX_SCORLL_CHANGED, scroll=self._focus))
                    self._scroll = self._focus - showCount + 1

                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._rect.collidepoint(event.pos):
                if event.button == 1:
                    print("click left button", pygame.time.get_ticks())

                    self._focus = self._scroll + (event.pos[1] - self._rect.top) // self._itemHeight
                    self.selected = self._focus
                    self._click_nums += 1
                    print("click nums:", self._click_nums)
                    
                    self._click_tick = pygame.time.get_ticks()
                elif event.button == 4:
                    newValue = max(0, self._scroll - 1)
                    if newValue != self._scroll:
                        self._scroll = newValue
                        self.post(Event(ListBox.LISTBOX_SCORLL_CHANGED, scroll=self._scroll))
                elif event.button == 5:
                    newValue = min(len(self._items) - self._rect.height // self._itemHeight - 1, self._scroll + 1)
                    if newValue != self._scroll:
                        self._scroll = newValue
                        self.post(Event(ListBox.LISTBOX_SCORLL_CHANGED, scroll=self._scroll))
                else:
                    return False
                
                return True
        
        return False

        # if self._selected < self._scroll:
        #     self._scroll = self._selected
        # elif self._selected >= self._scroll + showCount:
        #     self._scroll = self._selected - showCount + 1

    def update(self):
        if self._click_nums > 0 and pygame.time.get_ticks() - self._click_tick > 300:
            if self._click_nums == 1:
                self.post(Event(ListBox.LISTBOX_LCLICK, index=self._focus))
            elif self._click_nums == 2:
                self.post(Event(ListBox.LISTBOX_LDBLCLICK, index=self._focus))
            
            self._click_nums = 0

    def draw(self, surface: pygame.Surface) -> None:
        if self._style.backgroundImage is not None:
            surface.blit(self._style.backgroundImage, (0, 0))

        if self._style.borderSize > 0:
            pygame.draw.rect(surface, self._style.borderColor, self._rect, self._style.borderSize, self._style.borderRoundCorner)

        for i, item in enumerate(self._items[self._scroll:]):
            if i * self._itemHeight >= self._rect.height - self._itemHeight:
                break
            
            # draw items
            item_rect = pygame.Rect(
                self._rect.x + self.style.borderSize, 
                self._rect.y + self.style.borderSize + i * self._itemHeight, 
                self._rect.width - self.style.borderSize * 2, 
                self._itemHeight,
            )

            # calc padding
            item_rect.top += self._itemStyle.padding[Padding.TOP.value]
            item_rect.right -= self._itemStyle.padding[Padding.RIGHT.value]
            item_rect.bottom -= self._itemStyle.padding[Padding.BOTTOM.value]
            item_rect.left += self._itemStyle.padding[Padding.LEFT.value]

            textColor = pygame.Color(255,255,255)
            # draw item background
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                # hover item
                if self._itemStyle.hoverColor is not None:
                    pygame.draw.rect(surface, self._itemStyle.hoverColor, item_rect)
                
                textColor = self._itemStyle.hoverTextColor
            elif item.selected:
                # selected item
                if self._itemStyle.selectedColor is not None:
                    pygame.draw.rect(surface, self._itemStyle.selectedColor, item_rect)
                
                textColor = self._itemStyle.selectedTextColor
            else:
                # normal item
                if self._itemStyle.normalColor is not None:
                    pygame.draw.rect(surface, self._itemStyle.normalColor, item_rect)

                textColor = self._itemStyle.normalTextColor

            if i + self._scroll == self._focus:
                # focus rect
                focus_rc = pygame.Rect(
                    item_rect.left + self._itemStyle.padding[Padding.LEFT.value],
                    item_rect.top + self._itemStyle.padding[Padding.TOP.value],
                    item_rect.right - self._itemStyle.padding[Padding.RIGHT.value] - item_rect.left - self._itemStyle.padding[Padding.LEFT.value],
                    item_rect.bottom - self._itemStyle.padding[Padding.BOTTOM.value] - item_rect.top - self._itemStyle.padding[Padding.TOP.value]
                )
                if self._itemStyle.focusColor is not None:
                    pygame.draw.rect(surface, self._itemStyle.focusColor, focus_rc, 1, 3)

            if self._itemStyle.borderSize > 0 and self._itemStyle.borderColor is not None:
                # draw item border
                pygame.draw.rect(surface, self._itemStyle.borderColor, item_rect, self._itemStyle.borderSize, self._itemStyle.borderRoundCorner)

            if item.icon is not None:
                # draw icon
                icon_rect = ((
                        self._rect.x 
                            + self._style.borderSize 
                            + self._itemStyle.borderSize 
                            + self._itemStyle.padding[Padding.LEFT.value],
                        self._rect.y 
                            + i * self._itemHeight 
                            + (self._itemHeight - self._itemStyle.iconSize[1]) // 2
                            + self._itemStyle.padding[Padding.TOP.value],
                    ),
                    self._itemStyle.iconSize
                )

                surface.blit(self._shared_icon(item.icon), icon_rect)
            
            # draw text
            if textColor is not None:
                text_tex = self._font.render(item.text, True, textColor)
                if self._itemStyle.align == "center":
                    # center align
                    text_rect = text_tex.get_rect()
                    text_rect.topleft = (
                        self._rect.centerx - text_rect.width // 2, 
                        self._rect.y 
                            + i * self._itemHeight 
                            + (self._itemHeight - text_rect.height) // 2
                            + self._itemStyle.padding[Padding.TOP.value]
                    )

                elif self._itemStyle.align == "right":
                    # right align
                    text_rect = text_tex.get_rect()
                    text_rect.topleft = (
                        self._rect.right 
                            - text_rect.width 
                            - self._itemStyle.borderSize 
                            - self._style.borderSize
                            - self._itemStyle.padding[Padding.RIGHT.value],
                        self._rect.y 
                            + i * self._itemHeight 
                            + (self._itemHeight - text_rect.height) // 2
                            + self._itemStyle.padding[Padding.TOP.value]
                    )
                else:
                    # left align (default)
                    text_rect = text_tex.get_rect()
                    text_rect.topleft = (
                        self._rect.x 
                            + self._style.borderSize
                            + self._itemStyle.borderSize
                            + self._itemStyle.iconSize[0]
                            + self._itemStyle.iconPadding
                            + self._itemStyle.padding[Padding.LEFT.value],
                        self._rect.y 
                            + i * self._itemHeight 
                            + (self._itemHeight - text_rect.height) // 2
                            + self._itemStyle.padding[Padding.TOP.value]
                    )
                    
                surface.blit(text_tex, text_rect)

        super().draw(surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    utils.ResourceManager.loadFont("font/msyh.ttc", 16, "default")

    icon = pygame.image.load("images/folder1.png")
    listbox = ListBox((100, 100, 200, 300), 32, [
        ("Item 1", icon),
        ("Item 2", icon),
        ("Item 3", icon),
        ("Item 4", icon),
        ("Item 5", icon),
        ("Item 6", icon),
        ("Item 7", icon),
        ("Item 8", icon),
        ("Item 9", icon),
        ("Item 10",icon),
        ("Item 11", icon),
        ("Item 12", icon),
        ("Item 13", icon),
        ("Item 14", icon),
        ("Item 15", icon),
        ("Item 16", icon),
        ("Item 17", icon),
        ("Item 18", icon),
        ("Item 19", icon),
        ("Item 20", icon),
    ])
    listbox.style.backgroundColor = (192, 192, 192)
    listbox.style.borderColor = (255, 255, 255)
    listbox.style.borderSize = 1
    listbox.style.borderRoundCorner = 5
    listbox.itemStyle.normalTextColor = (0, 0, 255)
    listbox.itemStyle.borderColor = (255, 0, 120)
    listbox.itemStyle.borderSize = 1
    listbox.itemStyle.normalColor = (174, 128, 55)
    listbox.itemStyle.selectedColor = (178, 0, 0)
    listbox.itemStyle.focusColor = (255, 255, 255)
    listbox.itemStyle.hoverColor = (0, 255, 0)
    listbox.itemStyle.iconSize = (16, 16)
    listbox.itemStyle.iconPadding = 10
    listbox.itemStyle.align = "left"
    listbox.itemStyle.padding = (2, 4)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            listbox.process(event)
        
        screen.fill((0, 0, 0))
        listbox.draw(screen)
        pygame.display.flip()
        clock.tick(60)