# Algorithms
Some Algorithms for Easy Reuse in Simulations

1. `AStarAlgorithm.py` - Barebones code for the algorithm; can be modified for use elsewhere; might have some rare errors
2. `AStarSim_SingleRobot.py` - Algorithm simulated for 1 robot using PyGame
3. `AStarSim_MultiRobotWithClashes.py` - Algorithm simulated for multiple robots using PyGame, clashes are allowed
4. `AStarSim_MultiRobotWithClashPenalty.py` - Algorithm simulated for multiple robots using PyGame, clashes are heavily penalized

These are stand-alone files; each individual python script suffices to run one program. I will progressively clean up the code as I add more features.

Required Libraries:
1) PyGame
2) NumPy

Tested for **Python 2.7**

The following video shows `AStarSim_SingleRobot.py` in action:

![alt-text](https://github.com/ankurjay/Algorithms/blob/master/Capture_SingleRobot.gif)

The following shows `AStarSim_MultiRobotWithClashPenalty.py` in action:

![alt-text](https://github.com/ankurjay/Algorithms/blob/master/Capture_Multi.gif)

