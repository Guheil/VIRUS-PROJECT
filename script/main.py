import pygame
import math
import random
import os
import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Button, Label
import vlc
import time
import io
import cairosvg  # You'll need to install this: pip install cairosvg

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the sound mixer

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

# Load sounds
def load_sound(filename):
    sound_path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', filename)
    try:
        sound = pygame.mixer.Sound(sound_path)
        return sound
    except pygame.error:
        print(f"Could not load sound {filename}")
        return None

# Try to load sounds, but don't crash if files are missing
try:
    # Initialize pygame mixer with higher buffer size to avoid audio issues
    pygame.mixer.quit()  # Quit any existing mixer
    pygame.mixer.init(44100, -16, 2, 2048)  # Higher buffer size (2048)
    
    # Use consistent path format without './' prefix
    shoot_sound = load_sound('laser.wav')
    if shoot_sound:
        # Lower the volume of the laser sound to 0.3 (30% of original volume)
        shoot_sound.set_volume(0.3)
    
    enemy_death_sound = load_sound('explosion.wav')
    boss_hit_sound = load_sound('boss_hit.wav')
    boss_shoot_sound = load_sound('boss_shoot.wav')
    player_hit_sound = load_sound('player_hit.wav')
    
    # Load boss music using pygame.mixer.music for streaming audio
    boss_music_path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', 'boss_music.wav')
    
    # Print success message if sounds loaded
    if shoot_sound:
        print("Sound files loaded successfully")
except Exception as e:
    print(f"Sound loading error: {e}")
    print("Some sound files could not be loaded. Game will run without sound.")
    shoot_sound = enemy_death_sound = boss_hit_sound = boss_shoot_sound = player_hit_sound = None

# Function to load SVG images
def load_svg(filename, width, height):
    try:
        svg_path = os.path.join(os.path.dirname(__file__), 'assets', 'img', filename)
        if os.path.exists(svg_path):
            with open(svg_path, 'rb') as svg_file:
                svg_data = svg_file.read()
                png_data = cairosvg.svg2png(bytestring=svg_data, output_width=width, output_height=height)
                return pygame.image.load(io.BytesIO(png_data))
        else:
            print(f"SVG file {filename} not found")
            return None
    except Exception as e:
        print(f"Error loading SVG {filename}: {e}")
        return None

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Try to load SVG, fall back to simple shape if it fails
        svg_image = load_svg('player.svg', 40, 40)
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.score = 0
        self.popup_shown = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.shoot_cooldown = 0

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
        
        # Handle invulnerability after being hit
        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer > 60:  # 1 second of invulnerability
                self.invulnerable = False
                self.invulnerable_timer = 0
        
        # Handle shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, is_player_bullet=True)
            all_sprites.add(bullet)
            bullets.add(bullet)
            if shoot_sound:
                shoot_sound.play()
            self.shoot_cooldown = 10  # Cooldown between shots

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Try to load SVG, fall back to simple shape if it fails
        svg_image = load_svg('enemy.svg', 40, 40)  # Increased from 30x30
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((30, 30))  # Increased from 20x20
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn_enemy()
        self.speed = 2
        self.health = 20
        self.max_health = 20
        self.shoot_timer = random.randint(120, 240)  # Random initial timer

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
        
        # Normalize the direction vector and move the enemy toward the player
        if dist > 0:
            dx = dx / dist
            dy = dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
        # Update shoot timer
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(120, 240)  # Reset timer

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
        # Try to load SVG, fall back to simple shape if it fails
        svg_image = load_svg('boss.svg', 50, 50)
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(PURPLE)
        self.health = 300  # Increased health
        self.max_health = 300
        self.speed = 1.5
        self.attack_pattern = 0
        self.attack_timer = 0
        self.bullet_spread = 12  # Increased bullet spread
        self.spiral_angle = 0
        self.phase = 1  # Boss phases for difficulty progression
        self.phase_threshold = self.max_health * 0.5  # Phase 2 at 50% health
        
        # Start playing boss music when boss is spawned
        try:
            boss_music_path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', 'boss_music.mp3')
            pygame.mixer.music.load(boss_music_path)
            pygame.mixer.music.set_volume(0.9)  # Set music volume to 80%
            pygame.mixer.music.play(-1)  # Loop indefinitely (-1)
            print("Boss music started")
        except Exception as e:
            print(f"Error playing boss music: {e}")

    def update(self):
        player = pygame.sprite.Group.sprites(all_sprites)[0]
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        
        # Move towards player (fixed boss movement)
        if dist > 200:  # Only move if not too close to player
            dx = dx / dist
            dy = dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        self.attack_timer += 1
        if self.attack_timer >= 90:  # Reduced timer for more frequent attacks
            # Update phase based on health
            if self.health <= self.phase_threshold and self.phase == 1:
                self.phase = 2
                self.speed = 2.0  # Faster in phase 2
                self.bullet_spread = 16  # More bullets in phase 2
            
            # Different attack patterns
            if self.attack_pattern == 0:
                # Circular bullet pattern
                for i in range(self.bullet_spread):
                    angle = (2 * math.pi * i) / self.bullet_spread
                    bullet_dx = math.cos(angle) * WIDTH
                    bullet_dy = math.sin(angle) * HEIGHT
                    bullet = Bullet(self.rect.centerx, self.rect.centery,
                                  self.rect.centerx + bullet_dx,
                                  self.rect.centery + bullet_dy,
                                  is_player_bullet=False)
                    bullet.image.fill(YELLOW)
                    bullet.speed = 5 + (self.phase * 1.5)  # Faster in phase 2
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                if boss_shoot_sound:
                    boss_shoot_sound.play()
            
            elif self.attack_pattern == 1:
                # Spiral pattern
                for i in range(5):  # 5 bullets in spiral
                    angle = self.spiral_angle + (2 * math.pi * i) / 5
                    bullet_dx = math.cos(angle) * WIDTH
                    bullet_dy = math.sin(angle) * HEIGHT
                    bullet = Bullet(self.rect.centerx, self.rect.centery,
                                  self.rect.centerx + bullet_dx,
                                  self.rect.centery + bullet_dy,
                                  is_player_bullet=False)
                    bullet.image.fill(YELLOW)
                    bullet.speed = 6
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                self.spiral_angle += 0.3  # Rotate spiral pattern
                if boss_shoot_sound:
                    boss_shoot_sound.play()
            
            elif self.attack_pattern == 2:
                # Laser beam attack - straight lines in 4 or 8 directions
                directions = 8 if self.phase == 2 else 4
                for i in range(directions):
                    angle = (2 * math.pi * i) / directions
                    bullet_dx = math.cos(angle) * WIDTH
                    bullet_dy = math.sin(angle) * HEIGHT
                    # Create 3 bullets in a line to simulate a laser beam
                    for j in range(3):
                        distance = (j + 1) * 20
                        bullet = Bullet(self.rect.centerx + math.cos(angle) * distance,
                                      self.rect.centery + math.sin(angle) * distance,
                                      self.rect.centerx + bullet_dx,
                                      self.rect.centery + bullet_dy,
                                      is_player_bullet=False)
                        bullet.image.fill(RED)  # Red for laser beams
                        bullet.speed = 10  # Fast laser beams
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                if boss_shoot_sound:
                    boss_shoot_sound.play()
            
            elif self.attack_pattern == 3:
                # Direct shots at player - more dangerous!
                shots = 5 if self.phase == 2 else 3
                for _ in range(shots):  # Multiple shots directly at player
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-30, 30)
                    bullet = Bullet(self.rect.centerx, self.rect.centery,
                                  player.rect.centerx + offset_x, 
                                  player.rect.centery + offset_y,
                                  is_player_bullet=False)
                    bullet.image.fill(YELLOW)
                    bullet.speed = 8 + self.phase  # Faster in phase 2
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                if boss_shoot_sound:
                    boss_shoot_sound.play()
            
            # In phase 2, add a bullet hell pattern
            if self.phase == 2 and random.random() < 0.3:  # 30% chance for extra attack
                # Random bullet spray
                for _ in range(8):
                    angle = random.uniform(0, 2 * math.pi)
                    bullet_dx = math.cos(angle) * WIDTH
                    bullet_dy = math.sin(angle) * HEIGHT
                    bullet = Bullet(self.rect.centerx, self.rect.centery,
                                  self.rect.centerx + bullet_dx,
                                  self.rect.centery + bullet_dy,
                                  is_player_bullet=False)
                    bullet.image.fill(PURPLE)
                    bullet.speed = random.uniform(3, 7)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                
                # Add homing bullets in phase 2
                if random.random() < 0.5:  # 50% chance for homing bullets
                    for _ in range(2):  # 2 homing bullets
                        bullet = Bullet(self.rect.centerx, self.rect.centery,
                                      player.rect.centerx, player.rect.centery,
                                      is_player_bullet=False, bullet_type="homing")
                        all_sprites.add(bullet)
                        bullets.add(bullet)
            
            # Add a special laser attack pattern in phase 2
            if self.phase == 2 and self.attack_pattern == 3 and random.random() < 0.7:  # 70% chance in phase 2
                # Create a cross-shaped laser pattern
                for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
                    for distance in range(1, 5):  # Multiple bullets to form a laser beam
                        offset = distance * 15
                        start_x = self.rect.centerx + math.cos(angle) * offset
                        start_y = self.rect.centery + math.sin(angle) * offset
                        target_x = self.rect.centerx + math.cos(angle) * WIDTH
                        target_y = self.rect.centery + math.sin(angle) * HEIGHT
                        
                        bullet = Bullet(start_x, start_y, target_x, target_y, 
                                      is_player_bullet=False, bullet_type="laser")
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                if boss_shoot_sound:
                    boss_shoot_sound.play()
            
            # Cycle through attack patterns
            self.attack_pattern = (self.attack_pattern + 1) % 4  # Now 4 patterns
            self.attack_timer = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, is_player_bullet=True, bullet_type="normal"):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(WHITE if is_player_bullet else YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10 if is_player_bullet else 7
        self.is_player_bullet = is_player_bullet
        self.bullet_type = bullet_type
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        self.dx = self.speed * dx / dist if dist != 0 else 0
        self.dy = self.speed * dy / dist if dist != 0 else 0
        
        # Add a trail effect
        self.trail_timer = 0
        self.trail_colors = [WHITE, YELLOW, RED] if is_player_bullet else [YELLOW, RED, PURPLE]
        
        # For homing bullets
        self.homing_strength = 0.05
        self.target_player = not is_player_bullet
        
        # Add lifespan for homing bullets (4 seconds at 60 FPS)
        self.lifespan = 240 if bullet_type == "homing" else -1
        self.life_counter = 0

    def update(self):
        # Check lifespan for homing bullets
        if self.lifespan > 0:
            self.life_counter += 1
            if self.life_counter >= self.lifespan:
                self.kill()
                return
                
        # Special behavior for homing bullets
        if self.bullet_type == "homing" and self.target_player:
            # Find player
            player = None
            for sprite in all_sprites:
                if isinstance(sprite, Player):
                    player = sprite
                    break
                    
            if player:
                # Calculate direction to player
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    # Gradually adjust direction toward player
                    self.dx = self.dx * (1 - self.homing_strength) + (dx / dist) * self.homing_strength
                    self.dy = self.dy * (1 - self.homing_strength) + (dy / dist) * self.homing_strength
                    
                    # Normalize direction vector
                    mag = math.sqrt(self.dx * self.dx + self.dy * self.dy)
                    if mag > 0:
                        self.dx /= mag
                        self.dy /= mag
                        # Make homing bullets faster but still dodgeable
                        self.dx *= 1.5
                        self.dy *= 1.5
        
        self.rect.x += self.dx
        self.rect.y += self.dy
        if not screen.get_rect().colliderect(self.rect):
            self.kill()
            
        # Create trail effect
        self.trail_timer += 1
        if self.trail_timer >= 3:
            self.trail_timer = 0
            trail = pygame.Surface((4, 4))
            trail_color = random.choice(self.trail_colors)
            trail.fill(trail_color)
            trail_rect = trail.get_rect()
            trail_rect.center = self.rect.center
            # We would add this to a trail group if we had one

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

# Tkinter root (hidden) - Moved above game initialization as requested
root = tk.Tk()
root.withdraw()

# Function to show popup ads
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

# Game state variables
game_state = "start_menu"  # Can be "start_menu", "playing", or "game_over"
score = 0

# Initialize background for menu screens
background = Background()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
background = Background()

# Create player (will be initialized when game starts)
player = None

# Game loop setup
clock = pygame.time.Clock()
enemy_spawn_timer = 0
boss_spawn_score = 200
boss_active = False

# Function to play full-screen unpausable video with VLC
def play_video():
    messagebox.showinfo("Demotion", "BAD NOW I AM DEMOTING YOU TO WINDOWS 7")
    
    # Minimize Pygame window to avoid overlap
    pygame.display.iconify()
    
    # VLC setup with reset plugins cache and fullscreen
    instance = vlc.Instance('--reset-plugins-cache', '--fullscreen', '--no-video-title-show')
    player = instance.media_player_new()
    media = instance.media_new(r"C:\Users\DESKTOP\Desktop\VIRUS-PROJECT\script\assets\vid\win7.mp4")  # Your video path
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

# Create player bullet group and enemy bullet group
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Font setup
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Function to initialize/reset the game
def init_game():
    global player, all_sprites, enemies, bullets, enemy_spawn_timer, boss_active, game_state, score
    
    # Clear all sprite groups
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Reset game variables
    enemy_spawn_timer = 0
    boss_active = False
    score = 0
    game_state = "playing"

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Start menu button click
                if game_state == "start_menu":
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        init_game()
                # Game over button click
                elif game_state == "game_over":
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        init_game()
                # Player shooting in game
                elif game_state == "playing":
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    player.shoot(mouse_x, mouse_y)
    
    # Start Menu State
    if game_state == "start_menu":
        screen.fill(BLACK)
        background.update()
        background.draw(screen)
        
        # Title
        title_text = font_large.render("TOP DOWN SHOOTER", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(title_text, title_rect)
        
        # Instructions
        instr1 = font_small.render("WASD to move, Mouse to aim and shoot", True, WHITE)
        instr1_rect = instr1.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
        screen.blit(instr1, instr1_rect)
        
        instr2 = font_small.render("Defeat enemies and survive as long as possible!", True, WHITE)
        instr2_rect = instr2.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(instr2, instr2_rect)
        
        # Start button
        button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(screen, GREEN, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        
        start_text = font_medium.render("START", True, BLACK)
        start_text_rect = start_text.get_rect(center=button_rect.center)
        screen.blit(start_text, start_text_rect)
    
    # Game Over State
    elif game_state == "game_over":
        screen.fill(BLACK)
        background.update()
        background.draw(screen)
        
        # Game Over text
        gameover_text = font_large.render("GAME OVER", True, RED)
        gameover_rect = gameover_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(gameover_text, gameover_rect)
        
        # Final score
        score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
        screen.blit(score_text, score_rect)
        
        # Restart button
        button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(screen, GREEN, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        
        restart_text = font_medium.render("RESTART", True, BLACK)
        restart_text_rect = restart_text.get_rect(center=button_rect.center)
        screen.blit(restart_text, restart_text_rect)
    
    # Playing State
    elif game_state == "playing":
        # Show popup ad at score 100
        if player.score >= 100 and not player.popup_shown:
            show_popup()

        # Spawn enemies
        if not boss_active:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= 60:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = 0

            # Spawn boss at score threshold
            if player.score >= boss_spawn_score and not boss_active:
                boss = Boss()
                all_sprites.add(boss)
                enemies.add(boss)
                boss_active = True

        # Update all game objects
        all_sprites.update()

        # Sort bullets into player and enemy groups
        for bullet in bullets:
            if bullet.is_player_bullet:
                player_bullets.add(bullet)
            else:
                enemy_bullets.add(bullet)
        
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy, bullet_list in hits.items():
            if isinstance(enemy, Boss):
                enemy.health -= 5
                if boss_hit_sound:
                    boss_hit_sound.play()
                if enemy.health <= 0:
                    enemy.kill()
                    boss_active = False
                    player.score += 100
                    score = player.score  # Update global score for game over screen
                    boss_spawn_score += 500
                    # Stop boss music when boss is defeated
                    pygame.mixer.music.stop()
                    if enemy_death_sound:
                        enemy_death_sound.play()
            else:
                enemy.health -= 10
                if enemy.health <= 0:
                    enemy.kill()
                    player.score += 10
                    score = player.score  # Update global score for game over screen
                    if enemy_death_sound:
                        enemy_death_sound.play()

        # Enemy bullets hitting player
        if not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            if hits:
                player.health -= 5 * len(hits)
                player.invulnerable = True
                if player_hit_sound:
                    player_hit_sound.play()
                if player.health <= 0:
                    score = player.score  # Save final score for game over screen
                    game_state = "game_over"  # Change to game over state
                    # Stop boss music if it's playing
                    pygame.mixer.music.stop()
        
        # Enemies colliding with player
        if not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            if hits:
                player.health -= 10
                player.invulnerable = True
                if player_hit_sound:
                    player_hit_sound.play()
                if player.health <= 0:
                    score = player.score  # Save final score for game over screen
                    game_state = "game_over"  # Change to game over state
                    # Stop boss music if it's playing
                    pygame.mixer.music.stop()

        # Draw game elements
        screen.fill(BLACK)
        background.update()
        background.draw(screen)
        all_sprites.draw(screen)

        for enemy in enemies:
            enemy.draw_health_bar(screen)

        # Draw player health bar
        health_ratio = player.health / 100
        bar_width = 200
        bar_height = 20
        fill_width = bar_width * health_ratio
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill_width, bar_height)
        pygame.draw.rect(screen, RED, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

        # Draw score
        score_text = font_medium.render(f'Score: {player.score}', True, WHITE)
        screen.blit(score_text, (10, 40))

    # Update display for all game states
    pygame.display.flip()

root.destroy()
pygame.quit()