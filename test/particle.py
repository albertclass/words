import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 设置窗口大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("烟花动画")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0),
          (0, 0, 255), (75, 0, 130), (238, 130, 238)]

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (int(random.uniform(0, 255)), int(random.uniform(0, 255)), int(random.uniform(0, 255)))
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = random.uniform(70, 140)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

class Firework:
    def __init__(self, x: int, y: int, n: int | None = None):
        self._particles = [Particle(x, y)]
        for _ in range(n or int(random.uniform(80,120))):
            self._particles.append(Particle(x, y))
    
    @property
    def alive(self) -> bool:
        return any(particle.life > 0 for particle in self._particles)
    
    def update(self):
        alived = []
        for particle in self._particles:
            particle.update()
            if particle.life > 0:
                alived.append(particle)
        
        self._particles = alived
    
    def draw(self):
        for particle in self._particles:
            particle.draw()

fireworks = []

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            fireworks.append(Firework(x, y))

    screen.fill(BLACK)

    alived = []
    for firework in fireworks:
        firework.update()
        if firework.alive:
            alived.append(firework)
    
    fireworks = alived
    for firework in fireworks:
        firework.draw()
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()