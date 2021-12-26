import os, sys, pygame

pygame.init()
str = "1234567890"
lst = [ord(ch) for ch in str]
print(lst)

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
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.last = 0
        self.texture = image
        self.rect = (0, 0, letter_w, letter_h)
        self.image = self.texture.subsurface(self.rect)
        self.iter = 0
        
    def update(self, time, rate=600):
        if time > self.last + rate:
            self.last = self.last + rate
            self.rect = (self.iter * letter_w, 0, letter_w, letter_h)
            self.image = self.texture.subsurface(self.rect)
            self.iter = self.iter + 1
            if self.iter >= 94:
                self.iter = 0


letter = Letter()
group = pygame.sprite.Group()
group.add(letter)

while True:
    tick = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            exit()

    screen.fill((0,0,0))
    group.update(tick)
    group.draw(screen)

    pygame.display.update()
    
