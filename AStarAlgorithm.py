import math
import random

import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt
import plotly.express as px


class Map:
    '''Used to create a Map object'''
    def __init__(self, height=5, width=5, numObjects=1):
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

    def getMapDetails(self):
        return {'occupancies': self.occupancies, 'height': self.h, 'width': self.w, 'objects': self.n,
                'obstacles': self.obstacles}


class Simulation:
    '''Used to create a Simulation object'''
    def __init__(self, mapDict):
        self.h = mapDict['height']
        self.w = mapDict['width']
        self.n = mapDict['objects']
        self.occupancies = mapDict['occupancies']
        self.obstacles = mapDict['obstacles']
        self.robot = None
        self.goal = None

    def createGoal(self, h, w):
        '''
        :param h: height or 'y' coordinate of initial pose of goal
        :param w: width or 'x' coordinate of initial pose of goal
        '''
        if not self.goal:
            self.goal = (h, w)
            self.occupancies[h][w] = 3
            print "Goal created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
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

    def createRobot(self, h, w):
        '''
        :param h: height or 'y' coordinate of initial pose of robot
        :param w: width or 'x' coordinate of initial pose of robot
        '''
        if not self.robot:
            self.robot = (h, w)
            self.occupancies[h][w] = 2
            print "Robot created at (" + str(h) + "," + str(w) + ") : " + str(self.occupancies[h][w])
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
        A* Algorithm planner
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
                return [], visited
                break
            if a[1][-1] == goalpose:
                retrpath = a[1]
                print "optimal path found"
                print "iterations taken = " + str(count)
                return retrpath, visited
            else:
                retrpath = a[1]
                last_state_x = retrpath[-1][0]
                last_state_y = retrpath[-1][1]
                if last_state_x - 1 < 0 or last_state_y + 0 >= self.w or (
                last_state_x - 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_up = retrpath + [(last_state_x - 1, last_state_y + 0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_up, heuristic((last_state_x - 1, last_state_y + 0), goalpose))

                if last_state_x + 1 >= self.h or last_state_y + 0 >= self.w or (
                last_state_x + 1, last_state_y + 0) in visited:
                    pass
                else:
                    pose_down = retrpath + [(last_state_x + 1, last_state_y + 0)]
                    visited.add((last_state_x - 1, last_state_y + 0))
                    agenda.addToAgenda(pose_down, heuristic((last_state_x + 1, last_state_y + 0), goalpose))

                if last_state_x + 0 >= self.h or last_state_y + 1 >= self.w or (
                last_state_x + 0, last_state_y + 1) in visited:
                    pass
                else:
                    pose_right = retrpath + [(last_state_x + 0, last_state_y + 1)]
                    visited.add((last_state_x + 0, last_state_y + 1))
                    agenda.addToAgenda(pose_right, heuristic((last_state_x + 0, last_state_y + 1), goalpose))

                if last_state_x + 0 >= self.h or last_state_y - 1 < 0 or (last_state_x + 0, last_state_y - 1) in visited:
                    pass
                else:
                    pose_left = retrpath + [(last_state_x + 0, last_state_y - 1)]
                    visited.add((last_state_x + 0, last_state_y - 1))
                    agenda.addToAgenda(pose_left, heuristic((last_state_x + 0, last_state_y - 0), goalpose))

    def plot(self):
        '''Does the plotting task for occupancy grid after complete planning'''
        self.getFigure()
        planned_path,visited_nodes = self.plan()
        for item in visited_nodes:
            x = item[0]
            y = item[1]
            self.occupancies[x][y] = 5
            self.occupancies[self.robot[0]][self.robot[1]] = 2
            self.occupancies[self.goal[0]][self.goal[1]] = 3
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
        '''Does plotting task for occupancy grid'''
        if self.robot is not None and self.goal is not None:
            cmap = colors.ListedColormap(['white', 'black', 'red', 'green', 'blue','cyan'])
        else:
            cmap = colors.ListedColormap(['white', 'black'])
        plt.gca().invert_yaxis()
        plt.imshow(self.getMap(), interpolation='nearest', cmap=cmap)
        plt.pause(1e-5)



class Agenda:
    '''A priority queue'''
    def __init__(self):
        '''Initialize empty agenda'''
        self.agenda = []

    def addToAgenda(self, path, hc):
        '''
        :param path: A list of poses (tuples) that signify a succession of states of the robot
        :param hc: heuristic cost as computed from the heuristic function
        '''
        cost = len(path) + hc
        self.agenda.append([cost, path])
        self.agenda = sorted(self.agenda, key=lambda x: x[0])

    def getFromAgenda(self):
        '''Returns the first element of the Agenda'''
        return self.agenda.pop(0)

    def isEmpty(self):
        return not any(self.agenda)


def heuristic(ip, gp):
    '''
        :param ip: A tuple of x and y coordinates of current pose of robot
        :param gp: A tuple of x and y coordinates of goal of robot
        :return: A numerical (double) value of the heuristic cost
        '''
    return math.sqrt((ip[0] - gp[0]) ** 2 + (ip[1] - gp[1]) ** 2)
#    return abs(ip[0]-gp[0]) + abs(ip[1]-gp[1]) # Alternative heuristic - Manhattan Distance. Uncomment this and comment the previous line to use this heuristic

if __name__ == '__main__':
    '''User inputs should be h, w, n.
    h: height of gridmap
    w: width of gridmap
    n: number of obstacles
    
    Optionally, the user may input the robot's initial pose and goal pose as per the commented-out lines
    '''
    h = 50
    w = 50
    n = 50
    newMap = Map(h, w, n)
    sim = Simulation(newMap.getMapDetails())
    sim.createRobot(random.randint(0, h - 1), random.randint(0, w - 1))
    sim.createGoal(random.randint(0, h - 1), random.randint(0, w - 1))
    #sim.createRobot(5, 7)
    #sim.createGoal(34,14)
    sim.getFigure()
    sim.showMap()
    sim.plot()
