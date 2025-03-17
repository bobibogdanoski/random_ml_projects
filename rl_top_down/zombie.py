import pygame
import random
import math

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/zombie.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += self.speed * math.cos(angle)
        self.rect.y += self.speed * math.sin(angle)

        angle = math.degrees(math.atan2(dy, dx)) * -1
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
