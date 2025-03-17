import pygame
import random
import math
from player import Player
from zombie import Zombie
from bullet import Bullet
from settings import *
if RL_ENABLED:
    from mlp import Agent

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Shooter")

def spawn_zombie(player_x, player_y, min_distance=150):
    while True:
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        distance = math.sqrt((x - player_x) ** 2 + (y - player_y) ** 2)
        if distance >= min_distance:
            return Zombie(x, y)

def main():
    player = Player()
    zombies = pygame.sprite.Group()
    bullets = []
    all_sprites = pygame.sprite.Group()
    
    all_sprites.add(player)

    for _ in range(INIT_NUM_ZOMBIES):
        zombie = spawn_zombie(player.rect.centerx, player.rect.centery)
        zombies.add(zombie)
        all_sprites.add(zombie)

    zombie_spawn_time = 0

    def get_state():
        nn_zombies = list(zombies)
        if len(zombies) >= MAX_ZOMBIES:
            nn_zombies = nn_zombies[:MAX_ZOMBIES]
        else:
            nn_zombies += [(0, 0)] * (max(0, MAX_ZOMBIES - len(zombies)))

        for i in range(min(len(zombies), MAX_ZOMBIES)):
            x, y = nn_zombies[i].rect.center
            nn_zombies[i] = (x, y)

        survival_time = pygame.time.get_ticks() / 1000
        player_x, player_y = player.getPos()
        player_vel_x, player_vel_y = player.getVelocity()
        player_angle = player.getAngle()

        state = [survival_time, player_x, player_y, player_vel_x, player_vel_y, player_angle]
        for x, y in nn_zombies:
            state.append(x)
            state.append(y)
        
        return state

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not RL_ENABLED and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    player_x, player_y = player.rect.center
                    angle = math.atan2(mouse_y - player_y, mouse_x - player_x)
                    bullet = Bullet(player_x, player_y, angle)
                    bullets.append(bullet)

        if not RL_ENABLED:
            keys = pygame.key.get_pressed()
            move_x = 0
            move_y = 0
            if keys[pygame.K_a]:
                move_x -= 1
            if keys[pygame.K_d]:
                move_x += 1
            if keys[pygame.K_w]:
                move_y -= 1
            if keys[pygame.K_s]:
                move_y += 1
            
            player.update(move_x, move_y)

        zombies.update(player)

        reward = 0
        if RL_ENABLED:
            pygame.current_state = get_state()
            move_x, move_y, angle, shoot = Agent.predict(pygame.current_state)
            player.image = pygame.transform.rotate(player.original_image, angle)
            player.update(move_x, move_y)
            
            #if shoot:
            #    player_x, player_y = player.getPos()
            #    bullet = Bullet(player_x, player_y, angle)
            #    bullets.append(bullet)

        for bullet in bullets:
            bullet.update()
            bullet.draw(screen)

            for zombie in zombies:
                if zombie.rect.collidepoint(bullet.x, bullet.y):
                    #reward = 1
                    
                    zombies.remove(zombie)
                    bullets.remove(bullet)
                    all_sprites.remove(zombie)
                    break
        
        died = False
        #if RL_ENABLED:
        player_x, player_y = player.getPos()
        for zombie in zombies:
            if zombie.rect.collidepoint(player_x, player_y):
                died = True
                reward = -1
                break
        
        if reward != 0:
            Agent.reward(pygame.current_state, reward, get_state())
            if died:
                running = False


        zombie_spawn_time += 1
        if zombie_spawn_time > 50:
            zombie_spawn_time = 0
            zombie = spawn_zombie(player.rect.centerx, player.rect.centery)
            zombies.add(zombie)
            all_sprites.add(zombie)

        all_sprites.draw(screen)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
