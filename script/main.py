import pygame
import math
import random
import os
import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Button, Label
import vlc
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Shooter")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.score = 0
        self.popup_shown = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn_enemy()
        self.speed = 2
        self.health = 20
        self.max_health = 20

    def spawn_enemy(self):
        side = random.randint(1, 4)
        if side == 1:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -20
        elif side == 2:
            self.rect.x = WIDTH + 20
            self.rect.y = random.randint(0, HEIGHT)
        elif side == 3:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + 20
        else:
            self.rect.x = -20
            self.rect.y = random.randint(0, HEIGHT)

    def update(self):
        player = pygame.sprite.Group.sprites(all_sprites)[0]
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.rect.x += self.speed * dx / dist
            self.rect.y += self.speed * dy / dist

    def draw_health_bar(self, surface):
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.rect.width
            bar_height = 5
            fill_width = bar_width * health_ratio
            outline_rect = pygame.Rect(self.rect.x, self.rect.y - 8, bar_width, bar_height)
            fill_rect = pygame.Rect(self.rect.x, self.rect.y - 8, fill_width, bar_height)
            pygame.draw.rect(surface, RED, fill_rect)
            pygame.draw.rect(surface, WHITE, outline_rect, 1)

class Boss(Enemy):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(PURPLE)
        self.health = 200
        self.max_health = 200
        self.speed = 1.5
        self.attack_pattern = 0
        self.attack_timer = 0
        self.bullet_spread = 8

    def update(self):
        player = pygame.sprite.Group.sprites(all_sprites)[0]
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            self.rect.x += self.speed * dx / dist
            self.rect.y += self.speed * dy / dist

        self.attack_timer += 1
        if self.attack_timer >= 120:
            if self.attack_pattern == 0:
                for i in range(self.bullet_spread):
                    angle = (2 * math.pi * i) / self.bullet_spread
                    bullet_dx = math.cos(angle) * WIDTH
                    bullet_dy = math.sin(angle) * HEIGHT
                    bullet = Bullet(self.rect.centerx, self.rect.centery,
                                  self.rect.centerx + bullet_dx,
                                  self.rect.centery + bullet_dy)
                    bullet.image.fill(YELLOW)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            else:
                # Direct shot at player
                bullet = Bullet(self.rect.centerx, self.rect.centery,
                              player.rect.centerx, player.rect.centery)
                bullet.image.fill(YELLOW)
                all_sprites.add(bullet)
                bullets.add(bullet)
            self.attack_pattern = (self.attack_pattern + 1) % 2
            self.attack_timer = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        self.dx = self.speed * dx / dist if dist != 0 else 0
        self.dy = self.speed * dy / dist if dist != 0 else 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Background:
    def __init__(self):
        self.bg_image = pygame.Surface((WIDTH, HEIGHT))
        for i in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(self.bg_image, GRAY, (x, y), 1)
        self.y1 = 0
        self.y2 = -HEIGHT

    def update(self):
        self.y1 += 1
        self.y2 += 1
        if self.y1 > HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 > HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, surface):
        surface.blit(self.bg_image, (0, self.y1))
        surface.blit(self.bg_image, (0, self.y2))

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
background = Background()

# Create player
player = Player()
all_sprites.add(player)

# Game loop setup
running = True
clock = pygame.time.Clock()
enemy_spawn_timer = 0
boss_spawn_score = 200
boss_active = False

# Tkinter root (hidden)
root = tk.Tk()
root.withdraw()

# Function to play full-screen unpausable video with VLC
def play_video():
    messagebox.showinfo("Demotion", "BAD NOW I AM DEMOTING YOU TO WINDOWS 7")
    
    # Minimize Pygame window to avoid overlap
    pygame.display.iconify()
    
    # VLC setup with reset plugins cache and fullscreen
    instance = vlc.Instance('--reset-plugins-cache', '--fullscreen', '--no-video-title-show')
    player = instance.media_player_new()
    media = instance.media_new("./assets/vid/win7.mp4")  # Your video path
    player.set_media(media)
    player.play()
    
    # Ensure fullscreen and disable pausing
    time.sleep(0.5)  # Small delay to let VLC initialize
    player.set_fullscreen(True)
    player.set_pause(0)
    
    video_running = True
    while video_running:
        for event in pygame.event.get():  # Use Pygame to detect 'q' key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                video_running = False
                player.stop()
        clock.tick(FPS)
    
    # Restore Pygame window
    pygame.display.set_mode((WIDTH, HEIGHT))

def show_popup():
    popup = Toplevel()
    popup.title("Claim Your Prize")
    
    # Center the popup
    popup_width = 300
    popup_height = 150
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width // 2) - (popup_width // 2)
    y = (screen_height // 2) - (popup_height // 2)
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    # Make the popup modal
    popup.grab_set()
    popup.protocol("WM_DELETE_WINDOW", lambda: [popup.destroy(), play_video()])

    Label(popup, text="You've won 500,000 pesos from GCash!").pack(pady=10)
    Label(popup, text="Type 'claim' to activate the button:").pack()

    entry = Entry(popup)
    entry.pack(pady=5)

    claim_button = Button(popup, text="Yes, Claim", state="disabled", 
                         command=lambda: [popup.destroy(), setattr(player, 'popup_shown', True)])
    claim_button.pack(pady=10)

    def check_input(event):
        if entry.get().lower() == "claim":
            claim_button.config(state="normal")
        else:
            claim_button.config(state="disabled")

    entry.bind("<KeyRelease>", check_input)
    popup.wait_window()

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y)
                all_sprites.add(bullet)
                bullets.add(bullet)

    if player.score >= 100 and not player.popup_shown:
        show_popup()

    if not boss_active:
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        if player.score >= boss_spawn_score and not boss_active:
            boss = Boss()
            all_sprites.add(boss)
            enemies.add(boss)
            boss_active = True

    all_sprites.update()

    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in hits.items():
        if isinstance(enemy, Boss):
            enemy.health -= 5
            if enemy.health <= 0:
                enemy.kill()
                boss_active = False
                player.score += 100
                boss_spawn_score += 500
        else:
            enemy.health -= 10
            if enemy.health <= 0:
                enemy.kill()
                player.score += 10

    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 10
        if player.health <= 0:
            running = False

    screen.fill(BLACK)
    background.update()
    background.draw(screen)
    all_sprites.draw(screen)

    for enemy in enemies:
        enemy.draw_health_bar(screen)

    health_ratio = player.health / 100
    bar_width = 200
    bar_height = 20
    fill_width = bar_width * health_ratio
    outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
    fill_rect = pygame.Rect(10, 10, fill_width, bar_height)
    pygame.draw.rect(screen, RED, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {player.score}', True, WHITE)
    screen.blit(score_text, (10, 40))

    pygame.display.flip()

root.destroy()
pygame.quit()