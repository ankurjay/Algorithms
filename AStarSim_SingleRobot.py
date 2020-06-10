import pygame
from pygame.locals import *
import random, math, sys
import numpy as np

OBSTACLES = 500
ROWS = 100
COLUMNS = 100
CELL_SIZE = 10

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = CELL_SIZE * COLUMNS
SCREEN_HEIGHT = CELL_SIZE * ROWS

class Map:
    def __init__(self, height=ROWS, width=COLUMNS, numObjects=OBSTACLES):
        self.h = height
        self.w = width
        self.n = numObjects
        self.occupancies = np.zeros((self.h, self.w))
        self.obstacles = set()
        self.placeObjects()

    def placeObjects(self):
        for i in range(self.n):
            h = random.randint(0, self.h - 1)
            w = random.randint(0, self.w - 1)
            self.occupancies[h][w] = 1
            self.obstacles.add((h, w))

    def getObjects(self):
        return self.obstacles

def createObstacles(objects):
    obstacles = pygame.sprite.Group()
    for i in objects:
        O = Obstacles(i[1], i[0])
        obstacles.add(O)
    return obstacles

class Obstacles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        center = (x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2)
        self.surf.fill(BLACK)
        self.rect = self.surf.get_rect(center=center)

    def move(self):
        pass  # Do nothing; obstacles do not move

class PathSprites(pygame.sprite.Sprite):
    def __init__(self, x, y, color=BLUE):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        center = (x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2)
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=center)

    def move(self):
        pass  # Do nothing; obstacles do not move

def createGoal(goal):
    goals = pygame.sprite.Group()
    G = Goal(goal['goal_1'][1], goal['goal_1'][0])
    goals.add(G)
    return goals

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        center = (x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2)
        self.surf.fill(GREEN)
        self.rect = self.surf.get_rect(center=center)

    def move(self):
        pass  # Do nothing; obstacles do not move

def createRobot(robot):
    robots = pygame.sprite.Group()
    R = Robot(robot['robot_1'][1], robot['robot_1'][0])
    robots.add(R)
    return robots

class Robot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.image.load("Player.png")
        self.surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        center = (x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2)
        self.surf.fill(RED)
        self.rect = self.surf.get_rect(center=center)

    def move(self, action):
        self.rect.move_ip(CELL_SIZE*action[1], CELL_SIZE*action[0])
        print (action[0], action[1])
        print (self.rect.top/CELL_SIZE, self.rect.left/CELL_SIZE)

class AStarSimulator(Map):
    def __init__(self, height=ROWS, width=COLUMNS, numObjects=OBSTACLES):
        Map.__init__(self, height, width, numObjects)
        self.robot = None
        self.goal = None

    def createGoal(self, h, w, name):
        if not self.goal and self.occupancies[h][w]==0:
            self.goal = {name: (h, w)}
            self.occupancies[h][w] = 3
            print "Goal created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
        elif name in self.goal:
            print "Cannot create goal. Goal already exists"
            return
        elif name not in self.goal and self.occupancies[h][w]==0:
            self.goal[name] = (h, w)
            self.occupancies[h][w] = 3
            print "Goal created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
        else:
            print "Cannot create Goal at this position"
            return

    def createRobot(self, h, w, name):
        if not self.robot and self.occupancies[h][w]==0:
            self.robot = {name: (h, w)}
            self.occupancies[h][w] = 2
            print "Robot created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
        elif name in self.robot:
            print "Cannot create robot. Robot already exists"
            return
        elif name not in self.robot and self.occupancies[h][w]==0:
            self.robot[name] = (h, w)
            self.occupancies[h][w] = 2
            print "Robot created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
        else:
            print "Cannot create robot at this position"
            return

    def getMap(self):
        return self.occupancies

    def getRobotCoordinates(self):
        """Returns a dictionary of tuples of robot coordinates"""
        return self.robot

    def getGoalCoordinates(self):
        """Returns a dictionary of tuples of goal coordinates"""
        return self.goal

    def plan(self):
        '''
        :param initpose: A tuple of x and y coordinates of initial pose of robot
        :param goalpose: A tuple of x and y coordinates of goal of robot
        :param obstacles: A set containing tuples of x and y coordinates of static obstacles
        :param robots: A set containing tuples of x and y coordinates of all other robots in the environment
        :return: Empty list if no path found in 20000 iterations, or Optimal List of coordinates to visit
        '''
        initpose = self.getRobotCoordinates()['robot_1'] #This is now a dictionary
        initaction = [] + [(0,0)]
        goalpose = self.getGoalCoordinates()['goal_1'] # This is now a dictionary
        obs = self.obstacles
        agenda = Agenda()
        initcost = heuristic(initpose, goalpose)
        visited = {initpose}
        visited.update(obs) # Adding obstacles to list of visited points so we won't try to move to these points on map
        initpath = [] + [initpose]
        agenda.addToAgenda(initpath, initcost, initaction)
        count = 0
        while True:
            a = agenda.getFromAgenda()
            count += 1
            if count == 1000000:
                print "Too long to search"
                print "iterations taken =  " + str(count)
                return [], visited, []
            if a[1][-1] == goalpose:
                retrpath = a[1]
                lastaction = (goalpose[0] - a[1][-2][0], goalpose[1] - a[1][-2][1])
                actionplan = a[2] + [lastaction]
                print "optimal path found"
                print "iterations taken = " + str(count)
                return retrpath, visited, actionplan
            else:
                retrpath = a[1]
                actionplan = a[2]
                last_state_x = retrpath[-1][0]
                last_state_y = retrpath[-1][1]
                if last_state_x - 1 < 0 or last_state_y + 0 >= self.w or (
                        last_state_x - 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_up = retrpath + [(last_state_x - 1, last_state_y + 0)]
                    action_next = actionplan + [(-1,0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_up, heuristic((last_state_x - 1, last_state_y + 0), goalpose), action_next)

                if last_state_x + 1 >= self.h or last_state_y + 0 >= self.w or (
                        last_state_x + 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_down = retrpath + [(last_state_x + 1, last_state_y + 0)]
                    action_next = actionplan + [(1, 0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_down, heuristic((last_state_x + 1, last_state_y + 0), goalpose), action_next)

                if last_state_x + 0 >= self.h or last_state_y + 1 >= self.w or (
                        last_state_x + 0, last_state_y + 1) in visited:
                    pass
                else:
                    pose_right = retrpath + [(last_state_x + 0, last_state_y + 1)]
                    action_next = actionplan + [(0, 1)]
                    visited.add((last_state_x + 0, last_state_y + 1))
                    agenda.addToAgenda(pose_right, heuristic((last_state_x + 0, last_state_y + 1), goalpose), action_next)

                if last_state_x + 0 >= self.h or last_state_y - 1 < 0 or (
                        last_state_x + 0, last_state_y - 1) in visited:
                    pass
                else:
                    pose_left = retrpath + [(last_state_x + 0, last_state_y - 1)]
                    action_next = actionplan + [(0, -1)]
                    visited.add((last_state_x + 0, last_state_y - 1))
                    agenda.addToAgenda(pose_left, heuristic((last_state_x + 0, last_state_y - 0), goalpose), action_next)

class Agenda:
    def __init__(self):
        self.agenda = []

    def addToAgenda(self, path, hc, actionplan):
        cost = len(path) + hc
        self.agenda.append([cost, path, actionplan])
        self.agenda = sorted(self.agenda, key=lambda x: x[0])

    def getFromAgenda(self):
        return self.agenda.pop(0)

    def isEmpty(self):
        return not any(self.agenda)

def heuristic(ip, gp):
    return math.sqrt((ip[0] - gp[0]) ** 2 + (ip[1] - gp[1]) ** 2)
#    return abs(ip[0]-gp[0]) + abs(ip[1]-gp[1])

def visualise(sim):
    pygame.init()
    FPS = 20
    FramePerSec = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    DISPLAYSURF.fill(WHITE)
    pygame.display.set_caption("Game")

    retrpath, visited, actionplan = sim.plan() # Will be lists of lists of tuples, maybe can make it a dictionary?
    obstacles = createObstacles(sim.getObjects())
    goals = createGoal(sim.getGoalCoordinates())
    robots = createRobot(sim.getRobotCoordinates())

    static_sprites = pygame.sprite.Group()
    for i in obstacles:
        static_sprites.add(i)
    for i in goals:
        static_sprites.add(i)

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        DISPLAYSURF.fill(WHITE)  # Refresh the screen

        # Moves and redraws all Sprites
        # First, the static sprites : paths, obstacles and goals
        if retrpath:
            lastpos = retrpath.pop(0)
            pathtile = PathSprites(lastpos[1], lastpos[0], color = BLUE) #Assign color from a dictionary later
            static_sprites.add(pathtile)
        for entity in static_sprites:
            DISPLAYSURF.blit(entity.surf, entity.rect)
            entity.move()
        # Next, the dynamic sprites : robots
        if actionplan:
            action = actionplan.pop(0)
            for i in range(len(robots)):
                robots.sprites()[i].move(action)
                DISPLAYSURF.blit(robots.sprites()[i].surf, robots.sprites()[i].rect)
        if not actionplan:
            pygame.quit()
            sys.exit()

        pygame.display.update()
        FramePerSec.tick(FPS)  # Make sure this only repeats at FPS rate

#----------------------------------------------------------------------------------------------------------------------

# First create a Map given some parameters
sim = AStarSimulator(ROWS,COLUMNS,OBSTACLES)

# Next, be able to create a robot and a goal
ROBOTS = 1
for i in range(ROBOTS):
    sim.createRobot(random.randint(0,ROWS-1),random.randint(0,COLUMNS-1), 'robot_'+str(i+1))
    sim.createGoal(random.randint(0, ROWS-1),random.randint(0, COLUMNS-1), 'goal_'+str(i+1))

# Next, perform sequentially-simultaneous planning of the path for each robot
retrpath, visited, actionplan = sim.plan()

# That's it. We have done the required computations. Now all we have to do is display stuff.
visualise(sim)

