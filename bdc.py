import os, sys, pygame
import urllib.request
from lxml import etree
import re 
import time
from functools import reduce
import json

class Book:
    def __init__(self):
        self.dirty = False
        self.words = []
        self.iter = 0

    def isEmpty(self):
        return len(self.words) == 0

    def add(self, word, content):
        self.words.append({
            "word" : word,
            #出现次数
            "count" : 0,
            #错误次数
            "wrong" : 0,
            #正确次数，错误时重置该值
            "right" : 0,
            #熟练度, 0 - 100
            "proficiency" : 0,
            #单词详细信息
            "content" : content
        })

    def new(self):
        f = open(os.path.join("book", self.name + ".txt"))
        try:
            lines = f.readlines()
            words = [ln[:-1] for ln in lines]
            self.dict.newBook(words, self)
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

        return False

    def save(self, account):
        if not self.dirty:
            return True

        f = open(self.file, "w")
        json.dump(self.words, f, indent = "  ", skipkeys=("content"))
        f.close()
        return True

    def __iter__(self):
        self.iter = 0
        return self

    def __next__(self):
        if len(self.words) == 0:
            raise StopIteration
        
        while len(self.words):
            word = self.words[self.iter]
            if word['proficiency'] >= 90:
                del self.words[self.iter]
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

pygame.init()

screen = pygame.display.set_mode((800, 600), 0, 32)
font = pygame.font.SysFont("SimHei", 32)
str=""
for i in range(32, 126):
    str += chr(i)

image = font.render(str, True, [255,255,255])
image_rect = image.get_rect()
letter_w = image_rect.width / 94
letter_h = image_rect.height

class Letter(pygame.sprite.Sprite):
    def __init__(self, char=None, x = 0, y = 0):
        pygame.sprite.Sprite.__init__(self)
        index = ord(char)
        self.char = char
        self.last = 0
        self.texture = image
        self.rect = (x, y, letter_w, letter_h)
        self.char = char
        self.letter('_')
    
    def letter(self, char):
        if char == None:
            return

        ch = ord(char)

        if ch < ord(' ') or ch > ord('~'):
            return

        ch -= ord(' ')

        rect = (ch * letter_w, 0, letter_w, letter_h)

        self.image = self.texture.subsurface(rect)

    def check(self, char):
        if char == self.char:
            self.letter(char)
            return True

        if char == pygame.K_BACKSPACE:
            self.letter('_')

        if char == pygame.K_DELETE:
            self.letter('_')
    
        return False

    def update(self, time, rate=600):
        if time > self.last + rate:
            self.last = self.last + rate

    def correct(self):
        self.letter(self.char)

class Word(pygame.sprite.Group):
    def __init__(self, word, x, y):
        pygame.sprite.Group.__init__()
        self.word = []
        self.x = x - len(word) * (letter_w + 1) / 2
        self.y = y - letter_h / 2
        for ch in word:
            self.word.append(Letter(ch, x, y))
            x += letter_w + 1

        # add to group
        for letter in self.word:
            self.add(letter)

        self.cursor = 0

        for ch in word:
            self.add(Letter(ch, x, y))
            x += letter_w

    def type(self, char):
        if len(self.word) == self.cursor:
            return

        if self.word[self.cursor].check(char):
            self.cursor += 1
        elif char == pygame.K_BACKSPACE:
            self.cursor -= 1

    def complated(self):
        return len(self.word) == self.cursor

d = Dictionary('default')
b = Book('M1U1', d)
if b.isEmpty():
    b.new()

for w in b:
    print(w['word'])

g = Word('albert')

d = Dictionary("Bing")
b = d.newBook("M1U1")
b.load("xuchenhao")
d.save()

running = True

while running:
    tick = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.KEYUP:
            if event.key > pygame.K_FIRST and event.key < pygame.K_LAST:
                pass

    screen.fill((0,0,0))
    group.update(tick)
    group.draw(screen)

    pygame.display.update()

b.save("xuchenhao")