import math, random, pgzrun
from pygame import Rect

WIDTH, HEIGHT, TITLE = 800, 600, "Shadow Knight Adventure"
MENU, PLAYING, GAME_OVER, VICTORY = "menu", "playing", "game_over", "victory"
PLATFORMS = [Rect(0, 560, 800, 40), Rect(500, 420, 150, 20), Rect(350, 320, 150, 20),
             Rect(600, 220, 150, 20), Rect(200, 150, 250, 20)]

current_state, music_enabled = MENU, True
game_objects, player = [], None

class Entity:
    def __init__(self, pos, idle_r, idle_l, walk_r, walk_l):
        self.actor = Actor(idle_r[0], pos)
        self.idle_r, self.idle_l = idle_r, idle_l
        self.walk_r, self.walk_l = walk_r, walk_l
        self.current, self.idx, self.timer = idle_r, 0, 0
        self.facing = "right"

    def animate(self, moving):
        if self.facing == "right": f = self.walk_r if moving else self.idle_r
        else: f = self.walk_l if moving else self.idle_l
        if self.current != f: self.current, self.idx, self.timer = f, 0, 0
        self.timer += 1
        if self.timer >= 10:
            self.timer, self.idx = 0, (self.idx + 1) % len(self.current)
        self.actor.image = self.current[self.idx]
    def draw(self): self.actor.draw()

class Player(Entity):
    def __init__(self, x, y):
        super().__init__((x, y), ['hero_idle_1'], ['hero_idle_left'], 
                         ['hero_run_1'], ['hero_run_left'])
        self.vx = self.vy = 0
        self.ground = False
    def update(self):
        self.vx = 0
        if keyboard.left: self.vx, self.facing = -5, "left"
        elif keyboard.right: self.vx, self.facing = 5, "right"
        if (keyboard.up or keyboard.space) and self.ground:
            self.vy, self.ground = -13, False
            play_sfx('sfx_jump_09')
        self.vy += 0.6
        self.actor.x += self.vx
        self.actor.y += self.vy
        self.actor.left = max(0, min(self.actor.left, WIDTH - self.actor.width))
        self.ground = False
        for p in PLATFORMS:
            if self.actor.colliderect(p) and self.vy > 0 and self.actor.bottom <= p.top + 15:
                self.actor.bottom, self.vy, self.ground = p.top, 0, True
        self.animate(self.vx != 0)

class Enemy(Entity):
    def __init__(self, x, y, r):
        super().__init__((x, y), ['enemy_walk_1', 'enemy_walk_2'], ['enemy_walk_1left', 'enemy_walk_2left'], 
                         ['enemy_walk_1', 'enemy_walk_2'], ['enemy_walk_1left', 'enemy_walk_2left'])
        self.start_x, self.range, self.dir = x, r, 1
    def update(self):
        self.actor.x += 2 * self.dir
        self.facing = "right" if self.dir > 0 else "left"
        if abs(self.actor.x - self.start_x) > self.range: self.dir *= -1
        self.animate(True)

def play_sfx(n):
    if music_enabled:
        try: getattr(sounds, n).play()
        except: pass

def init_game():
    global player, game_objects, current_state
    player, game_objects, current_state = Player(50, 500), [Enemy(400, 544, 150), Enemy(580, 404, 60), Enemy(320, 134, 100)], PLAYING
    if music_enabled:
        try: music.play('background_music')
        except: pass

def draw():
    screen.fill((30, 30, 45))
    if current_state == MENU:
        draw_txt(TITLE, 60, -150)
        draw_btn("START GAME", 250, "darkgreen")
        draw_btn("SOUND: " + ("ON" if music_enabled else "OFF"), 330, "steelblue")
        draw_btn("EXIT", 410, "darkred")
    elif current_state == PLAYING:
        try: screen.blit('background', (0,0))
        except: pass
        for p in PLATFORMS: screen.draw.filled_rect(p, (100, 70, 40))
        player.draw()
        for o in game_objects: o.draw()
        screen.draw.filled_circle((350, 130), 10, "gold")
    else:
        msg = "VICTORY!" if current_state == VICTORY else "GAME OVER"
        draw_txt(msg, 80, 0, "gold" if current_state == VICTORY else "red")
        draw_txt("Click to Restart", 30, 60)

def draw_txt(t, s, y, c="white"):
    screen.draw.text(t, center=(WIDTH//2, HEIGHT//2+y), fontsize=s, color=c, shadow=(1,1))

def draw_btn(t, y, c):
    r = Rect(WIDTH//2-110, y-25, 220, 50)
    screen.draw.filled_rect(r, c); screen.draw.text(t, center=r.center, fontsize=30)

def update():
    global current_state
    if current_state == PLAYING:
        player.update()
        for o in game_objects:
            o.update()
            hb = Rect(0, 0, 20, 20); hb.center = o.actor.center
            if player.actor.colliderect(hb): current_state = GAME_OVER
        if player.actor.colliderect(Rect(340, 120, 20, 20)): current_state = VICTORY

def on_mouse_down(pos):
    global current_state, music_enabled
    if current_state == MENU:
        if Rect(290, 225, 220, 50).collidepoint(pos): init_game()
        elif Rect(290, 305, 220, 50).collidepoint(pos):
            music_enabled = not music_enabled
            if not music_enabled: music.stop()
            else:
                try: music.play('background_music')
                except: pass
        elif Rect(290, 385, 220, 50).collidepoint(pos): exit()
    elif current_state in (GAME_OVER, VICTORY): current_state = MENU

if music_enabled:
    try: music.play('background_music')
    except: pass

pgzrun.go()
