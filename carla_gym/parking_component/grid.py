from turtle import position
from sympy import im
from carla_gym.parking_component.cell import Cell
from carla_gym.parking_component.parking_parameters import *

class Grid:
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.map = [[Cell(x, y, n_rows, n_cols) for y in range(n_cols)] for x in range(n_rows)]

        self.start = None
        self.target = None

        self.open_set = list()
        self.closed_set = list()

        # class variables
        self.path_list = None
    
    def set_start_target(self, start, target_list):
        self.start = self.map[start[0]][start[1]]
        self.map[start[0]][start[1]].color = GREEN

        self.target = [list() for i in range(len(target_list))]

        for i in range(len(target_list)):
            for target in target_list[i]:
                cell = self.map[target[0]][target[1]]
                cell.target = True
                cell.color = PURPULE
                cell.reward = 20
                self.target[i].append(cell)

    def set_obs(self, obstacles):
        self.obs = obstacles
        self._set_boarders()
        for obs in obstacles:
            cell = self.map[obs[0]][obs[1]]
            cell.obs = True
            cell.color = BLACK
            cell.reward = -20

    def algorithm(self):
        
        path_list = [list() for i in range(len(self.target))]

        for j in range(len(self.target)):
            self.open_set = list()
            self.closed_set = list()
            self.open_set.append(self.start)
            sol_flag = False
            target = self.target[j][0]
            while not sol_flag:
                current_index = 0
                            
                for i in range(len(self.open_set)):
                    if self.open_set[i].f < self.open_set[current_index].f:
                        current_index = i
                
                current = self.open_set[current_index]
                    

                if current == target:
                    sol_flag = True
                    print('found! -- ', current.f)
                    for i in range(current.f):
                        path_list[j].append(current)
                        current.color = PATH_COLOR
                        current = current.parent

                    for cell in self.target[j]:
                        cell.color = PATH_COLOR
                    
                    self.start.color = PATH_COLOR
                    
                    continue
                    
                
                self.closed_set.append(current)
                self.open_set.remove(current)
                
                current.set_neighbors(self.map)
                neighbors = current.neighbors
                for neighbor in neighbors:
                    if neighbor.obs:
                        continue
                    if neighbor not in self.closed_set:
                        temp_g = current.g + current.value
                        if neighbor in self.open_set:
                            if neighbor.g > temp_g:
                                neighbor.g = temp_g
                        else:
                            neighbor.g = temp_g
                            self.open_set.append(neighbor)
                    
                    #print('target -- ', target)
                    neighbor.heu = self._get_distance(neighbor, target)
                    neighbor.f = neighbor.g + neighbor.heu

                    if neighbor.parent is None:
                        neighbor.parent = current

        # distribute rewards
        self._heat_map(path_list)

        self.path_list = path_list    
        return path_list
    
    def get_reward(self, agetnt_position):
        position = self._map_to_world(agetnt_position)
        if position:
            return self.map[position[0]][position[1]].reward

    def reset(self):
        # have to reset all values?!
        for x in range(self.n_rows):
            for y in range(self.n_cols):
                self.map[x][y].color = WHITE

    def _map_to_world(self, agent_position):
        x_agent = agent_position.x
        y_agent = agent_position.y

        x_pygame = (-x_agent + 20.20) * 10.544
        y_pygame = (-y_agent - 8.5) * 10.786
        
        ix = int(y_pygame // (RES[1] // self.n_rows))
        iy = int(x_pygame // (RES[0] // self.n_cols))
        
        if (ix < 0) or (ix > self.n_rows) or \
            (iy < 0) or (iy > self.n_cols):
                return

        #self.map[ix][iy].color = RED

        return ix, iy

    def _get_distance(self, a, b):
        d = abs(a.x - b.x) + abs(a.y - b.y)
        return d

    def _set_boarders(self):
        for x in range(self.n_rows):
            for y in range(self.n_cols):
                self.map[x][0].obs = True
                self.map[x][0].color = BLACK
                self.map[x][0].reward = -20

                self.map[0][y].obs = True
                self.map[0][y].color = BLACK
                self.map[0][y].reward = -20

                self.map[x][self.n_cols-1].obs = True
                self.map[x][self.n_cols-1].color = BLACK
                self.map[x][self.n_cols-1].reward = -20

                self.map[self.n_rows-1][y].obs = True
                self.map[self.n_rows-1][y].color = BLACK
                self.map[self.n_rows-1][y].reward = -20
    
    def _heat_map(self, path_list):
        all_cellpath = list()
        for path in path_list:
            for p in path:
                all_cellpath.append(p)

        for cell in all_cellpath:
            x, y = cell.get_coordinate()
            cell.reward = 5
            for i in range(x-1, -1, -1):
                if self.map[i][y].reward is None: 
                    self.map[i][y].reward = 5 + (i-x)
            for i in range(x+1, self.n_rows):
                if self.map[i][y].reward is None:
                    self.map[i][y].reward = 5 + (x-i)
            for j in range(y-1, -1, -1):
                reward = 5 +(j-y)
                if self.map[x][j].reward is not None:
                    if self.map[x][j].reward < reward:
                        self.map[x][j].reward = reward
                else:
                    self.map[x][j].reward = reward
            for j in range(y, self.n_cols):
                reward = 5 + (y-j)
                if self.map[x][j].reward is not None:
                    if self.map[x][j].reward < reward:
                        self.map[x][j].reward = reward
                else:
                    self.map[x][j].reward = reward

        for x in range(self.n_rows):
            for y in range(self.n_cols):
                cell = self.map[x][y]
                if (cell.obs) or (cell.target):
                    continue
                if cell.reward == 5:
                    cell.color = COLOR_PATH
                elif cell.reward == 4:
                    cell.color = COLOR_1
                elif cell.reward == 3:
                    cell.color = COLOR_2
                elif cell.reward == 2:
                    cell.color = COLOR_3
                else:
                    cell.color = COLOR_4