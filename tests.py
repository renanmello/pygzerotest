import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 600

def draw():
    pgzrun.screen.fill("black")
    pgzrun.screen.draw.text("Main Menu", (300, 100), fontsize=40, color="white")
    pgzrun.screen.draw.filled_rect(Rect((300, 200), (200, 50)), "blue")
    pgzrun.screen.draw.text("Start Game", (320, 210), fontsize=30, color="white")
    pgzrun.screen.draw.filled_rect(Rect((300, 300), (200, 50)), "green")
    pgzrun.screen.draw.text("Toggle Music", (320, 310), fontsize=30, color="white")
    pgzrun.screen.draw.filled_rect(Rect((300, 400), (200, 50)), "red")
    pgzrun.screen.draw.text("Exit", (350, 410), fontsize=30, color="white")

# Função para lidar com cliques
def on_mouse_down(pos):
    global music_on
    if Rect((300, 200), (200, 50)).collidepoint(pos):
        print("Starting game...")
    elif Rect((300, 300), (200, 50)).collidepoint(pos):
        music_on = not music_on
        if music_on:
            print("Music ON")
        else:
            print("Music OFF")
    elif Rect((300, 400), (200, 50)).collidepoint(pos):
        exit()

# Reproduzir música de fundo
pgzrun.music.play("background_music.mp3")  
pgzrun.music.set_volume(0.5)

# teste animação do herói
class Hero:
    def __init__(self, x, y):
        # Carrega as animações
        self.run_images = [f"hero_run_{i}" for i in range(1, 5)]
        self.idle_images = [f"hero_idle_{i}" for i in range(1, 3)]
        self.jump_image = "hero_jump"
        
        self.actor = Actor(self.idle_images[0], (x, y))
        self.actor.width = 40
        self.actor.height = 60
        self.velocity_y = 0
        self.on_ground = True
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.current_state = "idle"
        self.actor.anchor = ("center", "bottom")

    def update_animation(self):
        self.animation_timer += 1
        
        # Atualiza primeiro a direção
        if keyboard.left:
            self.facing_right = False
        elif keyboard.right:
            self.facing_right = True

        # Lógica de estados de animação
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

        
        if hasattr(self.actor, '_flip_x'):
            self.actor._flip_x = not self.facing_right
        else:
            self.actor.flip_x = not self.facing_right

    def update(self):
        if not self.on_ground:
            self.velocity_y += 0.5
            self.y += self.velocity_y

        # Limites horizontais
        if self.x < self.width / 2:
            self.x = self.width / 2
        elif self.x > WIDTH - self.width / 2:
            self.x = WIDTH - self.width / 2

        # Movimento horizontal
        if keyboard.left:
            self.x -= 4
        if keyboard.right:
            self.x += 4

        # Pulo
        if (keyboard.up or keyboard.space) and self.on_ground:
            self.velocity_y = -12
            self.on_ground = False
            self.current_state = "jumping"
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


# Reproduzir som ao clicar
def play_sound():
    pgzrun.sounds.click.play()  

def on_mouse_down(pos):
    play_sound()

pgzrun.go()