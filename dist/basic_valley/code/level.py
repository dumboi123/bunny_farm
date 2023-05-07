import pygame
from settings import*
from support import*
from player import Player
from overlay import Overlay
from sprites import Generic, Water, Decorations, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from transition import Transition
from random import randint
from soil import SoilLayer
from sky import Rain, Sky
from shop import Menu
class Level:
    def __init__(self):
        self.display_surf = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        # change screen
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()
        # shop
        self.shop_active = False
        self.menu = Menu(self.player, self.run_shop)
        # addition
        self.clock =pygame.time.Clock()
        self.rainny_day = [120,120,120]
        self.sunny_day = [255,255,255]
        self.delta = self.clock.tick()/1000
        # sound
        self.collect_sound = pygame.mixer.Sound('basic_valley/audio/success.wav')
        self.collect_sound.set_volume(0.3)
        self.bg_music = pygame.mixer.Sound('basic_valley/audio/2-01 Twinleaf Town (Night).mp3')
        self.bg_music.set_volume(0.3)
        self.bg_music.play(loops=-1)
        

    def setup(self):
        tmx_data=load_pygame('basic_valley/data/map.tmx')
        # house
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x *TILE_SIZE, y*TILE_SIZE),surf, self.all_sprites, LAYERS['house bottom'])       
        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x *TILE_SIZE, y*TILE_SIZE),surf, self.all_sprites)
        # fence
        for x,y,surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x *TILE_SIZE, y*TILE_SIZE),surf, [self.all_sprites, self.collision_sprites])
        # water
        water_frames = import_fold('basic_valley/graphics/water')
        for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x *TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)
        # decorations
        for ob in tmx_data.get_layer_by_name('Decoration'):
            Decorations((ob.x, ob.y),ob.image,[self.all_sprites, self.collision_sprites])
        # Tree
        for ob in tmx_data.get_layer_by_name('Trees'):
            Tree((ob.x, ob.y), ob.image,[self.all_sprites, self.collision_sprites, self.tree_sprites], ob.name, self.item_add)
        # other collisions
        for x,y,surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x *TILE_SIZE, y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
        # Player
        for ob in tmx_data.get_layer_by_name('Player'):
            if ob.name =='Start':
                self.player = Player((ob.x, ob.y), self.all_sprites, self.collision_sprites, self.tree_sprites, self.interaction_sprites, self.soil_layer, run_shop = self.run_shop)
            if ob.name =='Bed':
                Interaction((ob.x, ob.y), (ob.width, ob.height), self.interaction_sprites, ob.name)
            if ob.name =='Trader':
                Interaction((ob.x, ob.y), (ob.width, ob.height), self.interaction_sprites, ob.name)

        Generic((0,0), pygame.image.load('basic_valley/graphics/world/ground.png').convert_alpha(),self.all_sprites, LAYERS['ground'])

    def item_add(self, item):
        self.player.item_collected[item] +=1
        self.collect_sound.play()

    def plants_harvest(self):
        if self.soil_layer.plant_sprites:
            for p in self.soil_layer.plant_sprites.sprites():
                if p.harvest and p.rect.colliderect(self.player.hitbox):
                    self.item_add(p.plant)
                    p.kill()
                    Particle(p.rect.topleft, p.image, self.all_sprites, LAYERS['main'])
                    self.soil_layer.grid[p.rect.centery//TILE_SIZE][p.rect.centerx//TILE_SIZE].remove('P')

    def run_shop(self):
        self.shop_active = not self.shop_active

    def run(self,dt):
        self.display_surf.fill('black')
        self.all_sprites.custom_draw(self.player)
        #shop
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plants_harvest()

        self.overlay.display()
        # weather
        if self.raining:
            self.rain.update()
            self.sky.display(dt,self.rainny_day)
        else: 
            self.sky.display(dt,self.sunny_day)
        # screen change
        if self.player.sleep:
            self.transition.play()     
     
    def reset(self):
        # new day
        self.bg_music.stop()
        # self.bg_music_ranny.stop()
        # if self.raining: self.bg_music_ranny.play(loops =-1)
        self.bg_music.play(loops =-1)

        self.sunny_day =[255,255,255]
        self.rainny_day= [120,120,120]       
        self.sky.display(self.delta, self.sunny_day)
        # plants
        self.soil_layer.update_plants()
        # tree
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create()
        # water
        self.soil_layer.water_remove()
        # random rain
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.watering_all()

            
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
    
    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)