import pygame
from settings import *
from random import randint, choice
from settings import LAYERS
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.2,-self.rect.height*0.75)
        self.z =z

class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames= frames
        self.frame_index = 0

        super().__init__( pos, self.frames[self.frame_index], groups, LAYERS['water'])
    
    def animate(self,dt):
        self.frame_index += 5 *dt
        if self.frame_index >= len(self.frames):
            self.frame_index =0
        self.image = self.frames[int(self.frame_index)]         

    def update(self,dt):
        self.animate(dt)

class Decorations(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20,-self.rect.height*0.9)

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration =200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
    # white sprite
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey('black')
        self.image = new_surf

    def update(self,dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

class Tree(Generic):
    def __init__(self, pos, surf, groups, name, item_add):
        super().__init__(pos, surf, groups)
        # tree inform
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(f'basic_valley/graphics/stumps/{"small" if name == "Small" else "large"}.png').convert_alpha()
        self.invul_timer = Timer(200,None) 
        # fruit
        self.apple_surf = pygame.image.load('basic_valley/graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create()
        # collect
        self.item_add = item_add
        # chopping sound
        self.chop_sound = pygame.mixer.Sound('basic_valley/audio/axe.mp3')

    def damage(self):
        self.health-=1
        self.chop_sound.play()
        if len(self.apple_sprites.sprites()) > 0:
            ran_apple = choice(self.apple_sprites.sprites())
            Particle(ran_apple.rect.topleft, ran_apple.image, self.groups()[0], LAYERS['fruit'])
            self.item_add('apple')
            ran_apple.kill()
    
    def remove_tree(self):
        if self.health <=0:
            Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 320)
            self.item_add('wood')
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive =False
            
    def create(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2 :
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic((x,y), self.apple_surf, [self.apple_sprites, self.groups()[0]], LAYERS['fruit'])    
    
    def update(self,dt):
        if self.alive :
            self.remove_tree()

class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name    
