import pygame,sys
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Stardew valley')   
        self.screen = pygame.display.set_mode((1280,720))
        self.clock =pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            dt = self.clock.tick()/1000
            self.level.run(dt)
            pygame.display.update()

if __name__ == '__main__':
    game =Game()
    game.run()
