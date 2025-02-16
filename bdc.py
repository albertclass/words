import os
import sys
import math
import pygame
import logging
import utils

logging.basicConfig(filename='word.log', level=logging.DEBUG)
sys.path.append(os.path.abspath('./ECDICT/'))
import stardict
if not os.path.exists("dict.db") and os.path.exists("./ECDICT/ecdict.csv"):
    stardict.convert_dict("dict.db", "./ECDICT/ecdict.csv")

# Create a cursor object to execute SQL commands

create_user = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    book TEXT NOT NULL,
);
"""

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

# define the screen wight and height
screen = pygame.display.set_mode((800, 600), 0, 32)
# load font to display
fonts = [
    pygame.font.SysFont(["Microsoft YaHei", "SimHei", "Lucida Sans Unicode", "dejavusans"], 24),
    pygame.font.SysFont("SimHei", 32), # Arial,Helvetica,Sans-Serif
    pygame.font.SysFont("Calibri", 24),
    pygame.font.SysFont("Microsoft YaHei", 32),
]

running = True

# 关闭输入法
pygame.key.stop_text_input()

# 开始背单词
for w in b:
    s = CharSequence(w.word, screen.get_size())
    g = pygame.sprite.Group()
    # show the phonetic
    # g.add(Sprite(fonts[2].render(w.content["phonetic"], True, [255,255,255]), 10, 40))
    # show the explain
    if "translation" in w.content \
        and w.content["translation"] is not None \
        and type(w.content["translation"]) is str:
            
        translations = w.content["translation"].split("\n")
        for i, translation in enumerate(translations):
            g.add(Sprite(fonts[0].render(translation, True, [255,255,255]), 10, 70 + i * 30))

    wrong = 0
    # wait = pygame.time.get_ticks()
    crack = False
    while running and not s.complated():
        tick = pygame.time.get_ticks()
            
        for event in pygame.event.get():
            # print(event.type, event.dict)

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.TEXTINPUT:
                pygame.key.stop_text_input()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    s.backspace()
                elif event.key == pygame.K_DELETE:
                    s.delete()
                elif event.key == pygame.K_RETURN:
                    if s.is_empty():
                        crack = True
                        # show correct spelling, if wrong more than 3 times
                        answer = fonts[3].render(w.word, True, [200,0,100])
                        answer_rect = answer.get_rect()
                        pos_x = (800 - answer_rect.width) // 2
                        pos_y = (600 - answer_rect.height) // 2
                        g.add(utils.Sprite(answer, pos_x, pos_y))
                        s.reset()
                        w.play()
                    elif s.check() == False:
                        # 回答错误，错误次数 +1
                        wrong += 1
                        b.wrong(w)
                        s.reset()
                        
                        if wrong == 1:
                            # play the pronunciation, if wrong more than 1 times
                            w.play()
                        if wrong == 2:
                            # show the phonetic symbol, if wrong more than 2 times
                            pron = utils.Sprite(fonts[2].render(w.content["phonetic"], True, [255,255,255]), 10, 40)
                            g.add(pron)
                        if wrong == 3:
                            # show correct spelling, if wrong more than 3 times
                            answer = fonts[3].render(w.word, True, [200,0,100])
                            answer_rect = answer.get_rect()
                            pos_x = (800 - answer_rect.width) // 2
                            pos_y = (600 - answer_rect.height) // 2
                            g.add(utils.Sprite(answer, pos_x, pos_y))
                            break
                    elif not crack:
                        # 回答正确，正确次数 +1
                        b.right(w)
                        pygame.time.wait(1000)
                # elif event.mod & pygame.KMOD_SHIFT:
                #     s.press(event.key)
                elif len(event.unicode) > 0:
                    s.press(event.unicode)
                    
        screen.fill((0,0,0))

        screen.blit(fonts[0].render(f"评价：{w.proficiency:1f} 分", True, (255,255,255)), (300, 10))
        screen.blit(fonts[0].render(f"用时：{tick/1000:5.2f} 秒", True, (255,255,255)), (580, 10))
        
        s.update(tick)
        s.draw(screen)

        g.update(tick)
        g.draw(screen)

        pygame.display.update()
        pygame.display.flip()

    if not running:
        break
else:
    print("finished.")
    pass