import pygame
import math

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.length = 10
        self.speed = 7
        self.direction = direction

    def update(self):
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600:
            return False
        return True

    def draw(self, screen):
        end_x = self.x + self.length * math.cos(self.direction)
        end_y = self.y + self.length * math.sin(self.direction)
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)
