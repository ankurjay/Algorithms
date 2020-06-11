import pygame
from pygame.locals import *
import random, math, sys
import numpy as np

OBSTACLES = 50
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

# DO NOT TOUCH THIS STUFF----------------------------------------------------------------------------------------------

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
    """
    :param objects: A set of tuples (row,column) that are coordinates of the obstacles
    :return: A group containing obstacles specified by coordinates (column, row) or (x,y)
    """
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
        #print "(correct poses) (row, column) =  : ", (self.rect.top / CELL_SIZE, self.rect.left / CELL_SIZE)
        pass  # Do nothing; obstacles do not move

def createGoal(goal):
    """
    :param goal: A dictionary of goals tuples (row, column)
    :return: A group of goals specified by (column, row) or (x,y)
    """
    goals = pygame.sprite.Group()
    for key in goal:
        G = Goal(goal[key][1], goal[key][0])
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
    """
    :param robot: A dictionary of  robot tuples (row, column)
    :return: A dictionary of robot sprites specified by (column, row) or (x,y)
    """
    robots = {}
    for key in robot.keys():
        robots[key] = Robot(robot[key][1], robot[key][0])
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
        #print "row action : ",action[0], " column action : ",action[1]
        #print "(robot poses) (row,column) : ", (self.rect.top/CELL_SIZE, self.rect.left/CELL_SIZE)

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

    def viewFromAgenda(self):
        return self.agenda[0]

def heuristic(ip, gp):
    return math.sqrt((ip[0] - gp[0]) ** 2 + (ip[1] - gp[1]) ** 2)
#    return abs(ip[0]-gp[0]) + abs(ip[1]-gp[1])

class Simulator(Map):
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
        """Returns a set of tuples of obstacle coordinates"""
        return self.occupancies

    def getRobotCoordinates(self):
        """Returns a dictionary of tuples of robot coordinates"""
        return self.robot

    def getGoalCoordinates(self):
        """Returns a dictionary of tuples of goal coordinates"""
        return self.goal

    def moveUpYRows(self, last_y):
        return last_y - 1

    def moveDownYRows(self, last_y):
        return last_y + 1

    def moveRightXCols(self, last_x):
        return last_x + 1

    def moveLeftXCols(self, last_x):
        return last_x - 1

    def dontMove(self, coord):
        return coord

    def up(self):
        return (-1, 0)

    def down(self):
        return (1, 0)

    def right(self):
        return (0, 1)

    def left(self):
        return (0, -1)

# MODIFY ONLY THIS ---------------------------------------------------------------------------------------------------------

class AStarSimulator(Simulator):
    def __init__(self, height = ROWS, width = COLUMNS, numObjects = OBSTACLES):
        Simulator.__init__(self, height, width, numObjects)
        self.initpose = {}
        self.initaction = {}
        self.goalpose = {}
        self.agenda = {}
        self.visited = {}
        self.initpath = {}
        self.count = {}
        self.flag = {}
        self.a = {}
        self.retrpath = {}
        self.actionplan = {}
        self.next_state = {}
        self.last_state = {}

    def checkAndMoveUp(self, last_state_row, last_state_col, key, next_state):
        # Move Up Conditions
        if self.moveUpYRows(last_state_row) < 0 or self.dontMove(last_state_col) >= self.w:  # Check for out of bounds
            #print "Checking MoveUp, out of bounds"
            pass  # Do nothing
        else:
            if (self.moveUpYRows(last_state_row), self.dontMove(last_state_col)) in self.visited[key]:  # Check for visited nodes
                #print "Checking MoveUp, visited node"
                pass  # Do nothing
            else:
                if next_state:  # If next_state has been filled
                    templist = []
                    for vals in next_state.values(): # Get a list of tuples
                        templist += vals # Append to larger list
                    #print "templist of states", templist
                    if (self.moveUpYRows(last_state_row), self.dontMove(last_state_col)) in templist:  # Check for robot clashes
                        pass  # Do nothing; modify this later
                    else: # If no robot clashes, only then update next_state
                        #print "Currently key is : ", key
                        if key not in next_state:
                            #print "Key not there"
                            next_state[key] = [] + [(self.moveUpYRows(last_state_row), self.dontMove(last_state_col))]
                            #print "Is Key there now? : ", key in next_state
                        else:
                            #print "Key is there"
                            next_state[key] += [(self.moveUpYRows(last_state_row), self.dontMove(last_state_col))]
                        pose_up = self.retrpath[key] + [(self.moveUpYRows(last_state_row), self.dontMove(last_state_col))]
                        action_next = self.actionplan[key] + [self.up()]
                        self.visited[key].add((self.moveUpYRows(last_state_row), self.dontMove(last_state_col)))
                        self.agenda[key].addToAgenda(pose_up, heuristic((self.moveUpYRows(last_state_row), self.dontMove(last_state_col)), self.goalpose[key]), action_next)
                else:  # If next_state has not been filled, update next_state
                    next_state[key] = [] + [(self.moveUpYRows(last_state_row), self.dontMove(last_state_col))]
                    pose_up = self.retrpath[key] + [(self.moveUpYRows(last_state_row), self.dontMove(last_state_col))]
                    action_next = self.actionplan[key] + [self.up()]
                    self.visited[key].add((self.moveUpYRows(last_state_row), self.dontMove(last_state_col)))
                    self.agenda[key].addToAgenda(pose_up, heuristic((self.moveUpYRows(last_state_row), self.dontMove(last_state_col)), self.goalpose[key]), action_next)
        #print "MoveUp Complete\n\n\n\n"
        return next_state # Returns the dictionary of lists of tuples

    def checkAndMoveDown(self, last_state_row, last_state_col, key, next_state):
        # Move Down Conditions
        if self.moveDownYRows(last_state_row) >= self.h or self.dontMove(last_state_col) >= self.w:
            #print "Checking MoveDown, out of bounds"
            pass  # Do nothing
        else:
            if (self.moveDownYRows(last_state_row), self.dontMove(last_state_col)) in self.visited[key]:  # Check for visited nodes
                #print "Checking MoveDown, visited node"
                pass  # Do nothing
            else:
                if next_state:  # If next_state has been filled
                    templist = []
                    for vals in next_state.values(): # Get a list of tuples
                        #print vals
                        templist += vals # Append to larger list
                    #print "templist of states", templist
                    if (self.moveDownYRows(last_state_row), self.dontMove(last_state_col)) in templist:  # Check for robot clashes
                        pass  # Do nothing; modify this later
                    else:
                        #print "Currently key is : ", key
                        if key not in next_state:
                            #print "Key not there"
                            next_state[key] = [] + [(self.moveDownYRows(last_state_row), self.dontMove(last_state_col))]
                            #print "Is Key there now? : ", key in next_state
                        else:
                            #print "Key is there"
                            next_state[key] += [(self.moveDownYRows(last_state_row), self.dontMove(last_state_col))]
                        pose_up = self.retrpath[key] + [(self.moveDownYRows(last_state_row), self.dontMove(last_state_col))]
                        action_next = self.actionplan[key] + [self.down()]
                        self.visited[key].add((self.moveDownYRows(last_state_row), self.dontMove(last_state_col)))
                        self.agenda[key].addToAgenda(pose_up, heuristic((self.moveDownYRows(last_state_row), self.dontMove(last_state_col)), self.goalpose[key]), action_next)
                else:  # If next_state has not been filled
                    next_state[key] = [] + [(self.moveDownYRows(last_state_row), self.dontMove(last_state_col))]
                    pose_up = self.retrpath[key] + [(self.moveDownYRows(last_state_row), self.dontMove(last_state_col))]
                    action_next = self.actionplan[key] + [self.down()]
                    self.visited[key].add((self.moveDownYRows(last_state_row), self.dontMove(last_state_col)))
                    self.agenda[key].addToAgenda(pose_up, heuristic((self.moveDownYRows(last_state_row), self.dontMove(last_state_col)), self.goalpose[key]), action_next)
        #print "MoveDown Complete\n\n\n\n"
        return next_state

    def checkAndMoveRight(self, last_state_row, last_state_col, key, next_state):
        # Move Right Conditions
        if self.dontMove(last_state_row) >= self.h or self.moveRightXCols(last_state_col) >= self.w:
            #print "Checking MoveRight, out of bounds"
            pass  # Do nothing
        else:
            if (self.dontMove(last_state_row), self.moveRightXCols(last_state_col)) in self.visited[key]:  # Check for visited nodes
                #print "Checking MoveRight, visited node"
                pass  # Do nothing
            else:
                if next_state:  # If next_state has been filled
                    templist = []
                    for vals in next_state.values(): # Get a list of tuples
                        templist += vals # Append to larger list
                    #print "templist of states", templist
                    if (self.dontMove(last_state_row), self.moveRightXCols(last_state_col)) in templist:  # Check for robot clashes
                        pass  # Do nothing; modify this later
                    else:
                        #print "Currently key is : ", key
                        if key not in next_state:
                            #print "Key not there"
                            next_state[key] = [] + [(self.dontMove(last_state_row), self.moveRightXCols(last_state_col))]
                            #print "Is Key there now? : ", key in next_state
                        else:
                            #print "Key is there"
                            next_state[key] += [(self.dontMove(last_state_row), self.moveRightXCols(last_state_col))]
                        pose_up = self.retrpath[key] + [(self.dontMove(last_state_row), self.moveRightXCols(last_state_col))]
                        action_next = self.actionplan[key] + [self.right()]
                        self.visited[key].add((self.dontMove(last_state_row), self.moveRightXCols(last_state_col)))
                        self.agenda[key].addToAgenda(pose_up, heuristic((self.dontMove(last_state_row), self.moveRightXCols(last_state_col)), self.goalpose[key]), action_next)
                else:  # If next_state has not been filled
                    next_state[key] = [] + [(self.dontMove(last_state_row), self.moveRightXCols(last_state_col))]
                    pose_up = self.retrpath[key] + [(self.dontMove(last_state_row), self.moveRightXCols(last_state_col))]
                    action_next = self.actionplan[key] + [self.right()]
                    self.visited[key].add((self.dontMove(last_state_row), self.moveRightXCols(last_state_col)))
                    self.agenda[key].addToAgenda(pose_up, heuristic((self.dontMove(last_state_row), self.moveRightXCols(last_state_col)), self.goalpose[key]),action_next)
        #print "MoveRight Complete\n\n\n\n"
        return next_state

    def checkAndMoveLeft(self, last_state_row, last_state_col, key, next_state):
        # Move Left Conditions
        if self.dontMove(last_state_row) + 0 >= self.h or self.moveLeftXCols(last_state_col) < 0:
            #print "Checking MoveLeft, out of bounds"
            pass  # Do nothing
        else:
            if (self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)) in self.visited[key]:  # Check for visited nodes
                #print "Checking MoveLeft, visited node"
                pass  # Do nothing
            else:
                if next_state:  # If next_state has been filled
                    #print "next_state is : ",next_state
                    templist = []
                    for vals in next_state.values(): # Get a list of tuples
                        templist += vals # Append to larger list
                    #print "templist of states", templist
                    if (self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)) in templist:  # Check for robot clashes
                        pass  # Do nothing; modify this later
                    else:
                        #print "Currently key is : ", key
                        if key not in next_state:
                            #print "Key not there"
                            next_state[key] = [] + [(self.dontMove(last_state_row), self.moveLeftXCols(last_state_col))]
                            #print "Is Key there now? : ", key in next_state
                        else:
                            #print "Key is there"
                            next_state[key] += [(self.dontMove(last_state_row), self.moveLeftXCols(last_state_col))]
                        pose_up = self.retrpath[key] + [(self.dontMove(last_state_row), self.moveLeftXCols(last_state_col))]
                        action_next = self.actionplan[key] + [self.left()]
                        self.visited[key].add((self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)))
                        self.agenda[key].addToAgenda(pose_up, heuristic((self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)), self.goalpose[key]), action_next)
                else:  # If next_state has not been filled
                    next_state[key] = [] + [(self.dontMove(last_state_row), self.moveLeftXCols(last_state_col))]
                    pose_up = self.retrpath[key] + [(self.dontMove(last_state_row), self.moveLeftXCols(last_state_col))]
                    action_next = self.actionplan[key] + [self.left()]
                    self.visited[key].add((self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)))
                    self.agenda[key].addToAgenda(pose_up, heuristic((self.dontMove(last_state_row), self.moveLeftXCols(last_state_col)), self.goalpose[key]),action_next)
        #print "MoveLeft Complete\n\n\n\n"
        return next_state

    def plan(self):
        '''
        :return: retrpath (dictionary of lists of full paths), visited (dictionary of sets of visited nodes), actionplan (dictionary of lists of actions)
        '''

        # Initialize empty dictionaries for all variables we will use

        for key in self.robot.keys():
            self.initpose[key] = self.getRobotCoordinates()[key]
            self.initaction[key] = [] + [(0,0)]
            self.goalpose[key] = self.getGoalCoordinates()['goal_'+str(key[-1])]  # Here I am making the same key refer to goal and robot
            self.agenda[key] = Agenda()
            self.visited[key] = {self.initpose[key]}
            self.visited[key].update(self.obstacles) # Adding obstacles to list of visited points so we won't try to move to these points on map
            self.initpath[key] = [] + [self.initpose[key]]
            initcost = heuristic(self.initpose[key], self.goalpose[key])
            self.agenda[key].addToAgenda(self.initpath[key], initcost, self.initaction[key])
            self.count[key] = 0
            self.flag[key] = 0

        # Now the loop starts

        while True:
            # First, check for exit condition : High number of iterations
            if any(count >= 10000 for count in self.count.values()):
                print "Too long to search"
                print "iterations taken =  " + str(self.count)
                return {}, self.visited, {}

            # Next, get from agendas if agendas are not empty and check for goal condition
            for key in self.robot.keys():
                if not self.agenda[key].isEmpty(): # if agenda is not empty
                    self.a[key] = self.agenda[key].getFromAgenda() # a has stored the items on agenda
                    self.count[key] += 1
                    if self.a[key][1][-1] == self.goalpose[key]: # If reached goal
                        print "goal reached for key = ", key
                        if self.flag[key] == 0: # And flag is 0
                            self.flag[key] = 1 # Set flag to 1
                            self.retrpath[key] = self.a[key][1]
                            lastaction = (self.goalpose[key][0] - self.a[key][1][-2][0], self.goalpose[key][1] - self.a[key][1][-2][1])
                            self.actionplan[key] = self.a[key][2] + [lastaction]
                            print "optimal path found"
                            print "iterations taken = " + str(self.count[key])
                        # If flag is nonzero, do nothing
                        elif self.flag[key] == 1:
                            pass
                    else:
                        pass
                elif self.agenda[key].isEmpty(): # If no more options, trigger exit condition by setting flag
                    #print "now agenda is empty"
                    self.flag[key] = 1
                    #print self.flag[key]

            if all(value == 1 for value in self.flag.values()): # If all flags are 1
                print "Exit condition triggered"
                return self.retrpath, self.visited, self.actionplan

            else:
                next_state = {} # Initialize empty dictionary of empty states
                for key in self.robot.keys():
                    if self.flag[key] == 0:
                        self.retrpath[key] = self.a[key][1]
                        self.actionplan[key] = self.a[key][2]
                        last_state_row = self.retrpath[key][-1][0]
                        last_state_col = self.retrpath[key][-1][1]
                        self.last_state[key] = (last_state_row, last_state_col)

                        next_state = self.checkAndMoveUp(last_state_row, last_state_col, key, next_state)
                        next_state = self.checkAndMoveDown(last_state_row, last_state_col, key, next_state)
                        next_state = self.checkAndMoveRight(last_state_row, last_state_col, key, next_state)
                        next_state = self.checkAndMoveLeft(last_state_row, last_state_col, key, next_state)

def visualise(sim):
    pygame.init()
    FPS = 20
    FramePerSec = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    DISPLAYSURF.fill(WHITE)
    pygame.display.set_caption("Game")

    retrpath, visited, actionplan = sim.plan() # Will be dictionary of lists of tuple
    obstacles = createObstacles(sim.getObjects()) # Will be sprite group
    goals = createGoal(sim.getGoalCoordinates()) # will be sprite group
    robots = createRobot(sim.getRobotCoordinates()) # will be dictionary of sprites

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
        for key in retrpath.keys():
            if retrpath[key]: #If exists
                lastpos = retrpath[key].pop(0) #Get the first element
                pathtile = PathSprites(lastpos[1], lastpos[0], color = BLUE) #Assign color from a dictionary later
                static_sprites.add(pathtile)
            for entity in static_sprites:
                DISPLAYSURF.blit(entity.surf, entity.rect)
                entity.move()
            # Next, the dynamic sprites : robots
        for key in retrpath.keys():
            if actionplan[key]: #If exists
                action = actionplan[key].pop(0)
                robots[key].move(action)
                DISPLAYSURF.blit(robots[key].surf, robots[key].rect)

        if all(not vals for vals in actionplan.values()):
            pygame.quit()
            sys.exit()

        pygame.display.update()
        FramePerSec.tick(FPS)  # Make sure this only repeats at FPS rate


# Now just run the Planner --------------------------------------------------------------------------------------------

# First create a Map given some parameters
sim = AStarSimulator(ROWS,COLUMNS,OBSTACLES)

# Next, be able to create a robot and a goal
ROBOTS = 5
for i in range(ROBOTS):
    sim.createRobot(random.randint(0,ROWS-1),random.randint(0,COLUMNS-1), 'robot_'+str(i+1))
    sim.createGoal(random.randint(0, ROWS-1),random.randint(0, COLUMNS-1), 'goal_'+str(i+1))

# Finally, visualize
visualise(sim)

