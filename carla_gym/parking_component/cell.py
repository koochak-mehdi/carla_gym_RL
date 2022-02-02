import pygame

from carla_gym.parking_component.parking_parameters import *

class Cell:
    def __init__(self, x, y, n_rows, n_cols):
        self.x = x
        self.y = y
        self.n_row = n_rows
        self.n_cols = n_cols

        self.w = USED_WIDTH/n_cols
        self.h = USED_HEIGHT/n_rows
    
        self.color = WHITE

        self.f = 0
        self.g = 0
        self.heu = 0
        self.value = 1

        self.obs = False
        self.target = False
        self.closed = False
        self.parent = None

        self.neighbors = list()

        self.reward = None

    def show(self, screen):
        rect_surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, self.color, rect_surface.get_rect())
        screen.blit(
            rect_surface, 
            (self.y * (self.w + MARGIN), self.x * (self.h + MARGIN))
        )

    def show_info(self):
        print(f'x:{self.x} -- y:{self.y}')
        print(f'w: {self.w} -- h: {self.h}')
        print(f'color: {self.color}')
        print(f'is obstacle: {self.obs}')
        print(f'h: {self.heu} -- g: {self.g} -- f: {self.f}')
        print('#'*50)

    def get_coordinate(self):
        return self.x, self.y
    
    def set_neighbors(self, grid_map):
        self.neighbors.append(grid_map[self.x-1][self.y-1])
        self.neighbors.append(grid_map[self.x-1][self.y])
        self.neighbors.append(grid_map[self.x-1][self.y+1])
        self.neighbors.append(grid_map[self.x][self.y-1])
        self.neighbors.append(grid_map[self.x][self.y+1])
        self.neighbors.append(grid_map[self.x+1][self.y-1])
        self.neighbors.append(grid_map[self.x+1][self.y])
        self.neighbors.append(grid_map[self.x+1][self.y+1])
    
    def set_parent(self, cell):
        self.parent = cell