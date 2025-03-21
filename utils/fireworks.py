import pygame
import random
import math
from abc import ABC, abstractmethod

class Particle:
    def __init__(self, x, y, vx: float, vy: float, life: float, color: tuple[int, int, int], gravity: float = 0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.color = color
        self.gravity = gravity
    
    def update(self, deltatime: float):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= deltatime

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

class Firework(ABC):
    def __init__(self, x: int, y: int, n: int | None = None):
        self._particles = []
        self._x = x
        self._y = y
        self._n = n
        self._generate()

    @abstractmethod
    def _generate(self):
        pass

    @property
    def alive(self) -> bool:
        return any(particle.life > 0 for particle in self._particles)
    
    def update(self, deltatime: float):
        alived = []
        for particle in self._particles:
            particle.update(deltatime)
            if particle.life > 0:
                alived.append(particle)
        
        self._particles = alived
    
    def draw(self, screen: pygame.Surface):
        for particle in self._particles:
            particle.draw(screen)

class RandomFirework(Firework):
    def __init__(self, x: int, y: int, n: int | None = None):
        super().__init__(x, y, n)

    def _generate(self):
        color = (int(random.uniform(172,255)), int(random.uniform(172,255)), int(random.uniform(172,255))) # color
        for _ in range(self._n or int(random.uniform(80,120))):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self._particles.append(
                Particle(
                    self._x, # x pos
                    self._y, # y pos
                    math.cos(angle) * speed, # x velocity
                    math.sin(angle) * speed, # y velocity
                    random.uniform(1, 2),  # life time
                    color
                )
            )

class Fireworks:
    def __init__(self):
        self._fireworks = []
        self._lasttick = pygame.time.get_ticks()
    
    def add(self, x: int, y: int, n: int | None = None) -> None:
        self._fireworks.append(RandomFirework(x, y, n))
    
    def update(self) -> None:
        deltatime = (pygame.time.get_ticks() - self._lasttick) / 1000
        self._lasttick = pygame.time.get_ticks()
        for firework in self._fireworks:
            firework.update(deltatime)
        
        self._fireworks = [firework for firework in self._fireworks if firework.alive]
    
    def draw(self, screen: pygame.Surface) -> None:
        for firework in self._fireworks:
            firework.draw(screen)
