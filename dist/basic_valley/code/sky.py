import pygame
from settings import *
from settings import LAYERS
from support import import_fold
from sprites import Generic
from random import randint, choice

class Drop(Generic):
    def __init__(self, pos, surf, movement, groups, z):
        # setup
        super().__init__(pos, surf, groups, z)  
        self.life =randint(400,500)
        self.start = pygame.time.get_ticks()
        # movement
        self.movement = movement
        if self.movement:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(200,250)

    def update(self, dt):
        # movement
        if self.movement:
            self.pos += self.direction*self.speed*dt
            self.rect.topleft = (round(self.pos.x),round(self.pos.y))
        # exist_time
        if pygame.time.get_ticks() - self.start >= self.life:
            self.kill()

class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_fold('basic_valley/graphics/rain/drops/')
        self.rain_floors = import_fold('basic_valley/graphics/rain/floor/')
        self.floor_w, self.floor_h = pygame.image.load('basic_valley/graphics/world/ground.png').get_size()

    def floor_create(self):
        surf = choice(self.rain_floors)
        pos = (randint(0, self.floor_w),randint(0, self.floor_h))
        movement = False
        groups = self.all_sprites
        z = LAYERS['rain floor']
        Drop(pos, surf, movement, groups, z)

    def drops_create(self):
        surf = choice(self.rain_drops)
        pos = (randint(0, self.floor_w),randint(0, self.floor_h))
        movement = True
        groups = self.all_sprites
        z = LAYERS['rain drops']    
        Drop(pos, surf, movement, groups, z)
    
    def update(self):
        self.floor_create()
        self.drops_create()

class Sky:
    def __init__(self):
        self.display_surf = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.day_color = []
        self.night_color = [43, 62, 80]

    def display(self, dt, color=[]):
        if not color:
            self.day_color = [255,255,255]
        else: self.day_color=color
        
        for index, value in enumerate(self.night_color):
            if self.day_color[index] > value:
                self.day_color[index] -= 2*dt
        self.full_surf.fill(self.day_color)
        self.display_surf.blit(self.full_surf, (0,0), special_flags= pygame.BLEND_RGB_MULT)