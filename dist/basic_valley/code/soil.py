import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice
class SoilLayer:
    def __init__(self, all_sprites, collide_sprites):
        # gene_setup
        self.all_sprites = all_sprites
        self.collide_sprites = collide_sprites
        self.soil_sprites =  pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        # graphics
        self.soil_surfs = import_fold_dict('basic_valley/graphics/soil/')
        self.water_surfs = import_fold('basic_valley/graphics/soil_water') 
        # sound
        self.hoe_sound =pygame.mixer.Sound('basic_valley/audio/hoe.wav')
        self.hoe_sound.set_volume(0.2)   
        self.plant_sound =pygame.mixer.Sound('basic_valley/audio/plant.wav')
        self.plant_sound.set_volume(0.2)
        # create
        self.create_soild_grid()
        self.create_hit()

    def create_soild_grid(self):
        ground =pygame.image.load('basic_valley/graphics/world/ground.png')
        hori_tiles =ground.get_width() // TILE_SIZE
        ver_tiles =ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(hori_tiles)] for row in range(ver_tiles)]
        for x, y, _ in load_pygame('basic_valley/data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
    
    def create_hit(self):
        self.hit_rects =[]
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'F' in cell:
                    x, y = col_index*TILE_SIZE, row_index*TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)
    
    def get_hit(self, point):
        
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()
                x, y = rect.x //TILE_SIZE, rect.y //TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.watering_all()
    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell:
                    # the around graphics
                    top= 'X' in self.grid[row_index-1][col_index]
                    bot= 'X' in self.grid[row_index+1][col_index]
                    right= 'X' in row[col_index +1]
                    left= 'X' in row[col_index -1]
                    # original type
                    soil_type= 'o'
                    # center
                    if all((top, bot, right, left)): soil_type = 'x'
                    # hori types
                    if left and not any((top, right, bot)): soil_type ='r'
                    if right and not any((top, left, bot)): soil_type ='l'
                    if left and right and not any((top, bot)): soil_type ='lr'
                    # ver types
                    if top and not any ((right, left, bot)): soil_type ='b'
                    if bot and not any ((right, left, top)): soil_type ='t'
                    if top and bot and not any ((right, left)): soil_type ='tb'
                    # corners
                    if left and bot and not any ((top, right)): soil_type = 'tr'
                    if right and top and not any((bot, left)) : soil_type = 'bl'
                    if left and top and not any ((bot, right)): soil_type = 'br'
                    if right and bot and not any((top, left)) : soil_type = 'tl'
                    # last aspect
                    if all((top, bot, right)) and not left: soil_type = 'tbr'
                    if all((top, bot, left)) and not right: soil_type = 'tbl'
                    if all((top, left, right)) and not bot: soil_type = 'lrb'
                    if all((left, bot, right)) and not top: soil_type = 'lrt'

                    SoilTile((col_index*TILE_SIZE, row_index*TILE_SIZE), self.soil_surfs[soil_type],[self.all_sprites, self.soil_sprites])
    
    def water(self, target):
        for soil in self.soil_sprites.sprites():
            if soil.rect.collidepoint(target):
                x, y = soil.rect.x // TILE_SIZE, soil.rect.y //TILE_SIZE
                self.grid[y][x].append('W')
                pos =soil.rect.topleft
                surf =choice(self.water_surfs)
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites] )

    def water_remove(self):
        for s in self.water_sprites.sprites():
            s.kill()        
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def watering_all(self):
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    WaterTile((col_index*TILE_SIZE,row_index*TILE_SIZE),choice(self.water_surfs),  [self.all_sprites, self.water_sprites] )

    def planting_seed(self, target, seed):
        for s_sprite in self.soil_sprites.sprites():
            if s_sprite.rect.collidepoint(target):
                self.plant_sound.play()
                x, y = s_sprite.rect.x // TILE_SIZE, s_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed,[self.all_sprites ,self.plant_sprites, self.collide_sprites], s_sprite, self.check_water)

    def check_water(self, pos):
        x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        watered = 'W' in cell
        return watered
    
    def update_plants(self):
        for p in self.plant_sprites.sprites():
            p.growing()
            
class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant, groups, soil, check_water):
        super().__init__(groups)
        # setup
        self.plant = plant
        self.frames = import_fold(f'basic_valley/graphics/fruit/{plant}')
        self.soil = soil
        self.check_water = check_water
        # growing
        self.time_grow = 0
        self.max_grow = len(self.frames)-1
        self.speed_grow = GROW_SPEED[plant]
        self.harvest = False
        # adding sprite
        self.image = self.frames[self.time_grow]
        self.y_offset = -16 if plant == 'corn' else -8
        self.rect = self.image.get_rect(midbottom =soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
        self.z = LAYERS['ground plant']
    
    def growing(self):
        if self.check_water(self.rect.center):
            self.time_grow += self.speed_grow

            if int(self.time_grow) >0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height*0.4)

            if self.time_grow >= self.max_grow:
                self.time_grow = self.max_grow
                self.harvest =True

            self.image = self.frames[int(self.time_grow)]
            self.rect = self.image.get_rect(midbottom =self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))