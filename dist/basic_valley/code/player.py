import pygame
from settings import*
from support import *
from timer import Timer
class Player(pygame.sprite.Sprite):

    def __init__(self, pos, group, collision, tree_sprite, interaction, soil_layer, run_shop):
        super().__init__(group)
        self.import_assets()
        self.status ='down_idle'
        self.frame_index = 0
        # gene_setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)       
        self.z = LAYERS['main']
        # sound
        self.watering =  pygame.mixer.Sound('basic_valley/audio/water.mp3')
        self.watering.set_volume(0.1)
        # movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed =200 
        # collide
        self.hitbox = self.rect.copy().inflate((-125,-70))
        self.collison = collision
        # interact
        self.tree_sprite = tree_sprite
        self.interaction = interaction
        self.sleep =False
        self.soil_layer = soil_layer
        self.run_shop = run_shop
        # use time
        self.timers = {
            'tool use': Timer(350,self.use_tool),
            'tool switch': Timer(200,self.passed),
            'seed use': Timer(350,self.use_seed),
            'seed switch': Timer(300,self.passed)
        }
        # collecting
        self.item_collected = {
            'wood':10,
            'apple':20,
            'corn':7,
            'tomato':5
        }
        # tools 
        self.tools=['axe','hoe','water']
        self.tool_index=0
        self.selected_tool = self.tools[self.tool_index]
        # seeds
        self.seeds=['corn','tomato']
        self.seed_index =0
        self.selected_seed = self.seeds[self.seed_index]
        # inventory
        self.seed_inven = {'corn': 5, 'tomato': 5 }
        self.budget = 200

    def target_pos(self):
        self.target = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def passed(self):
        pass
    def use_tool(self):
        if self.selected_tool == 'hoe': 
            self.soil_layer.get_hit(self.target)
        if self.selected_tool == 'axe': 
            for tree in self.tree_sprite.sprites():
                if tree.rect.collidepoint(self.target):
                    tree.damage()
        if self.selected_tool == 'water':
            self.watering.play() 
            self.soil_layer.water(self.target)
    def use_seed(self):
        if self.seed_inven[self.selected_seed] >0:
            self.soil_layer.planting_seed(self.target, self.selected_seed)
            self.seed_inven[self.selected_seed] -=1
    
    def import_assets(self):
        self.animations = { 'up':[],'down':[],'left':[],'right':[],
                            'up_idle':[],'down_idle':[],'left_idle':[],'right_idle':[],
                            'up_axe':[],'down_axe':[],'left_axe':[],'right_axe':[],
                            'up_water':[],'down_water':[],'left_water':[],'right_water':[],
                            'up_hoe':[],'down_hoe':[],'left_hoe':[],'right_hoe':[]}
        for animation in self.animations.keys():
            full_path = 'basic_valley/graphics/character/' + animation
            self.animations[animation] = import_fold(full_path)

    def animate(self,dt):
        self.frame_index += 5 *dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index =0
        self.image = self.animations[self.status][int(self.frame_index)] 

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] +'_idle'

        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def input(self):
        keys = pygame.key.get_pressed()
    # directions
        if not self.timers['tool use'].active and not self.sleep:
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y=0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status= 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status= 'left'
            else:
                self.direction.x=0
    # tools
        # selected tool
            if keys[pygame.K_z] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index+=1
                self.tool_index = self.tool_index if self.tool_index <len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]
        # tools use
            if keys[pygame.K_c]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index =0
    # seeds
        # selected seed
            if keys[pygame.K_x] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index+=1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]
        # seeds use
            if keys[pygame.K_v]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index =0
    # interact
            if keys[pygame.K_SPACE]:
                collide_interact = pygame.sprite.spritecollide(self, self.interaction, False)
                if collide_interact:
                    if collide_interact[0].name =='Trader': 
                        self.run_shop()
                    else: 
                        self.status = 'left_idle'
                        self.sleep =True

    def collide(self,direct):
        for sprite in self.collison.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):

                    if direct == 'hori':
                        # right
                        if self.direction.x >0: 
                            self.hitbox.right = sprite.hitbox.left
                        # left
                        if self.direction.x <0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direct == 'ver':
                        # up
                        if self.direction.y <0:
                            self.hitbox.top = sprite.hitbox.bottom
                        # down
                        if self.direction.y >0:
                            self.hitbox.bottom = sprite.hitbox.top
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self,dt):
    # normalize speed
        if self.direction.magnitude() >0:
            self.direction = self.direction.normalize()
    # horizon move
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx =  self.hitbox.centerx
        self.collide('hori')
    # ver move
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collide('ver')

    def update_timer(self):
        for timer in self.timers.values():
            timer.update()

    def update(self,dt):
        self.input()
        self.get_status()
        self.update_timer()
        self.target_pos()

        self.move(dt)
        self.animate(dt)