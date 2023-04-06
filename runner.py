import pygame
import sys
import os
import random
import pygame.font

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_COLOR = (0, 255, 0)
PLATFORM_COLOR = (100, 100, 100)
GRAVITY = 1
JUMP_FORCE = 18
BG_SCROLL_SPEED = 2
PARALLAX_FACTOR = 0.5
DRAG = 0.95
ACCELERATION = 15
MAX_SPEED = 15
MAX_COMBO_METER = 100

# Additional constants
NUM_LAYERS = 3
DOUBLE_JUMP_ALLOWED = 1
SHADOW_OFFSET = 5
SHADOW_COLOR = (50, 50, 50)
FONT_COLOR = (255, 255, 255)

def draw_text(surface, text, x, y, font_size=35, color=(220,20,60)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.x, text_rect.y = x, y
    surface.blit(text_surface, text_rect)

# Initialize Pygame
pygame.init()

# Create a window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Game")

def load_image(name):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), name)).convert_alpha()

player_image = load_image('rubara.png')
background_image = pygame.transform.scale(load_image('background.png'), (SCREEN_WIDTH * 2, SCREEN_HEIGHT))

class ParallaxBackground:
    def __init__(self, image, scroll_speed):
        self.image = image
        self.scroll_speed = scroll_speed
        self.offset = 0

    def update(self):
        self.offset += self.scroll_speed
        if self.offset >= self.image.get_width() // 2:
            self.offset -= self.image.get_width() // 2

    def draw(self, surface):
        x = -self.offset
        while x < SCREEN_WIDTH:
            surface.blit(self.image, (x, 0))
            x += self.image.get_width() // 2

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 100, 100
        self.vx, self.vy = -500, 80
        self.facing_right = True
        self.coin_count = 0
        self.combo_meter = 0
        self.double_jump_count = 0

    def update(self, platforms):
        self.vy += GRAVITY

        if self.vx > 0:
            self.facing_right = False
            self.image = pygame.transform.flip(player_image, True, False)
        elif self.vx < 0:
            self.facing_right = True
            self.image = pygame.transform.flip(player_image, False, False)

        self.vx *= DRAG
        self.vx = max(min(self.vx, MAX_SPEED), -MAX_SPEED)
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
                self.double_jump_count = 0

        if self.on_ground():
            self.double_jump_count = 0

    def jump(self):
        if self.on_ground() or self.double_jump_count < DOUBLE_JUMP_ALLOWED:
            self.vy = -JUMP_FORCE * (1 - 0.5 * self.double_jump_count)
            self.double_jump_count += 1

    def on_ground(self):
        return self.rect.y + self.rect.height >= SCREEN_HEIGHT - 32

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
        self.speed = random.uniform(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = -self.rect.height
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)


class EvilCoin(Coin):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.scale = random.uniform(1, 2)
        self.image = pygame.transform.scale(load_image('evil_coin.png'), (int(130 * self.scale), int(130 * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed = random.uniform(1, 3)
        self.glow_image = pygame.transform.scale(load_image('evil_coin_glow.png'), (int(130 * self.scale), int(130 * self.scale)))

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = -self.rect.height
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)

def gradient_background(width, height, start_color, end_color):
    gradient_surface = pygame.Surface((width, height))
    for y in range(height):
        color = [start_color[i] + (end_color[i] - start_color[i]) * y // height for i in range(3)]
        pygame.draw.line(gradient_surface, color, (0, y), (width, y))
    return gradient_surface

def game_over_screen(screen):
    gradient_surf = gradient_background(SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0), (76, 0, 153))
    screen.blit(gradient_surf, (0, 0))
    draw_text(screen, "GG, rubara se prezoba", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 40, font_size=50, color=(255, 255, 255))

    for seconds_until_restart in range(5, 0, -1):
        screen.blit(gradient_surf, (0, 0))
        draw_text(screen, "GG, rubara se prezoba", SCREEN_WIDTH // 3 - 60, SCREEN_HEIGHT // 3 - 40, font_size=50, color=(255, 255, 255))
        draw_text(screen, f"Otnovo v studioto sled {seconds_until_restart} seconds...", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, color=(255, 255, 255))
        pygame.display.flip()
        pygame.time.delay(1000)  # Wait for 1 second

    screen.blit(gradient_surf, (0, 0))
    draw_text(screen, "YEA BUDDY", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50, font_size=50, color=(255, 255, 255))
    draw_text(screen, "Grebane s tesen xvat...", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20, color=(255, 255, 255))
    pygame.display.flip()
    pygame.time.delay(1000)  # Wait for 1 second




def main():
    clock = pygame.time.Clock()
    running = True
    game_over = False
    parallax_background = ParallaxBackground(background_image, BG_SCROLL_SPEED)
    player = Player()
    platforms = [Platform(0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32)]
    coins = [Coin(random.randint(50, SCREEN_WIDTH - 50), random.randint(-100, -32)) for _ in range(10)]
    evil_coins = [EvilCoin(random.randint(50, SCREEN_WIDTH - 50), random.randint(-200, -32)) for _ in range(3)]

    while running:
        clock.tick(60)  # Set game to run at 60 FPS

        if game_over:
            game_over_screen(screen)
            game_over = False
            player.rect.x, player.rect.y = 100, 100
            player.vx, player.vy = 0, 0
            player.coin_count = 0
            evil_coins = [EvilCoin(random.randint(50, SCREEN_WIDTH - 50), random.randint(-200, -32)) for _ in range(3)]
            continue

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        keys = pygame.key.get_pressed()
        player.vx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * ACCELERATION

        # Update game objects
        parallax_background.update()
        player.update(platforms)

        for coin in coins:
            coin.update()

        for evil_coin in evil_coins:
            evil_coin.update()

        # Check for coin collisions
        for coin in coins:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                player.coin_count += 1

        # Check for evil coin collisions
        for evil_coin in evil_coins:
            if player.rect.colliderect(evil_coin.rect):
                game_over = True
                break

        # Draw game objects
        parallax_background.draw(screen)
        screen.blit(player.image, player.rect)
        for platform in platforms:
            screen.blit(platform.image, platform.rect)
        for coin in coins:
            screen.blit(coin.image, coin.rect)
        for evil_coin in evil_coins:
            screen.blit(evil_coin.image, evil_coin.rect)

        # Draw the coin counter
        draw_text(screen, f"Max Squat: {player.coin_count} kg.", SCREEN_WIDTH - 250, 10)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()