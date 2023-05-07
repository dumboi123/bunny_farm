import pygame
from settings import *
from timer import Timer
class Menu:
    def __init__(self, player, shop_menu):
        self.player = player
        self.shop_menu = shop_menu
        self.display_surf = pygame.display.get_surface()
        self.font = pygame.font.Font('basic_valley/font/LycheeSoda.ttf',30)

        # shop layout
        self.width =400
        self.space = 10
        self.padding =8
        self.options = list(self.player.item_collected.keys())+list(self.player.seed_inven.keys())
        self.border = len(self.player.item_collected) -1
        self.setup()
        # select
        self.index =0
        self.timer = Timer(200, None)

    def setup(self):
        self.text_surfs =[]
        self.total_height =0
        for item in self.options:
            text_surf =self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding*2) 
        self.total_height += (len(self.text_surfs)-1)*self.space
        self.menu_top = SCREEN_HEIGHT/2 - self.total_height/2
        self.main_rect = pygame.Rect(SCREEN_WIDTH/2 - self.width/2, self.menu_top, self.width, self.total_height)
        # Trading
        self.buy_t = self.font.render('Buy', False,'Black')
        self.sell_t = self.font.render('Sell', False,'Black')

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()
        if keys[pygame.K_ESCAPE]:
            self.shop_menu()
        # select
        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -=1
                self.timer.activate()
            if keys[pygame.K_DOWN]:
                self.index +=1
                self.timer.activate()
        # item_trade
            # sell
            if keys[pygame.K_SPACE]:
                self.timer.activate()
                current_item = self.options[self.index]
                if self.index <= self.border:
                    if self.player.item_collected[current_item] >0:
                        self.player.item_collected[current_item] -=1
                        self.player.budget += SALE_PRICES[current_item]
            # buy
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.budget >= seed_price:
                        self.player.seed_inven[current_item] +=1
                        self.player.budget -= PURCHASE_PRICES[current_item]
    # moving 
        if self.index <0:
            self.index = len(self.options)-1
        if self.index > len(self.options)-1:
            self.index =0

    def budget(self):
        text_surf= self.font.render(f'${self.player.budget}', False, 'Black')
        text_rect= text_surf.get_rect(midbottom = (SCREEN_WIDTH/2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.display_surf,'#d59667', text_rect.inflate(10,10),0, 6)
        self.display_surf.blit(text_surf,text_rect)   

    def entry(self, text_surf, amount, pos, select):
        # BG
        bg_rect = pygame.Rect(self.main_rect.left, pos, self.width, text_surf.get_height()+(self.padding*2))
        pygame.draw.rect(self.display_surf, '#d59667', bg_rect,0,4)
        # text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surf.blit(text_surf, text_rect)
        # amount
        a_surf = self.font.render(str(amount), False, 'Black')
        a_rect = a_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surf.blit(a_surf,a_rect)

        if select:
            pygame.draw.rect(self.display_surf,'black', bg_rect, 4, 4)
            if self.index <= self.border:
                pos_rect = self.sell_t.get_rect(midleft = (self.main_rect.left + 150, bg_rect.centery))
                self.display_surf.blit(self.sell_t,pos_rect)
            else:
                pos_rect = self.sell_t.get_rect(midleft = (self.main_rect.left + 150, bg_rect.centery))
                self.display_surf.blit(self.buy_t,pos_rect)
                
    def update(self):
        self.input()
        self.budget()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding*2) + self.space)
            a_list = list(self.player.item_collected.values())+list(self.player.seed_inven.values())
            a = a_list[text_index]

            self.entry(text_surf, a, top, self.index == text_index)
            