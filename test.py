import pygame,sys,time

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()

t_rect = pygame.Rect(0,310,100,100)
t_pos =t_rect.x
speed = 200

p_time= time.time()

while True:
    # lấy khoảng giá trị giữa các frame
    # dt = time.time() - p_time
    # p_time=time.time()
    # equally
    
    dt =clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    
    t_pos += speed*dt
    t_rect.x = round(t_pos)
    pygame.draw.rect(screen,'red',t_rect)
    pygame.display.update()