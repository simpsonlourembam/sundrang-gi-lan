import pygame
import sys
import random
import math
from pygame import mixer
import os

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Sundrang-gi-lan")
clock = pygame.time.Clock()

# Touch controls
class TouchControls:
    def __init__(self):
        self.joystick_center = (100, SCREEN_HEIGHT - 100)
        self.joystick_radius = 50
        self.joystick_pos = self.joystick_center
        self.joystick_active = False
        self.shoot_button_rect = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100, 80, 80)
        self.pause_button_rect = pygame.Rect(SCREEN_WIDTH - 50, 20, 30, 30)

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            x, y = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
            if self.is_in_joystick_area(x, y):
                self.joystick_active = True
                self.joystick_pos = (x, y)
            elif self.shoot_button_rect.collidepoint(x, y):
                return "shoot"
            elif self.pause_button_rect.collidepoint(x, y):
                return "pause"
        elif event.type == pygame.FINGERUP:
            if self.joystick_active:
                self.joystick_active = False
                self.joystick_pos = self.joystick_center
        elif event.type == pygame.FINGERMOTION and self.joystick_active:
            x, y = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
            self.joystick_pos = self.clamp_joystick(x, y)
        return None

    def is_in_joystick_area(self, x, y):
        return math.sqrt((x - self.joystick_center[0])**2 + (y - self.joystick_center[1])**2) <= self.joystick_radius

    def clamp_joystick(self, x, y):
        dx = x - self.joystick_center[0]
        dy = y - self.joystick_center[1]
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.joystick_radius:
            dx = dx * self.joystick_radius / distance
            dy = dy * self.joystick_radius / distance
        return (self.joystick_center[0] + dx, self.joystick_center[1] + dy)

    def get_movement(self):
        if not self.joystick_active:
            return (0, 0)
        dx = self.joystick_pos[0] - self.joystick_center[0]
        dy = self.joystick_pos[1] - self.joystick_center[1]
        return (dx / self.joystick_radius, dy / self.joystick_radius)

    def draw(self, surface):
        # Draw joystick background
        pygame.draw.circle(surface, (100, 100, 100), self.joystick_center, self.joystick_radius)
        # Draw joystick handle
        pygame.draw.circle(surface, (150, 150, 150), self.joystick_pos, 20)
        # Draw shoot button
        pygame.draw.circle(surface, RED, self.shoot_button_rect.center, 40)
        # Draw pause button
        pygame.draw.rect(surface, WHITE, self.pause_button_rect)

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.lifetime = random.randint(20, 40)
        self.alpha = 255

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 40) * 255)
        self.image.set_alpha(self.alpha)
        if self.lifetime <= 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.powerup_time = 0
        self.powerup_type = None
        self.shield = 0

    def update(self, touch_controls=None):
        if touch_controls:
            dx, dy = touch_controls.get_movement()
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.rect.y += self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

        # Update powerup timer
        if self.powerup_time > 0:
            self.powerup_time -= 1
            if self.powerup_time <= 0:
                self.powerup_type = None

        # Create engine particles
        if random.random() < 0.3:
            particle = Particle(self.rect.centerx, self.rect.bottom, BLUE)
            all_sprites.add(particle)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.powerup_type == "double":
                bullet1 = Bullet(self.rect.left + 10, self.rect.top)
                bullet2 = Bullet(self.rect.right - 10, self.rect.top)
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)
        self.health = 2

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 25:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 2
        self.type = random.choice(["double", "shield"])

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create enemies
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game variables
score = 0
game_over = False
paused = False
powerup_spawn_timer = 0

# Initialize touch controls
touch_controls = TouchControls()

# Game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)

    # Process input/events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_SPACE and not game_over:
                player.shoot()
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            action = touch_controls.handle_event(event)
            if action == "shoot" and not game_over:
                player.shoot()
            elif action == "pause":
                paused = not paused

    if not paused and not game_over:
        # Update
        player.update(touch_controls)
        all_sprites.update()

        # Spawn powerups
        powerup_spawn_timer += 1
        if powerup_spawn_timer >= 300:  # Spawn powerup every 5 seconds
            powerup_spawn_timer = 0
            if random.random() < 0.3:  # 30% chance to spawn
                powerup = PowerUp()
                all_sprites.add(powerup)
                powerups.add(powerup)

        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.health -= len(bullet_list)
            if enemy.health <= 0:
                score += 10
                # Create explosion particles
                for _ in range(10):
                    particle = Particle(enemy.rect.centerx, enemy.rect.centery, RED)
                    all_sprites.add(particle)
                enemy.kill()
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

        # Check for powerup collisions
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            player.powerup_type = hit.type
            player.powerup_time = 300  # 5 seconds
            if hit.type == "shield":
                player.shield = 50

        # Check for player-enemy collisions
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            if player.shield > 0:
                player.shield -= 20
            else:
                player.health -= 20
            # Create collision particles
            for _ in range(5):
                particle = Particle(hit.rect.centerx, hit.rect.centery, YELLOW)
                all_sprites.add(particle)
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            if player.health <= 0:
                game_over = True

    # Draw / render
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw touch controls
    touch_controls.draw(screen)

    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw health bar
    health_text = font.render(f'Health: {player.health}', True, WHITE)
    screen.blit(health_text, (10, 50))

    # Draw shield
    if player.shield > 0:
        shield_text = font.render(f'Shield: {player.shield}', True, BLUE)
        screen.blit(shield_text, (10, 90))

    # Draw powerup status
    if player.powerup_type:
        powerup_text = font.render(f'PowerUp: {player.powerup_type}', True, GREEN)
        screen.blit(powerup_text, (10, 130))

    if game_over:
        game_over_text = font.render('GAME OVER', True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))

    if paused:
        pause_text = font.render('PAUSED', True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))

    # Flip the display
    pygame.display.flip()

pygame.quit()
sys.exit() 