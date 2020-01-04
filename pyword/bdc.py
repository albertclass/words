import json
import os
import re
import sys
import time
import urllib.request
from functools import reduce

import pygame
from lxml import etree


class Book:
    def __init__(self, name, dictionary):
        self.dirty = False
        self.words = []
        self.name = name
        self.file = name + ".json"
        self.iter = 0
        self.dictionary = dictionary

    def isEmpty(self):
        return len(self.words) == 0

    def add(self, word, content):
        props = {
            "word" : word,
            #出现次数
            "count" : 0,
            #错误次数
            "wrong" : 0,
            #正确次数，错误时重置该值
            "right" : 0,
            #熟练度, 0 - 100
            "proficiency" : 100,
            #单词详细信息
            "content" : content
        }

        self.words.append(type('Word', (object,), props))

    def new(self):
        f = open(os.path.join("book", self.name + ".txt"))
        try:
            lines = f.readlines()
            words = [ln[:-1] for ln in lines]
            self.dictionary.newBook(words, self)
        except Exception as e:
            print(e)

    def load(self):
        if os.path.exists(self.file):
            f = open(self.file)
            try:
                self.words = json.load(f)
            except Exception as e:
                print("%s line = %d, position = %d" % (e.msg, e.lineno, e.pos))
                return False
            
            f.close
            return True

        return False

    def save(self, account):
        f = open(self.file, "w")
        json.dump(self.words, f, indent = "  ", skipkeys=("content", "proficiency"))
        f.close()
        return True

    def __iter__(self):
        self.iter = 0
        return self

    def __next__(self):
        if len(self.words) == 0:
            raise StopIteration
        
        while len(self.words):
            word = self.words[self.iter % len(self.words)]
            if word.proficiency > 100:
                del self.words[self.iter % len(self.words)] 
            else:
                self.iter += 1
                return word
        else:
            raise StopIteration

        
class Dictionary:
    def __init__(self, name):
        self.name = name
        self.file = self.name + ".json"
        self.words = {}
        self.dirty = False

        if not os.path.isdir("pronunciation"):
            os.mkdir("pronunciation")
        
        if not os.path.isdir("pronunciation/en"):
            os.mkdir("pronunciation/en")
    
        if not os.path.isdir("pronunciation/us"):
            os.mkdir("pronunciation/us")

        if os.path.exists(self.file):
            f = open(self.file)
            try:
                self.words = json.load(f)
            except Exception as e:
                print("%s line = %d, position = %d" % (e.msg, e.lineno, e.pos))
            
            f.close

    # 获取单词信息
    def get(self, word):
        return self.words[word]

    #下载音标文件
    def download(url, out):
        try:
            if url.startswith("http://") or url.startswith("https://"):
                urllib.request.urlretrieve(url, out)
            else:
                return False
        except Exception as e:
            print('download_http_source error %s' % str(e))
            return False

    #获得页面数据
    def getPage(word):
        try:
            basurl='http://cn.bing.com/dict/search?q='
            searchurl=basurl+word.replace(' ', '+')
            response = urllib.request.urlopen(searchurl)
            html = response.read()
            return html
        except Exception as e:
            print('got page falut (%s)' % (str(e)))
            return None

    #获得单词释义
    def getExplains(html_selector):
        explains=[]
        hanyi_xpath='/html/body/div[1]/div/div/div[1]/div[1]/ul/li'
        get_hanyi=html_selector.xpath(hanyi_xpath)
        for item in get_hanyi:
            it=item.xpath('span')
            ix=it[1].getchildren()
            explains.append('%s - %s' % (it[0].text, reduce(lambda x, y: x + y.text, ix, "")))
            
        return explains

    #获得单词音标和读音连接
    def getPronunciation(html_selector, word):
        pronunciation={}
        pronunciation_xpath='/html/body/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div'
        bbb="(https\\:.*?mp3)"
        reobj1=re.compile(bbb,re.I|re.M|re.S)
        pronunciations=html_selector.xpath(pronunciation_xpath)
        for item in pronunciations:
            it=item.xpath('div')
            if len(it)>0:
                voice=reobj1.findall(it[1].xpath('a')[0].get('onmouseover',None))
                pronunciation["us"] = it[0].text
                Dictionary.download(voice[0], "./pronunciation/us/" + word + ".mp3")
                voice=reobj1.findall(it[3].xpath('a')[0].get('onmouseover',None))
                pronunciation["en"] = it[2].text
                Dictionary.download(voice[0], "./pronunciation/en/" + word + ".mp3")

        return pronunciation

    #获得例句
    def getExample(html_selector):
        examples=[]
        get_example_e=html_selector.xpath('//*[@class="val_ex"]')
        get_example_cn=html_selector.xpath('//*[@class="bil_ex"]')
        get_len=len(get_example_e)
        for i in range(get_len):
            example = {}
            example["en"] = get_example_e[i].text
            example["cn"] = get_example_cn[i].text

            examples.append(example)

        return examples

    def getWord(word):
        content = {}
        #获得页面
        page=Dictionary.getPage(word)
        if page != None:
            selector = etree.HTML(page.decode('utf-8'))
            #单词释义
            content["explain"] = Dictionary.getExplains(selector)
            #单词音标及读音
            content["pronunciation"] = Dictionary.getPronunciation(selector, word) 
            #例句
            content["example"] = Dictionary.getExample(selector)

        return content

    def newBook(self, words, book):
        book = book or Book()

        for word in words:
            if not self.words.__contains__(word):    
                time.sleep(0.2)
                print("loading %s" % (word))
                info = Dictionary.getWord(word.rstrip())

                self.words[word] = info
                self.dirty = True

            book.add(word, self.words[word])

        return book

    def save(self):
        if not self.dirty:
            return

        f = open(self.file, "w")
        json.dump(self.words, f, indent = "  ")
        f.close()

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x = 0, y = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(x, y, self.image.get_rect().width, self.image.get_rect().height)
    
    def height(self):
        return self.rect.height

    def width(self):
        return self.rect.width

class Letter(pygame.sprite.Sprite):
    def __init__(self, char=None, x = 0, y = 0):
        pygame.sprite.Sprite.__init__(self)
        index = ord(char)
        self.char = char
        self.type = char
        self.last = 0
        self.texture = image
        self.rect = (x, y, letter_w, letter_h)
        self.set('_')
    
    def set(self, char):
        if char == None:
            return
        
        ch = ord(char)
        if ch >= ord(' ') and ch <= ord('~'):
            self.type = char

            ch -= ord(' ')
            self.image = self.texture.subsurface((ch * letter_w, 0, letter_w, letter_h))

    def reset(self):
        self.set('_')
        
    def press(self, char):
        self.set(char)

    def correct(self):
        return self.type == self.char

class CharSequence(pygame.sprite.Group):
    def __init__(self, word, x, y):
        pygame.sprite.Group.__init__(self)
        self.sequence = []
        self.x = x - len(word) * (letter_w + 1) / 2
        self.y = y - letter_h / 2
        self.judge = False
        self.complate = False

        for ch in word:
            self.sequence.append(Letter(ch, x, y))
            x += letter_w + 1

        # add to group
        for letter in self.sequence:
            self.add(letter)

        self.cursor = 0

    def press(self, char):
        if self.cursor < len(self.sequence):
            self.sequence[self.cursor].press(char if type(char) == "str" else chr(char))
            self.cursor += 1

    def delete(self):
        if self.cursor >= 0 and self.cursor < len(self.sequence):
            self.sequence[self.cursor].reset()

    def backspace(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.delete()

    def check(self):
        if not self.judge:
            # judge word is correct
            for ch in self.sequence:
                if not ch.correct():
                    break
            else:
                self.judge = True

            self.complate = True

        return self.judge

    def complated(self):
        return self.complate

class Pronunciation(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        ch = content["pronunciation"]["en"]
        en = Sprite(font.render(ch, True, [255,255,255]), x, y)
        ch = content["pronunciation"]["us"]
        us = Sprite(font.render(ch, True, [255,255,255]), x, y + en.height())
        
        self.add(en)
        self.add(us)

class Explain(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["explain"]:
            self.add(Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

class Example(pygame.sprite.Group):
    def __init__(self, content, x, y, font):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y

        for exp in content["example"]:
            self.add(Sprite(font.render(exp, True, [255,255,255]), x, y))
            y += 30

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

screen = pygame.display.set_mode((800, 600), 0, 32)
font = [
    pygame.font.SysFont("SimHei", 20),
    pygame.font.SysFont("SimHei", 32), # Arial,Helvetica,Sans-Serif
    pygame.font.SysFont("Arial", 24),
]

str=""
for i in range(32, 126):
    str += chr(i)

image = font[1].render(str, True, [255,255,255])
image_rect = image.get_rect()
letter_w = image_rect.width / 94
letter_h = image_rect.height
sound = "en"

d = Dictionary('default')
b = Book('M1U1', d)
if b.isEmpty():
    b.new()

d.save()

running = True

mp3 = ""

for w in b:
    s = CharSequence(w.word, 400, 540)
    w.count += 1
    factor = 0.1

    p = Pronunciation(w.content, 10, 10, font[2])
    e = Explain(w.content, 10, 70, font[0])

    mp3 = "./pronunciation/" + sound + "/" + w.word + ".mp3"
    if os.path.exists(mp3):
        pygame.mixer.music.load(mp3)
        pygame.mixer.music.play()
    
    while running and not s.complated():
        tick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    s.backspace()
                elif event.key == pygame.K_DELETE:
                    s.delete()
                elif event.key == pygame.K_RETURN:
                    s.check()
                else:
                    s.press(event.key)

        screen.fill((0,0,0))
        # y = 100
        # for img in uniimg:
        #     screen.blit(img, (0, y))
        #     y += 30

        screen.blit(font[0].render("评价：%.1f 分" % (w.proficiency), True, (255,255,255)), (300, 10))
        screen.blit(font[0].render("用时：%5.2f 秒" % (tick/1000), True, (255,255,255)), (580, 10))
        
        s.update(tick)
        s.draw(screen)

        p.update(tick)
        p.draw(screen)

        e.update(tick)
        e.draw(screen)

        pygame.display.update()
        pygame.display.flip()

    if not running:
        break

    if s.check():
        w.right += 1
        w.proficiency += 1
    else:
        w.wrong += 1
else:
    print("finished.")
    pass

b.save("xuchenhao")
