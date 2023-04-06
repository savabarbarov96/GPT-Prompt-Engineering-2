import pygame
import sys
import os
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_COLOR = (0, 255, 0)
PLATFORM_COLOR = (100, 100, 100)
GRAVITY = 1
JUMP_FORCE = 15
BG_SCROLL_SPEED = 2
PARALLAX_FACTOR = 0.5
DRAG = 0.9
ACCELERATION = 0.5
MAX_SPEED = 10

# Initialize Pygame
pygame.init()

# Create a window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Game")

def load_image(name):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), name)).convert_alpha()

player_image = load_image('rubara.png')
background_image = pygame.transform.scale(load_image('background.png'), (SCREEN_WIDTH * 2, SCREEN_HEIGHT))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 100, 100
        self.vx, self.vy = 0, 0
        self.facing_right = True

    def update(self, platforms):
        self.vy += GRAVITY

        if self.vx > 0:
            self.facing_right = False
            self.image = pygame.transform.flip(player_image, True, False)
        elif self.vx < 0:
            self.facing_right = True
            self.image = pygame.transform.flip(player_image, False, False)

        self.rect.x += self.vx
        self.rect.x %= SCREEN_WIDTH

        collisions = [p for p in platforms if self.rect.colliderect(p.rect)]
        for platform in collisions:
            if self.vx > 0:
                self.rect.right = platform.rect.left
            elif self.vx < 0:
                self.rect.left = platform.rect.right

        self.rect.y += self.vy
        collisions = [p for p in platforms if self.rect.colliderect(p.rect)]
        for platform in collisions:
            if self.vy > 0:
                self.rect.y = platform.rect.y - self.rect.height
                self.vy = 0

    def jump(self):
        if self.on_ground():
            self.vy -= JUMP_FORCE

    def on_ground(self):
        return self.rect.y + self.rect.height >= SCREEN_HEIGHT

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(load_image('coin.png'), (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        self.rect.y += 5

def spawn_coin():
    x = random.randint(0, SCREEN_WIDTH - 32)
    y = 0
    return Coin(x, y)

def main():
    clock = pygame.time.Clock()
    player = Player()
    floor = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
    platforms = [floor]
    all_sprites = pygame.sprite.Group(*platforms, player)

    bg_x = 0

    coins = pygame.sprite.Group()
    coin_spawn_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.vx -= ACCELERATION
        elif keys[pygame.K_RIGHT]:
            player.vx += ACCELERATION
        else:
            player.vx *= DRAG

        player.vx = max(min(player.vx, MAX_SPEED), -MAX_SPEED)

        player.update(platforms)

        if player.facing_right:
            bg_x += BG_SCROLL_SPEED
        else:
            bg_x -= BG_SCROLL_SPEED

        bg_x %= -background_image.get_width() // 2

        screen.fill((0, 0, 0))
        screen.blit(background_image, (bg_x, 0))
        all_sprites.draw(screen)

        coin_spawn_timer += 1
        if coin_spawn_timer > 60:  # Spawn a coin every 60 frames
            coin = spawn_coin()
            coins.add(coin)
            all_sprites.add(coin)
            coin_spawn_timer = 0

        coins.update()
        collected_coins = pygame.sprite.spritecollide(player, coins, True)
        for coin in collected_coins:
            print("Coin collected!")

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    