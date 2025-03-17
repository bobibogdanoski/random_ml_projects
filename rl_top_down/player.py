import pygame
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, RL_ENABLED

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/player.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)
        self.speed = 4
        self.prev_x = self.rect.centerx
        self.prev_y = self.rect.centery
        self.velocity = (0,0)
        self.angle = 0
    
    def getPos(self):
        return self.rect.x, self.rect.y
    
    def getVelocity(self):
        return self.velocity

    def getAngle(self):
        return self.angle

    def update(self, move_x = 0, move_y = 0):
        length = math.sqrt(move_x**2 + move_y**2)
        if length != 0:
            move_x /= length
            move_y /= length
        
        self.rect.x += move_x * self.speed
        self.rect.y += move_y * self.speed

        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 60))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - 60))

        self.velocity = (
            self.rect.centerx - self.prev_x,
            self.rect.centery - self.prev_y
        )

        self.prev_x = self.rect.centerx
        self.prev_y = self.rect.centery
        
        if not RL_ENABLED:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - self.rect.centerx
            dy = mouse_pos[1] - self.rect.centery
            self.angle = math.degrees(math.atan2(dy, dx)) * -1
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
