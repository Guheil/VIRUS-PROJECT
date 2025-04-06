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
pygame.display.set_caption("CYBERPUNK 2077")

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
    powerup_sound = load_sound('powerup.wav')
    
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
        svg_image = load_svg('cyberpunk_player.svg', 40, 40)
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
        self.shoot_cooldown = 25
        
        # Power-up attributes
        self.active_powerup = None
        self.powerup_timer = 0
        self.powerup_duration = 1200  # 20 seconds at 60 FPS

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
            
        # Handle burst fire continuation if active
        if hasattr(self, 'burst_count') and self.burst_count > 0 and self.active_powerup == "burstfire":
            self.burst_timer += 1
            if self.burst_timer >= 5:  # Fire next burst bullet after 5 frames
                bullet = Bullet(self.rect.centerx, self.rect.centery, 
                              self.burst_target_x, self.burst_target_y, 
                              is_player_bullet=True)
                all_sprites.add(bullet)
                bullets.add(bullet)
                if shoot_sound:
                    shoot_sound.play()
                
                self.burst_count -= 1
                self.burst_timer = 0
    
    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            # Different shooting behavior based on active powerup
            if self.active_powerup == "multishot":
                # Create three bullets at different angles
                angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
                spread = math.pi / 12  # 15 degrees spread
                
                # Left bullet
                left_angle = angle - spread
                left_target_x = self.rect.centerx + math.cos(left_angle) * 100
                left_target_y = self.rect.centery + math.sin(left_angle) * 100
                left_bullet = Bullet(self.rect.centerx, self.rect.centery, left_target_x, left_target_y, is_player_bullet=True)
                all_sprites.add(left_bullet)
                bullets.add(left_bullet)
                
                # Center bullet (straight ahead)
                center_bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, is_player_bullet=True)
                all_sprites.add(center_bullet)
                bullets.add(center_bullet)
                
                # Right bullet
                right_angle = angle + spread
                right_target_x = self.rect.centerx + math.cos(right_angle) * 100
                right_target_y = self.rect.centery + math.sin(right_angle) * 100
                right_bullet = Bullet(self.rect.centerx, self.rect.centery, right_target_x, right_target_y, is_player_bullet=True)
                all_sprites.add(right_bullet)
                bullets.add(right_bullet)
                
                if shoot_sound:
                    shoot_sound.play()
                self.shoot_cooldown = 15  # Slightly longer cooldown for balance
                
            elif self.active_powerup == "burstfire":
                # Create a burst of 3 bullets with a short delay between them
                bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, is_player_bullet=True)
                all_sprites.add(bullet)
                bullets.add(bullet)
                
                # Schedule two more bullets to be fired in quick succession
                self.burst_count = 2
                self.burst_target_x = target_x
                self.burst_target_y = target_y
                self.burst_timer = 0
                
                if shoot_sound:
                    shoot_sound.play()
                self.shoot_cooldown = 25  # Longer cooldown for balance
                
            elif self.active_powerup == "homing":
                # Create a homing bullet that tracks enemies
                bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, 
                              is_player_bullet=True, bullet_type="homing")
                bullet.target_player = False  # Target enemies instead of player
                all_sprites.add(bullet)
                bullets.add(bullet)
                
                if shoot_sound:
                    shoot_sound.play()
                self.shoot_cooldown = 20  # Increased cooldown for balance
                
            else:
                # Normal shooting behavior
                bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, is_player_bullet=True)
                all_sprites.add(bullet)
                bullets.add(bullet)
                
                if shoot_sound:
                    shoot_sound.play()
                self.shoot_cooldown = 20  # Increased standard cooldown

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Try to load SVG, fall back to simple shape if it fails
        svg_image = load_svg('zombie_enemy.svg', 40, 40)  # Cyberpunk zombie enemy
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((30, 30))
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
        svg_image = load_svg('cyber_zombie_boss.svg', 60, 60)  # Bigger cyber zombie boss with guns
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((60, 60))
            self.image.fill(PURPLE)
        self.health = 800  # Increased health
        self.max_health = 800
        self.speed = 1.5
        self.attack_pattern = 0
        self.attack_timer = 0
        self.bullet_spread = 12  # Increased bullet spread
        self.spiral_angle = 0
        self.phase = 1  # Boss phases for difficulty progression
        self.phase_threshold = self.max_health * 0.5  # Phase 2 at 50% health
        
        # Dialogue system variables
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.dialogue_duration = 180  # How long dialogue stays on screen (3 seconds at 60 FPS)
        self.dialogue_color = YELLOW
        self.dialogue_font = pygame.font.Font(None, 28)  # Use default font
        
        # Dialogue lists for different scenarios
        self.taunt_dialogues = [
            "Is that all you've got?",
            "You call that fighting?",
            "I've seen better aim from a blind rat!",
            "Running won't save you!",
            "Your skills are pathetic!"
        ]
        
        self.phase_change_dialogues = [
            "Now you've made me angry!",
            "Prepare for your doom!",
            "No more games!",
            "Time to end this!"
        ]
        
        self.homing_dialogues = [
            "There's nowhere to hide!",
            "My missiles will find you!",
            "You can't escape these!",
            "Heat seekers, locked on target!"
        ]
        
        self.laser_dialogues = [
            "Dodge this if you can!",
            "Burn in my laser grid!",
            "Let's light up the room!",
            "Feel the heat!"
        ]
        
        # Start playing boss music when boss is spawned
        try:
            boss_music_path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', 'boss_music.mp3')
            pygame.mixer.music.load(boss_music_path)
            pygame.mixer.music.set_volume(0.9)  # Set music volume to 80%
            pygame.mixer.music.play(-1)  # Loop indefinitely (-1)
            print("Boss music started")
        except Exception as e:
            print(f"Error playing boss music: {e}")
            
    def show_dialogue(self, dialogue_list):
        # Only set new dialogue if no dialogue is currently showing
        if self.dialogue_timer <= 0:
            self.current_dialogue = random.choice(dialogue_list)
            self.dialogue_timer = self.dialogue_duration

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

        # Update dialogue timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
            
        # Randomly spawn powerups during boss fight (20% chance per second at 60 FPS)
        if random.random() < 0.002:  # Approximately 20% chance per second (0.2/60 ≈ 0.003)
            # Determine what to spawn: power-up or health potion
            spawn_type = random.choice(["powerup", "health"])
            
            # Calculate a random position near the boss
            offset_x = random.randint(-150, 150)
            offset_y = random.randint(-150, 150)
            spawn_x = max(50, min(WIDTH - 50, self.rect.centerx + offset_x))
            spawn_y = max(50, min(HEIGHT - 50, self.rect.centery + offset_y))
            
            if spawn_type == "powerup":
                powerup_type = random.choice(["multishot", "burstfire", "homing"])
                powerup = PowerUp(spawn_x, spawn_y, powerup_type)
                all_sprites.add(powerup)
                powerups.add(powerup)
            else:  # health potion
                health_potion = HealthPotion(spawn_x, spawn_y)
                all_sprites.add(health_potion)
                health_potions.add(health_potion)

        self.attack_timer += 1
        if self.attack_timer >= 90:  # Reduced timer for more frequent attacks
            # Update phase based on health
            if self.health <= self.phase_threshold and self.phase == 1:
                self.phase = 2
                self.speed = 2.0  # Faster in phase 2
                self.bullet_spread = 16  # More bullets in phase 2
                # Show phase change dialogue
                self.show_dialogue(self.phase_change_dialogues)
            
            # Different attack patterns
            if self.attack_pattern == 0:
                # Show random taunt dialogue occasionally
                if random.random() < 0.3:  # 30% chance to taunt
                    self.show_dialogue(self.taunt_dialogues)
                    
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
                    # Show homing missile dialogue
                    self.show_dialogue(self.homing_dialogues)
                    
                    for _ in range(2):  # 2 homing bullets
                        bullet = Bullet(self.rect.centerx, self.rect.centery,
                                      player.rect.centerx, player.rect.centery,
                                      is_player_bullet=False, bullet_type="homing")
                        all_sprites.add(bullet)
                        bullets.add(bullet)
            
            # Add a special laser attack pattern in phase 2
            if self.phase == 2 and self.attack_pattern == 3 and random.random() < 0.7:  # 70% chance in phase 2
                # Show laser attack dialogue
                self.show_dialogue(self.laser_dialogues)
                
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

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        
        # Load the appropriate SVG based on powerup type
        if powerup_type == "multishot":
            svg_image = load_svg('multishot_powerup.svg', 30, 30)
            self.color = (255, 0, 255)  # Purple
        elif powerup_type == "burstfire":
            svg_image = load_svg('burstfire_powerup.svg', 30, 30)
            self.color = (255, 153, 0)  # Orange
        elif powerup_type == "homing":
            svg_image = load_svg('homing_powerup.svg', 30, 30)
            self.color = (0, 255, 0)  # Green
        else:  # Default powerup
            svg_image = load_svg('powerup.svg', 30, 30)
            self.color = (0, 255, 255)  # Cyan
        
        # Use the SVG if loaded, otherwise create a colored circle
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (10, 10), 10)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Add floating animation
        self.float_offset = 0
        self.float_speed = 0.05
        self.original_y = y
        
        # Add lifespan (10 seconds at 60 FPS)
        self.lifespan = 600
        self.life_counter = 0
    
    def update(self):
        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
        self.rect.y = self.original_y + self.float_offset
        
        # Update lifespan
        self.life_counter += 1
        if self.life_counter >= self.lifespan:
            self.kill()

class HealthPotion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the health potion SVG
        svg_image = load_svg('health_potion.svg', 30, 30)
        self.color = (255, 0, 0)  # Red for health
        
        # Use the SVG if loaded, otherwise create a colored circle
        if svg_image:
            self.image = svg_image
        else:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (10, 10), 10)
            # Draw a white cross to indicate health
            pygame.draw.line(self.image, WHITE, (10, 5), (10, 15), 2)
            pygame.draw.line(self.image, WHITE, (5, 10), (15, 10), 2)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Add floating animation
        self.float_offset = 0
        self.float_speed = 0.05
        self.original_y = y
        
        # Add lifespan (10 seconds at 60 FPS)
        self.lifespan = 600
        self.life_counter = 0
        
        # Health restoration amount
        self.heal_amount = 20
    
    def update(self):
        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
        self.rect.y = self.original_y + self.float_offset
        
        # Update lifespan
        self.life_counter += 1
        if self.life_counter >= self.lifespan:
            self.kill()

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
        self.homing_strength = 0.8 if is_player_bullet else 0.5  # Stronger homing for player bullets
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
        if self.bullet_type == "homing":
            if self.target_player:
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
                            self.dx *= 5.5
                            self.dy *= 5.5
            else:
                # Player's homing bullets targeting enemies
                # Find closest enemy
                closest_enemy = None
                closest_dist = float('inf')
                
                for sprite in all_sprites:
                    if isinstance(sprite, Enemy):
                        dx = sprite.rect.centerx - self.rect.centerx
                        dy = sprite.rect.centery - self.rect.centery
                        dist = math.sqrt(dx * dx + dy * dy)
                        
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_enemy = sprite
                
                if closest_enemy and closest_dist > 0:
                    # Calculate direction to closest enemy
                    dx = closest_enemy.rect.centerx - self.rect.centerx
                    dy = closest_enemy.rect.centery - self.rect.centery
                    
                    # Aggressively adjust direction toward enemy with higher homing strength
                    self.dx = self.dx * (1 - self.homing_strength) + (dx / closest_dist) * self.homing_strength
                    self.dy = self.dy * (1 - self.homing_strength) + (dy / closest_dist) * self.homing_strength
                    
                    # Normalize direction vector
                    mag = math.sqrt(self.dx * self.dx + self.dy * self.dy)
                    if mag > 0:
                        self.dx /= mag
                        self.dy /= mag
                        # Make player's homing bullets faster for better gameplay
                        self.dx *= 6.0
                        self.dy *= 6.0
        
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
        # Try to load neon field background SVG
        self.bg_image = load_svg('neon_field_background.svg', WIDTH, HEIGHT)
        
        # Fallback to simple star field if SVG loading fails
        if self.bg_image is None:
            self.bg_image = pygame.Surface((WIDTH, HEIGHT))
            self.bg_image.fill(BLACK)
            for i in range(100):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                pygame.draw.circle(self.bg_image, GRAY, (x, y), 1)
        
        self.y1 = 0
        self.y2 = -HEIGHT

    def update(self):
        self.y1 += 0.4 # Slower scrolling for cyberpunk city
        self.y2 += 0.4
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

# Function to start GCash server and open website
def start_gcash_server():
    import subprocess
    import threading
    import webbrowser
    import time
    import sys
    
    # Get the base path - works for both script and executable
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (executable)
        base_path = os.path.dirname(sys.executable)
    else:
        # If the application is run as a script
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the server.py file
    server_path = os.path.join(base_path, 'gcashweb', 'server.py')
    
    def run_server():
        # Create startupinfo object to hide the console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        # Get the Python executable path
        if getattr(sys, 'frozen', False):
            # If running as executable, use the bundled Python
            python_exe = sys.executable
            # Start the process with hidden window - directly run the server module
            subprocess.Popen([python_exe, '-c', 
                             f"import sys; sys.path.append('{base_path}'); "
                             f"import os; os.chdir('{os.path.join(base_path, 'gcashweb')}'); "
                             f"from gcashweb.server import run_server; run_server()"], 
                            startupinfo=startupinfo)
        else:
            # If running as script, use the system Python
            subprocess.Popen(['python', server_path], 
                            startupinfo=startupinfo)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Thread will exit when main program exits
    server_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(1)
    
    # Open the website in the default browser
    webbrowser.open('http://localhost:8000')
    
    print("GCash server started and website opened.")
    return

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
                         command=lambda: [popup.destroy(), setattr(player, 'popup_shown', True), start_gcash_server()])
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
powerups = pygame.sprite.Group()  # Group for power-ups
health_potions = pygame.sprite.Group()  # Group for health potions
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
    
    # VLC setup with fullscreen flags
    instance = vlc.Instance('--reset-plugins-cache', '--fullscreen', '--no-video-title-show')
    player = instance.media_player_new()
    media = instance.media_new(r"C:\Users\DESKTOP\Desktop\VIRUS-PROJECT\script\assets\vid\win7.mp4")  # Your video path
    player.set_media(media)
    
    # Set fullscreen mode before playing
    player.set_fullscreen(True)
    
    # Play the video
    player.play()
    
    # Ensure video can't be paused
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
    global player, all_sprites, enemies, bullets, powerups, health_potions, enemy_spawn_timer, boss_active, game_state, score
    
    # Clear all sprite groups
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    powerups.empty()
    health_potions.empty()
    
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
        title_text = font_large.render("CYBERPUNK 2077", True, WHITE)
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
        
        # Update player powerup timer
        if player.active_powerup:
            player.powerup_timer += 1
            if player.powerup_timer >= player.powerup_duration:
                player.active_powerup = None
                player.powerup_timer = 0

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
                    # Determine what to drop: power-up, health potion, or nothing
                    drop_roll = random.random()
                    
                    if drop_roll < 0.2:  # 20% chance to spawn a power-up
                        powerup_type = random.choice(["multishot", "burstfire", "homing"])
                        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                        all_sprites.add(powerup)
                        powerups.add(powerup)  # Add to powerups group
                    elif drop_roll < 0.35:  # 15% chance to spawn a health potion
                        health_potion = HealthPotion(enemy.rect.centerx, enemy.rect.centery)
                        all_sprites.add(health_potion)
                        health_potions.add(health_potion)  # Add to health potions group
                    
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
        
        # Player collecting power-ups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            player.active_powerup = powerup.powerup_type
            player.powerup_timer = 0
            
            # Visual feedback for power-up collection
            # Create a flash effect
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill(powerup.color)
            flash.set_alpha(50)  # Semi-transparent
            screen.blit(flash, (0, 0))
            
            # Play power-up sound
            if 'powerup_sound' in globals() and powerup_sound:
                powerup_sound.play()
                
        # Player collecting health potions
        health_potion_hits = pygame.sprite.spritecollide(player, health_potions, True)
        for health_potion in health_potion_hits:
            # Restore player health but don't exceed maximum
            player.health = min(100, player.health + health_potion.heal_amount)
            
            # Visual feedback for health potion collection
            # Create a flash effect
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill(health_potion.color)
            flash.set_alpha(50)  # Semi-transparent
            screen.blit(flash, (0, 0))
            
            # Play power-up sound for health potion too
            if 'powerup_sound' in globals() and powerup_sound:
                powerup_sound.play()
            
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
        pygame.draw.rect(screen, GREEN, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

        # Draw score
        score_text = font_medium.render(f'Score: {player.score}', True, WHITE)
        screen.blit(score_text, (10, 40))
        
        # Draw active power-up status
        if player.active_powerup:
            # Calculate remaining time
            remaining_time = (player.powerup_duration - player.powerup_timer) // 60  # Convert to seconds
            
            # Set color based on power-up type
            if player.active_powerup == "multishot":
                powerup_color = (255, 0, 255)  # Purple
                powerup_name = "Multi-Shot"
            elif player.active_powerup == "burstfire":
                powerup_color = (255, 153, 0)  # Orange
                powerup_name = "Burst Fire"
            elif player.active_powerup == "homing":
                powerup_color = (0, 255, 0)  # Green
                powerup_name = "Homing"
            else:
                powerup_color = WHITE
                powerup_name = "Power-Up"
            
            # Draw power-up status
            powerup_text = font_small.render(f'{powerup_name}: {remaining_time}s', True, powerup_color)
            screen.blit(powerup_text, (10, 70))
        
        # Draw boss dialogue if active
        if boss_active:
            # Find the boss instance
            boss_instance = None
            for enemy in enemies:
                if isinstance(enemy, Boss):
                    boss_instance = enemy
                    break
                    
            if boss_instance and boss_instance.dialogue_timer > 0 and boss_instance.current_dialogue:
                # Create a semi-transparent background for the dialogue
                dialogue_surface = pygame.Surface((WIDTH - 100, 40))
                dialogue_surface.set_alpha(180)  # Semi-transparent
                dialogue_surface.fill(BLACK)
                screen.blit(dialogue_surface, (50, HEIGHT - 100))
                
                # Render the dialogue text
                dialogue_text = boss_instance.dialogue_font.render(boss_instance.current_dialogue, True, boss_instance.dialogue_color)
                dialogue_rect = dialogue_text.get_rect(center=(WIDTH // 2, HEIGHT - 80))
                screen.blit(dialogue_text, dialogue_rect)

    # Update display for all game states
    pygame.display.flip()

root.destroy()
pygame.quit()