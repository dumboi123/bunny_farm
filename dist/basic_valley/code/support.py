from os import walk
import pygame
def import_fold(path):
    sur_list =[]
    for _,__,img_fold in walk(path):
        for image in img_fold:
            full_path= path +'/' +image
            image_surf = pygame.image.load(full_path).convert_alpha()
            sur_list.append(image_surf)
    return sur_list

def import_fold_dict(path):
    surf_dict = {}
    for _,__,img_fold in walk(path):
        for image in img_fold:
            full_path= path +'/' +image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surf_dict[image.split('.')[0]]=image_surf
    return surf_dict