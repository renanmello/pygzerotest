import pgzrun
import random
from pygame import Rect

# Configurações da tela Principal do jogo
WIDTH = 800
HEIGHT = 600
TITLE = "Zombie Attack"

# Paleta de cores usada no jogo
COLORS = {
    "menu_bg": "#2b2d42",
    "menu_primary": "#8d99ae",
    "menu_secondary": "#ef233c",
    "menu_text": "#edf2f4",
    "level1_bg": "#a8dadc",
    "level1_platform": "#457b9d",
    "level1_accent": "#1d3557",
    "level2_bg": "#f8edeb",
    "level2_platform": "#fec89a",
    "level2_accent": "#ffb5a7",
    "ui_text": "#2b2d42",
    "ui_health": "#e63946",
    "button_normal": "#4cc9f0",
    "button_hover": "#4895ef",
    "button_text": "#ffffff"
}

# Variáveis globais
game_started = False
hero_health = 3
game_over = False
current_level = 1
victory = False
music_on = True
sound_on = True
mouse_pos = (0, 0)  

# Classe para o jogador/player
class Hero:
    def __init__(self, x, y):
        self.run_images = [f"hero_run_{i}" for i in range(1, 5)]
        self.idle_images = [f"hero_idle_{i}" for i in range(1, 3)]
        self.jump_image = "hero_jump"
        
        self.actor = Actor(self.idle_images[0], (x, y))
        self.actor.width = 40
        self.actor.height = 60
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.current_state = "idle"
        self.actor.anchor = ("center", "bottom")
    # A animação idle(parado) e de andar ficaram com bugs
    # a de pular está normal. 
    def update_animation(self):
        self.animation_timer += 1
        
        if keyboard.left:
            self.facing_right = False
        elif keyboard.right:
            self.facing_right = True

        if not self.on_ground:
            if self.current_state != "jumping":
                self.current_state = "jumping"
                self.actor.image = self.jump_image
        elif keyboard.left or keyboard.right:
            if self.current_state != "running":
                self.current_state = "running"
                self.animation_frame = 0
                
            if self.animation_timer % 6 == 0:
                self.animation_frame = (self.animation_frame + 1) % len(self.run_images)
                self.actor.image = self.run_images[self.animation_frame]
        else:
            if self.current_state != "idle":
                self.current_state = "idle"
                self.animation_frame = 0
                
            if self.animation_timer % 10 == 0:
                self.animation_frame = (self.animation_frame + 1) % len(self.idle_images)
                self.actor.image = self.idle_images[self.animation_frame]

        self.actor._flip_x = not self.facing_right

    def update(self):
        if not self.on_ground:
            self.velocity_y += 0.5
            self.y += self.velocity_y

        if self.x < self.width / 2:
            self.x = self.width / 2
        elif self.x > WIDTH - self.width / 2:
            self.x = WIDTH - self.width / 2

        if keyboard.left:
            self.x -= 4
        if keyboard.right:
            self.x += 4

        if (keyboard.up or keyboard.space) and self.on_ground:
            self.velocity_y = -12
            self.on_ground = False
            if sound_on:
                sounds.jump.play()

        self.update_animation()

    def draw(self):
        self.actor.draw()

    @property
    def x(self):
        return self.actor.x

    @x.setter
    def x(self, value):
        self.actor.x = value

    @property
    def y(self):
        return self.actor.y

    @y.setter
    def y(self, value):
        self.actor.y = value

    @property
    def width(self):
        return self.actor.width

    @property
    def height(self):
        return self.actor.height

# Classe para plataformas
class Platform:
    def __init__(self, x, y, width, height, color, accent_color):
        self.rect = Rect(x, y, width, height)
        self.color = color
        self.accent_color = accent_color
        self.width = width
        self.height = height

    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.rect(self.rect, self.accent_color)

# Classe para inimigos
class Enemy:
    def __init__(self, x, y, platform):
        self.walk_images = [f"enemy_walk_{i}" for i in range(1, 3)]
        self.actor = Actor(self.walk_images[0], (x, y))
        self.actor.width = 40
        self.actor.height = 40
        self.platform = platform
        self.speed = random.uniform(1.0, 2.0)
        self.alive = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.actor.anchor = ("center", "bottom")
        self.y = platform.rect.top

    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer % 8 == 0:
            self.animation_frame = (self.animation_frame + 1) % len(self.walk_images)
            self.actor.image = self.walk_images[self.animation_frame]
            self.actor._flip_x = (self.speed < 0)

    def update(self):
        if self.alive:
            self.x += self.speed
            self.y = self.platform.rect.top
            self.update_animation()
            
            if self.x - self.width/2 < self.platform.rect.x:
                self.x = self.platform.rect.x + self.width/2
                self.speed *= -1
            elif self.x + self.width/2 > self.platform.rect.x + self.platform.width:
                self.x = self.platform.rect.x + self.platform.width - self.width/2
                self.speed *= -1

    def draw(self):
        if self.alive:
            self.actor.draw()

    @property
    def x(self):
        return self.actor.x

    @x.setter
    def x(self, value):
        self.actor.x = value

    @property
    def y(self):
        return self.actor.y

    @y.setter
    def y(self, value):
        self.actor.y = value

    @property
    def width(self):
        return self.actor.width

    @property
    def height(self):
        return self.actor.height

# Criação dos níveis
def create_levels():
    global level_1_platforms, level_1_enemies, level_2_platforms, level_2_enemies
    
    level_1_platforms = [
        Platform(0, HEIGHT-20, WIDTH, 20, COLORS["level1_platform"], COLORS["level1_accent"]),
        Platform(150, 450, 200, 20, COLORS["level1_platform"], COLORS["level1_accent"]),
        Platform(500, 350, 200, 20, COLORS["level1_platform"], COLORS["level1_accent"]),
        Platform(250, 250, 180, 20, COLORS["level1_platform"], COLORS["level1_accent"])
    ]
    level_1_enemies = [
        Enemy(level_1_platforms[1].rect.x + 50, level_1_platforms[1].rect.y, level_1_platforms[1]),
        Enemy(level_1_platforms[2].rect.x + 100, level_1_platforms[2].rect.y, level_1_platforms[2]),
        Enemy(level_1_platforms[3].rect.x + 90, level_1_platforms[3].rect.y, level_1_platforms[3])
    ]
    
    level_2_platforms = [
        Platform(0, HEIGHT-20, WIDTH, 20, COLORS["level2_platform"], COLORS["level2_accent"]),
        Platform(100, 450, 250, 20, COLORS["level2_platform"], COLORS["level2_accent"]),
        Platform(550, 350, 250, 20, COLORS["level2_platform"], COLORS["level2_accent"]),
        Platform(300, 250, 200, 20, COLORS["level2_platform"], COLORS["level2_accent"])
    ]
    level_2_enemies = [
        Enemy(level_2_platforms[1].rect.x + 125, level_2_platforms[1].rect.y, level_2_platforms[1]),
        Enemy(level_2_platforms[2].rect.x + 125, level_2_platforms[2].rect.y, level_2_platforms[2]),
        Enemy(level_2_platforms[3].rect.x + 100, level_2_platforms[3].rect.y, level_2_platforms[3])
    ]

create_levels()

# Instâncias iniciais
platforms = level_1_platforms
enemies = level_1_enemies
hero = Hero(100, HEIGHT-80)

# Sistema de colisão
def check_platform_collision():
    hero.on_ground = False
    hero_rect = Rect(hero.x - hero.width/2, hero.y - hero.height, hero.width, hero.height)
    
    for platform in platforms:
        if hero_rect.colliderect(platform.rect):
            if hero_rect.bottom > platform.rect.top and hero.velocity_y >= 0:
                hero.y = platform.rect.top
                hero.velocity_y = 0
                hero.on_ground = True
                hero.current_state = "idle"
            elif hero_rect.right > platform.rect.left and hero_rect.left < platform.rect.left:
                hero.x = platform.rect.left - hero.width/2
            elif hero_rect.left < platform.rect.right and hero_rect.right > platform.rect.right:
                hero.x = platform.rect.right + hero.width/2
    
    if hero.y > HEIGHT + hero.height:
        global hero_health
        hero_health = 0
        check_game_state()

def check_enemy_collision():
    global hero_health
    
    hero_rect = Rect(hero.x - hero.width/2, hero.y - hero.height, hero.width, hero.height)
    
    for enemy in enemies:
        if enemy.alive:
            enemy_rect = Rect(enemy.x - enemy.width/2, enemy.y - enemy.height, enemy.width, enemy.height)
            
            if hero_rect.colliderect(enemy_rect):
                if hero.velocity_y > 0 and hero_rect.bottom <= enemy_rect.top + 10:
                    enemy.alive = False
                    hero.velocity_y = -10
                    if sound_on:
                        sounds.enemy_hit.play()
                else:
                    hero_health -= 1
                    hero.x, hero.y = 100, HEIGHT-80
                    hero.velocity_y = 0
                    hero.on_ground = True
                    if sound_on:
                        sounds.player_hit.play()
    
    check_game_state()

def check_game_state():
    global game_over, current_level, victory, platforms, enemies
    
    if hero_health <= 0:
        game_over = True
        if sound_on:
            sounds.game_over.play()
        return
    
    if all(not enemy.alive for enemy in enemies):
        if current_level == 1:
            current_level = 2
            platforms[:] = level_2_platforms
            enemies[:] = level_2_enemies
            hero.x, hero.y = 100, HEIGHT-80
            hero.velocity_y = 0
            hero.on_ground = True
            if sound_on:
                sounds.level_up.play()
        elif current_level == 2:
            victory = True
            if sound_on:
                sounds.victory.play()

def reset_game():
    global game_started, hero_health, current_level, platforms, enemies, hero, victory, game_over
    hero_health = 3
    current_level = 1
    victory = False
    game_over = False
    create_levels()
    platforms[:] = level_1_platforms
    enemies[:] = level_1_enemies
    hero = Hero(100, HEIGHT-80)
    game_started = False

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        music.play("background")
    else:
        music.stop()

def toggle_sound():
    global sound_on
    sound_on = not sound_on

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def draw_menu():
   
    screen.fill(COLORS["menu_bg"])
    for i in range(HEIGHT):
        alpha = i/HEIGHT
        color = (
            int(43 * (1 - alpha) + 141 * alpha),
            int(45 * (1 - alpha) + 153 * alpha),
            int(66 * (1 - alpha) + 174 * alpha)
        )
        screen.draw.line((0, i), (WIDTH, i), color)
    
    # Título
    screen.draw.text(
        "Zombie Attack",
        center=(WIDTH//2, 100),
        fontsize=72,
        color=COLORS["menu_text"],
        shadow=(1, 1),
        scolor="#000000"
    )
    
    # Botões
    button_y = 200
    button_spacing = 75
    
    # Start Game
    start_hover = (300 <= mouse_pos[0] <= 500 and button_y <= mouse_pos[1] <= button_y + 50)
    screen.draw.filled_rect(
        Rect(300, button_y, 200, 50),
        COLORS["button_hover"] if start_hover else COLORS["button_normal"]
    )
    screen.draw.text(
        "START GAME",
        center=(400, button_y + 25),
        fontsize=30,
        color=COLORS["button_text"]
    )
    
    # Music Toggle
    button_y += button_spacing
    music_hover = (300 <= mouse_pos[0] <= 500 and button_y <= mouse_pos[1] <= button_y + 50)
    screen.draw.filled_rect(
        Rect(300, button_y, 200, 50),
        COLORS["button_hover"] if music_hover else COLORS["button_normal"]
    )
    screen.draw.text(
        "MUSIC: ON" if music_on else "MUSIC: OFF",
        center=(400, button_y + 25),
        fontsize=30,
        color=COLORS["button_text"]
    )
    
    # Sound Toggle
    button_y += button_spacing
    sound_hover = (300 <= mouse_pos[0] <= 500 and button_y <= mouse_pos[1] <= button_y + 50)
    screen.draw.filled_rect(
        Rect(300, button_y, 200, 50),
        COLORS["button_hover"] if sound_hover else COLORS["button_normal"]
    )
    screen.draw.text(
        "SOUND: ON" if sound_on else "SOUND: OFF",
        center=(400, button_y + 25),
        fontsize=30,
        color=COLORS["button_text"]
    )
    
    # Exit
    button_y += button_spacing
    exit_hover = (300 <= mouse_pos[0] <= 500 and button_y <= mouse_pos[1] <= button_y + 50)
    screen.draw.filled_rect(
        Rect(300, button_y, 200, 50),
        COLORS["menu_secondary"] if exit_hover else "#d90429"
    )
    screen.draw.text(
        "EXIT GAME",
        center=(400, button_y + 25),
        fontsize=30,
        color=COLORS["button_text"]
    )

def on_mouse_down(pos):
    global game_started
    
    if not game_started and not game_over and not victory:
        if 300 <= pos[0] <= 500 and 200 <= pos[1] <= 250:
            game_started = True
            if music_on:
                music.play("background")
        elif 300 <= pos[0] <= 500 and 275 <= pos[1] <= 325:
            toggle_music()
        elif 300 <= pos[0] <= 500 and 350 <= pos[1] <= 400:
            toggle_sound()
        elif 300 <= pos[0] <= 500 and 425 <= pos[1] <= 475:
            exit()
    
    elif game_over or victory:
        if 300 <= pos[0] <= 500 and 300 <= pos[1] <= 350:
            reset_game()
        elif 300 <= pos[0] <= 500 and 375 <= pos[1] <= 425:
            exit()

def draw_game():
    # Fundo do nível
    if current_level == 1:
        screen.fill(COLORS["level1_bg"])
        for i in range(0, WIDTH, 50):
            screen.draw.filled_circle((i, HEIGHT-10), 10, COLORS["level1_accent"])
    else:
        screen.fill(COLORS["level2_bg"])
        for i in range(0, WIDTH, 70):
            screen.draw.filled_circle((i, HEIGHT-10), 15, COLORS["level2_accent"])
    
    # Plataformas
    for platform in platforms:
        platform.draw()
    
    # Inimigos
    for enemy in enemies:
        enemy.draw()
    
    # Herói
    hero.draw()
    
    # UI do jogo
    screen.draw.text(
        f"HEALTH: {hero_health}",
        (20, 20),
        fontsize=30,
        color=COLORS["ui_health"],
        bold=True
    )
    screen.draw.text(
        f"LEVEL: {current_level}",
        (20, 50),
        fontsize=30,
        color=COLORS["ui_text"],
        bold=True
    )
    
    # Tela de Game Over
    if game_over:
        screen.draw.filled_rect(
            Rect(WIDTH//2-250, HEIGHT//2-150, 500, 300),
            "#2b2d42aa"
        )
        screen.draw.text(
            "GAME OVER",
            center=(WIDTH//2, HEIGHT//2-100),
            fontsize=60,
            color=COLORS["menu_text"]
        )
        
        # Botão Try Again
        screen.draw.filled_rect(
            Rect(WIDTH//2-100, HEIGHT//2, 200, 50),
            COLORS["button_normal"]
        )
        screen.draw.text(
            "TRY AGAIN",
            center=(WIDTH//2, HEIGHT//2+25),
            fontsize=30,
            color=COLORS["button_text"]
        )
        
        # Botão Quit
        screen.draw.filled_rect(
            Rect(WIDTH//2-100, HEIGHT//2+75, 200, 50),
            COLORS["menu_secondary"]
        )
        screen.draw.text(
            "QUIT",
            center=(WIDTH//2, HEIGHT//2+100),
            fontsize=30,
            color=COLORS["button_text"]
        )
    
    # Tela de Vitória
    if victory:
        screen.draw.filled_rect(
            Rect(WIDTH//2-250, HEIGHT//2-150, 500, 300),
            "#2b2d42aa"
        )
        screen.draw.text(
            "VICTORY!",
            center=(WIDTH//2, HEIGHT//2-100),
            fontsize=60,
            color="#ffd166"
        )
        
        # Botão Play Again
        screen.draw.filled_rect(
            Rect(WIDTH//2-100, HEIGHT//2, 200, 50),
            COLORS["button_normal"]
        )
        screen.draw.text(
            "PLAY AGAIN",
            center=(WIDTH//2, HEIGHT//2+25),
            fontsize=30,
            color=COLORS["button_text"]
        )
        
        # Botão Quit
        screen.draw.filled_rect(
            Rect(WIDTH//2-100, HEIGHT//2+75, 200, 50),
            COLORS["menu_secondary"]
        )
        screen.draw.text(
            "QUIT",
            center=(WIDTH//2, HEIGHT//2+100),
            fontsize=30,
            color=COLORS["button_text"]
        )

def update():
    if game_started and not game_over and not victory:
        hero.update()
        check_platform_collision()
        for enemy in enemies:
            enemy.update()
        check_enemy_collision()

def draw():
    if not game_started and not game_over and not victory:
        draw_menu()
    else:
        draw_game()
#Inicia o jogo
pgzrun.go()