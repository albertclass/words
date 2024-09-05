import pygame
import random

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

    def draw(self, screen: pygame.Surface):
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
    
    def draw(self, screen: pygame.Surface):
        for particle in self._particles:
            particle.draw(screen)

class Fireworks:
    def __init__(self):
        self._fireworks = []
    
    def add(self, x: int, y: int, n: int | None = None) -> None:
        self._fireworks.append(Firework(x, y, n))
    
    def update(self) -> None:
        for firework in self._fireworks:
            firework.update()
        
        self._fireworks = [firework for firework in self._fireworks if firework.alive]
    
    def draw(self, screen: pygame.Surface) -> None:
        for firework in self._fireworks:
            firework.draw(screen)
