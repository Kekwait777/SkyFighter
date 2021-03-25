import os
import sys

import pygame
import random
from pygame import mixer

WIDTH = 1200
HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SkyFighter")
clock = pygame.time.Clock()
PAUSED = False
GAME_OVER = False
GAME_STARTED = False
start_ticks = 0

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2 - 180
        self.rect.bottom = HEIGHT - 120
        self.speedx = 0
        self.last_sprite_update = pygame.time.get_ticks()
        self.i = 0
        self.lives = 7
        self.invul = False
        self.start_ticks = 0

    def update(self):
        if self.lives > 0:
            animation(self, player_images, 50, True)
            self.speedx = 0
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_LEFT]:
                self.speedx = -10
            elif keystate[pygame.K_RIGHT]:
                self.speedx = 10
            self.rect.x += self.speedx
            if self.rect.left > 620:
                self.rect.left = 620
            if self.rect.left < 100:
                self.rect.left = 100

            seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000

            if seconds > 0.5:
                self.invul = False
            for bullet in enemy_bullets:
                if is_collided_with(self, bullet):
                    self.start_ticks = pygame.time.get_ticks()
                    sound_mixer.sounds["small_expl_sound"].play(0)
                    if not self.invul:
                        self.take_damage()
                        self.invul = True
                    break
        else:
            self.die()

    def take_damage(self):
        self.lives -= 1

    def die(self):
        sound_mixer.sounds["big_expl_sound" + str(random.randint(1, 2))].play(0)
        animation(self, big_explosion, 30, False)

    def shoot(self):
        bullet = Our_bullet(self.rect.centerx + 20, self.rect.top + 80, -20)
        all_sprites.add(bullet)
        our_bullets.add(bullet)
        sound_mixer.sounds["shoot_sound"].play(0)
        bullet = Our_bullet(self.rect.centerx - 20, self.rect.top + 80, -20)
        all_sprites.add(bullet)
        our_bullets.add(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, attack_speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2 - 180 + x
        self.rect.bottom = HEIGHT - 700
        self.attack_speed = attack_speed
        self.speedy = 1.5
        self.last_sprite_update = pygame.time.get_ticks()
        self.last_shoot_update = pygame.time.get_ticks()
        self.i = 0
        self.is_alive = True

    def update(self):
        now = pygame.time.get_ticks()
        self.rect.y += self.speedy
        if self.is_alive:
            animation(self, enemy_images, 50, True)
            if now - self.last_shoot_update > self.attack_speed:
                self.shoot()
                self.last_shoot_update = now
            if self.rect.bottom > HEIGHT + 200:
                player.lives -= player.lives
                self.is_alive = False
        else:
            animation(self, big_explosion, 30, False)
        for bullet in our_bullets:
            if is_collided_with(self, bullet):
                sound_mixer.sounds["big_expl_sound"+str(random.randint(1,2))].play(0)
                self.die()
                break

    def die(self):
        print("Enemy: ", scores_.scores, 1 + spawner.i)
        scores_.scores += 1 + spawner.i
        self.is_alive = False

    def shoot(self):
        bullet = Enemy_bullet(self.rect.centerx + 20, self.rect.top + 100, 15)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)
        sound_mixer.sounds["shoot_sound"].play(0)
        bullet = Enemy_bullet(self.rect.centerx - 20, self.rect.top + 100, 15)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)


class Our_bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = speed
        self.last_sprite_update = pygame.time.get_ticks()
        self.i = 0
        self.is_alive = True

    def update(self):
        self.rect.y += self.speedy
        if self.is_alive:
            for enemy in enemies:
                if is_collided_with(self, enemy):
                    self.speedy = 0
                    self.is_alive = False
                    break
            if self.rect.bottom < 0:
                self.speedy = 0
                self.is_alive = False
        else:
            our_bullets.remove(self)
            animation(self, small_explosion, 30, False)


class Enemy_bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(pygame.transform.scale(bullet_img, (30, 30)), 180)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = speed
        self.last_sprite_update = pygame.time.get_ticks()
        self.i = 0
        self.is_alive = True

    def update(self):
        self.rect.y += self.speedy
        if self.is_alive:
            if is_collided_with(self, player):
                if player.lives > 0:
                    self.speedy = 0
                    self.is_alive = False
            if self.rect.bottom > HEIGHT:
                self.speedy = 0
                self.is_alive = False
        else:
            enemy_bullets.remove(self)
            animation(self, small_explosion, 30, False)


class Lives_panel(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = live_image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2 - 400
        self.rect.bottom = HEIGHT - 50

    def update(self):
        for live in range(player.lives):
            self.rect.centerx = WIDTH / 2 - 400 + 73 * live
            screen.blit(self.image, self.rect)
            self.rect.centerx = 0


class Scores:
    def __init__(self):
        self.scores = 0

    def update(self):
        print_text("SCORES: " + str(self.scores), 25, WHITE, 150, 100)


class Main_screen:
    def __init__(self):
        self.image = main_screen_images[0]
        self.rect = self.image.get_rect()
        self.rect.x += 70
        self.last_sprite_update = pygame.time.get_ticks()
        self.i = 0
        self.in_main_screen = True

    def update(self):
        if self.in_main_screen:
            animation(self,main_screen_images, 50, True)


class TV:
    def __init__(self):
        self.image = tv[0]
        self.rect = self.image.get_rect()
        self.last_sprite_update = pygame.time.get_ticks()
        self.i = 0
        self.idle = False
        self.off_animation = False
        self.on_animation = True

    def update(self):
        if self.on_animation:
            #print(self.idle, self.on_animation, self.off_animation)
            on = animation(self, tv_onoff_images, 30, False)
            if not on is None:
                self.on_animation = on
                self.idle = not self.on_animation
        elif self.idle:
            #print(self.idle, self.on_animation, self.off_animation)
            animation(self, tv, 200, True)
        if self.off_animation:
            #print(self.idle, self.on_animation, self.off_animation)
            off = animation(self, tv_onoff_images[::-1], 30, False)
            if not off is None:
                self.off_animation = off
                self.image = tv_onoff_images[0]
                pygame.quit()

    def TV_game_start(self):
        main_screen.in_main_screen = False
        self.on_animation = True
        self.idle = False
        self.off_animation = False

    def TV_back_to_main(self):
        main_screen.in_main_screen = True
        self.on_animation = True
        self.idle = False
        self.off_animation = False

    def TV_on(self):
        self.on_animation = True
        self.idle = False
        self.off_animation = False

    def TV_off(self):
        self.on_animation = False
        self.idle = False
        self.off_animation = True



class Button:
    def __init__(self, x, y, func1, func2):
        self.image = button_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.on = True
        self.func1 = func1
        self.func2 = func2

    def click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.left < mouse_x < self.rect.left + self.rect.width and self.rect.top < mouse_y < self.rect.top + self.rect.height:
            sound_mixer.sounds["tv_sound_buttons"].play(0)
            self.on = not self.on
            if not self.on:
                if not self.func1 == 0:
                    self.func1()
            if self.on:
                if not self.func2 == 0:
                    self.func2()

    def update(self):
        screen.blit(self.image, self.rect)
        if not self.on:
            self.image = button_images[1]
        else:
            self.image = button_images[0]


class Sound_button:
    def __init__(self, x, y, image, dest):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dest = dest

    def click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.left < mouse_x < self.rect.left + self.rect.width and self.rect.top < mouse_y < self.rect.top + self.rect.height:
            sound_mixer.sounds["tv_sound_buttons"].play(0)
            if self.dest == "+":
                sound_mixer.volume += 0.01
            if self.dest == "-":
                sound_mixer.volume -= 0.01

    def update(self):
        screen.blit(self.image, self.rect)


class Spawner:
    def __init__(self):
        self.speed = 1400
        self.last_update = pygame.time.get_ticks()
        self.difficulty = 1
        self.i = 0

    def update(self):
        now = pygame.time.get_ticks()
        attack_speed = random.randint(1000, 1500)
        if now - self.last_update > self.speed - self.difficulty:
            self.last_update = now
            enemy = Enemy(random.randint(-200, 200), attack_speed - self.difficulty / 2)
            enemies.add(enemy)
            all_sprites.add(enemy)
            self.i += 1
            self.difficulty += self.difficulty / self.i

    def get_i(self):
        return self.i

class Sound_mixer():
    def __init__(self):
        self.volume = 0.1
        self.sounds = {"background_music": self.load_sound("background_music"),
                       "shoot_sound": self.load_sound("shoot_sound"),
                       "tv_sound_buttons": self.load_sound("tv_sound_buttons"),
                       "small_expl_sound": self.load_sound("small_expl_sound"),
                       "big_expl_sound1": self.load_sound("big_expl_sound1"),
                       "big_expl_sound2": self.load_sound("big_expl_sound2"),
                       "game_over_sound": self.load_sound("game_over_sound")}

    def load_sound(self, name):
        path = resource_path(os.path.join("venv\\Sounds\\", name + ".wav"))
        return pygame.mixer.Sound(path)

    def update(self):
        mixer.music.set_volume(self.volume)
        for sound in self.sounds.keys():
            self.sounds[sound].set_volume(self.volume)

def animation(Entity, images, speed, endless):
    now = pygame.time.get_ticks()
    is_alive = True
    if now - Entity.last_sprite_update > speed:
        Entity.i += 1
        if Entity.i > len(images) - 1:
            if endless:
                Entity.i = 0
            else:
                Entity.i = 0
                try:
                    Entity.kill()
                except Exception:
                    pass
                is_alive = False
                return is_alive
        if is_alive:
            Entity.last_sprite_update = now
            new_image = images[Entity.i]
            Entity.image = new_image


def is_collided_with(self, sprite):
    return self.rect.colliderect(sprite.rect)


def load_images(name, count, scale):
    array = []
    if scale == 0:
        for i in range(count):
            try:
                array.append(pygame.image.load(resource_path(os.path.join("venv\\Sprites\\", str(name) + str(i + 1) + ".png"))).convert_alpha())
            except Warning:
                print(Warning)
    else:
        for i in range(count):
            try:
                array.append(pygame.transform.scale(
                    pygame.image.load(resource_path(os.path.join("venv\\Sprites\\", str(name) + str(i + 1) + ".png"))).convert_alpha(), (scale, scale)))
            except Warning:
                print(Warning)

    return array


def print_text(text, size, color, x, y):
    font = pygame.font.Font(resource_path(os.path.join("venv\\Fonts\\","MinecraftFont.ttf")), size)
    screen.blit(font.render(text, True, color), (x, y))


player_images = load_images("our_plane", 3, 120)
enemy_images = load_images("enemy_plane", 3, 120)
small_explosion = load_images("small_explosion", 9, 50)
big_explosion = load_images("big_explosion", 9, 120)
button_images = load_images("button_pos", 2, 110)
button_sound_images = load_images("button_sound", 2, 120)
main_screen_images = load_images("main_screen", 38, 0)
live_image = pygame.image.load(resource_path(os.path.join("venv\\Sprites\\", "our_plane_lives.png"))).convert_alpha()
live_image.set_alpha(200)
tv = load_images("TV_", 3, 0)
tv_onoff_images = load_images("TV_onoff", 11, 0)
bullet_img = pygame.image.load(resource_path(os.path.join("venv\\Sprites\\","bullet.png"))).convert_alpha()
background = main_screen_images[0]
background_rect = background.get_rect()
background_rect.x += 100

all_sprites = pygame.sprite.Group()
our_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
sound_mixer = Sound_mixer()
player = Player()
spawner = Spawner()
scores_ = Scores()
lives_panel = Lives_panel()
Tv = TV()
main_screen = Main_screen()
start_button = Button(945, 100, Tv.TV_game_start, Tv.TV_back_to_main)
exit_button = Button(945, 250, Tv.TV_off, Tv.TV_on)
sound_up_button = Sound_button(818, 95, button_sound_images[0], "+")
sound_down_button = Sound_button(818, 205, button_sound_images[1], "-")

mixer.music.load(resource_path(os.path.join("venv\\Sounds\\","bg_music.mp3")))
mixer.music.set_volume(0.2)
mixer.music.play(-1)

running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        sound_mixer.update()

        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.constants.MOUSEBUTTONDOWN:
            start_button.click()
            exit_button.click()
            sound_up_button.click()
            sound_down_button.click()
        elif event.type == pygame.KEYDOWN and not main_screen.in_main_screen:
            if event.key == pygame.K_SPACE and player.lives > 0 and not PAUSED:
                player.shoot()
            if event.key == pygame.K_ESCAPE and not GAME_OVER:
                PAUSED = not PAUSED
    if not main_screen.in_main_screen:
        if not GAME_STARTED:
            Tv.on_animation = True
            all_sprites = pygame.sprite.Group()
            our_bullets = pygame.sprite.Group()
            enemy_bullets = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            player = Player()
            spawner = Spawner()
            lives_panel = Lives_panel()
            all_sprites.add(player)
            GAME_STARTED = True

        if player.lives < 1 and GAME_OVER == False:
            GAME_OVER = True
            sound_mixer.sounds["game_over_sound"].play(0)
            start_ticks = pygame.time.get_ticks()
        screen.blit(background, background_rect)
        if not PAUSED:
            spawner.update()
            all_sprites.update()

        all_sprites.draw(screen)
        lives_panel.update()
        screen.blit(lives_panel.image, lives_panel.rect)
        scores_.update()

        if PAUSED:
            print_text("PAUSE", 50, WHITE, 500, 80)
        elif not PAUSED and GAME_OVER:
            print_text("GAME OVER", 50, WHITE, 250, 300)
            seconds = (pygame.time.get_ticks() - start_ticks) / 1000
            if seconds > 3:
                start_button.on = True
                GAME_STARTED = False
                Tv.on_animation = True
                main_screen.in_main_screen = True
                GAME_OVER = False

    if main_screen.in_main_screen:
        main_screen.update()
        screen.blit(main_screen.image, main_screen.rect)
        GAME_STARTED = False
        GAME_OVER = False

    Tv.update()
    screen.blit(Tv.image, Tv.rect)
    print_text(str(int(clock.get_fps())), 10, WHITE, 5,5)
    start_button.update()
    exit_button.update()
    sound_up_button.update()
    sound_down_button.update()
    pygame.display.flip()
sys.exit()
