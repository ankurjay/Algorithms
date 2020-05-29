from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np
import random
import math

class Map:
    def __init__(self,height=5, width=5, numObjects=1):
        self.h=height
        self.w=width
        self.n=numObjects
        self.occupancies=np.zeros((self.h,self.w))
        self.obstacles = set()
        self.placeObjects()

    def placeObjects(self):
        for i in range(self.n):
            h = random.randint(0,self.h-1)
            w = random.randint(0,self.w-1)
            self.occupancies[h][w] = 1
            self.obstacles.add((h,w))

    def getMapDetails(self):
        return {'occupancies':self.occupancies,'height':self.h, 'width':self.w, 'objects':self.n, 'obstacles':self.obstacles}

class Simulation:
    def __init__(self,mapDict):
        self.h = mapDict['height']
        self.w = mapDict['width']
        self.n = mapDict['objects']
        self.occupancies = mapDict['occupancies']
        self.obstacles = mapDict['obstacles']
        self.robot = None
        self.goal = None

    def createGoal(self,h,w):
        if not self.goal:
            self.goal = (h,w)
            self.occupancies[h][w] = 3
            print "Goal created at (" + str(h) + "," + str(w) + ") : "+ str(self.occupancies[h][w])
        else:
            if self.occupancies[h][w] == 0:
                (h_old, w_old) = self.goal
                self.goal = (h, w)
                self.occupancies[h_old][w_old] = 0
                self.occupancies[h][w] = 3
                print "Goal updated at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
            else:
                print "Cannot create goal. goal already exists"
                return

    def createRobot(self,h,w):
        if not self.robot:
            self.robot = (h,w)
            self.occupancies[h][w] = 2
            print "Robot created at (" + str(h) + "," + str(w) + ") : "+ str(self.occupancies[h][w])
        else:
            print "Cannot create robot. goal already exists"
            return

    def getMap(self):
        return self.occupancies

    def getRobotCoordinates(self):
        return self.robot

    def getGoalCoordinates(self):
        return self.goal

    def plan(self):
        '''
        :param initpose: A tuple of x and y coordinates of initial pose of robot
        :param goalpose: A tuple of x and y coordinates of goal of robot
        :param obstacles: A set containing tuples of x and y coordinates of static obstacles
        :param robots: A set containing tuples of x and y coordinates of all other robots in the environment
        :return: Empty list if no path found in 20000 iterations, or Optimal List of coordinates to visit
        '''
        initpose = self.getRobotCoordinates()
        goalpose = self.getGoalCoordinates()
        obstacles = self.obstacles
        agenda = Agenda()
        initcost = heuristic(initpose, goalpose)
        visited = {initpose}
        visited.update(obstacles)
        initpath = [] + [initpose]
        agenda.addToAgenda(initpath, initcost)
        count = 0
        while True:
            a = agenda.getFromAgenda()
#            print "Getting from agenda : "
#            print a
            count += 1
            if count == 1000000:
                print "Too long to search"
                print "iterations taken =  " + str(count)
                return []
                break
            if a[1][-1] == goalpose:
                retrpath = a[1]
                print "optimal path found"
                print "iterations taken = " + str(count)
                return retrpath
            else:
                retrpath = a[1]
                last_state_x = retrpath[-1][0]
                last_state_y = retrpath[-1][1]
                if last_state_x - 1 < 0 or last_state_y + 0 >= self.w or (last_state_x - 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_up = retrpath + [(last_state_x - 1, last_state_y + 0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_up, heuristic((last_state_x - 1, last_state_y + 0), goalpose))

                if last_state_x + 1 > self.h or last_state_y + 0 >= self.w or (last_state_x + 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_down = retrpath + [(last_state_x + 1, last_state_y + 0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_down, heuristic((last_state_x + 1, last_state_y + 0), goalpose))

                if last_state_x + 0 > self.h or last_state_y + 1 > self.w or (last_state_x + 0, last_state_y + 1) in visited:
                    pass
                else:
                    pose_right = retrpath + [(last_state_x + 0, last_state_y + 1)]
                    visited.add((last_state_x + 0, last_state_y + 1))
                    agenda.addToAgenda(pose_right, heuristic((last_state_x + 0, last_state_y + 1), goalpose))

                if last_state_x + 0 > self.h or last_state_y - 1 < 0 or (last_state_x + 0, last_state_y - 1) in visited:
                    pass
                else:
                    pose_left = retrpath + [(last_state_x + 0, last_state_y - 1)]
                    visited.add((last_state_x + 0, last_state_y - 1))
                    agenda.addToAgenda(pose_left, heuristic((last_state_x + 0, last_state_y - 0), goalpose))

    def plot(self):
        self.getFigure()
        planned_path = self.plan()
        for item in planned_path:
            x = item[0]
            y = item[1]
            self.occupancies[x][y] = 4
        self.occupancies[self.robot[0]][self.robot[1]] = 2
        self.occupancies[self.goal[0]][self.goal[1]] = 3
        self.showMap()


    def getFigure(self):
        return plt.figure(figsize=(self.h, self.w))

    def showMap(self):
        if self.robot is not None and self.goal is not None:
            cmap = colors.ListedColormap(['white', 'black', 'red', 'green','blue'])
        else:
            cmap = colors.ListedColormap(['white', 'black'])
        plt.gca().invert_yaxis()
        plt.imshow(self.getMap(), interpolation='nearest', cmap=cmap)
        plt.pause(5)

class Agenda:
    def __init__(self):
        self.agenda = []

    def addToAgenda(self,path, hc):
        cost = len(path) + hc
        self.agenda.append([cost, path])
        self.agenda = sorted(self.agenda, key=lambda x: x[0])

    def getFromAgenda(self):
        return self.agenda.pop(0)

    def isEmpty(self):
        return not any(self.agenda)

def heuristic(ip,gp):
    return math.sqrt((ip[0]-gp[0])**2 + (ip[1]-gp[1])**2)
#    return abs(ip[0]-gp[0]) + abs(ip[1]-gp[1])

if __name__ == '__main__':
    h = 50
    w = 50
    n = 50
    newMap = Map(h, w, n)
    sim = Simulation(newMap.getMapDetails())
    sim.createRobot(random.randint(0, h - 1), random.randint(0, w - 1))
    sim.createGoal(random.randint(0, h - 1), random.randint(0, w - 1))
    sim.getFigure()
    sim.showMap()
    sim.plot()


