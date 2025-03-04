import os
import sys
import pygame
import pygame_gui as gui
from pygame_gui import elements

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import Database, UserTable
import utils

class LoginScene(utils.Scene):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__("Login", size, 2, 1, *args, **kwargs)
        self.background_image = pygame.image.load("images/background-4.png")
        self._panel = elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (400, 400)),
            manager=self._uimanager,
            anchors={
                'center': 'center',
            }
        )
        self._db = Database("users.db")
        self._table = UserTable(self._db)
        self._table.Create()

        element_width = 300
        list_size: tuple[int, int] = (element_width, 200)
        input_size: tuple[int, int] = (element_width, 50)
        button_size: tuple[int, int] = (element_width, 50)
        spacing = 10
        
        self._user_label = elements.UILabel(
            relative_rect=pygame.Rect((50, 10), (element_width, 30)),
            text="Select User:",
            manager=self._uimanager,
            container=self._panel,
            object_id="#left_aligned_label"
        )
        # self._user_label.text_horiz_alignment = "left"
        # self._user_label.text_horiz_alignment_method = "left_triangle"

        self._user_list = elements.UISelectionList(
            relative_rect=pygame.Rect((0, spacing), list_size),
            item_list=[(user[0], '#item') for user in self._table.QueryAll()],
            manager=self._uimanager,
            container=self._panel,
            anchors={
                'centerx': 'centerx',
                'top': 'top',
                'centerx_target': self._user_label,
                'top_target': self._user_label
            },
            object_id="#user_list"
        )
        
        self._input_box = elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, spacing), input_size),
            initial_text="此处输入用户名",
            manager=self._uimanager,
            container=self._panel,
            anchors={
                'centerx': 'centerx',
                'top': 'top',
                'centerx_target': self._user_list,
                'top_target': self._user_list
            }
        )
        
        self._button = elements.UIButton(
            relative_rect=pygame.Rect((0, spacing), button_size),
            text='Login',
            manager=self._uimanager,
            container=self._panel,
            anchors={
                'centerx': 'centerx',
                'top': 'top',
                'centerx_target': self._input_box,
                'top_target': self._input_box
            }
        )

    def _onEnter(self, prevScene: utils.Scene | None) -> None:
        pass
    
    def _onLeave(self, nextScene: utils.Scene | None) -> None:
        pass
    
    def _onKeyDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onKeyUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseMove(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonDown(self, event: pygame.event.Event) -> None:
        pass
    
    def _onMouseButtonUp(self, event: pygame.event.Event) -> None:
        pass
    
    def _onUIEvent(self, event: pygame.event.Event) -> None:
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._button:
                name = self._input_box.get_text()
                if name == "":
                    return
                
                if name not in [item['text'] for item in self._user_list.item_list]:
                    self._table.Insert(name, "123456")
                    self._user_list.add_items([name])
                
                utils.SceneManager.SetProperty("user", name)
                utils.SceneManager.Switch("Books")

            if event.ui_object_id == "panel.#user_list.#item":
                name = str(event.ui_element.text)
                self._input_box.set_text(name)
    
    def Update(self, *args, **kwargs) -> bool:
        return True
    
    def Draw(self, screen: pygame.Surface) -> None:
        pass
    
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 1024))
    pygame.display.set_caption("兔哥背单词")
    scene = LoginScene((1280, 1024), theme_path="themes.json")

    utils.SceneManager.AddScene("Login", scene, True)
    clock = pygame.time.Clock()

    while utils.SceneManager.Update():
        utils.SceneManager.Draw(screen)
        
        pygame.display.update()
        clock.tick(100)
        
    pygame.quit()