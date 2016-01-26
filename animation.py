

import pygame
from pygame.locals import *
import sys



class Animation:
    def __init__(self, strip, width, cycle=1):
        self.cycle = cycle
        height = strip.get_size()[1]
        self.images = []
        print(strip.get_size()[0]//width)
        print(width*10)
        for i in range(0, strip.get_size()[0]//width):
            image = pygame.Surface((width, height))
            image.blit(strip, (0, 0), (width*i, 0, width*(i+1), height))
            self.images.append(image)
        self.i = 0
        self.image = self.images[self.i]
        self.c = 0

    def set_cycle(self, length):
        self.cycle = length

    def update(self):
        self.image = self.images[self.i]
        if self.c % self.cycle == 0:
            self.i += 1
        if self.i % len(self.images) == 0:
            self.i = 0
        self.c += 1


def test():
    SPRITEWIDTH = 18

    sprite_sheet = pygame.image.load("/home/gillett/Documents/Code/Python/PlatformerEngine/resources/images/playerstrip.png")

    print(sprite_sheet.get_size()[0])

    screen = pygame.display.set_mode((SPRITEWIDTH, sprite_sheet.get_size()[1]), pygame.RESIZABLE)

    spr_anim = Animation(sprite_sheet, SPRITEWIDTH, 5)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    sys.exit()
                    pygame.quit()

        screen.blit(spr_anim.image, (0, 0))
        spr_anim.update()
        pygame.display.flip()

if __name__ == '__main__':
    test()
