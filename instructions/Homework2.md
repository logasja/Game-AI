# Homework 2: Path Network Navigation

One of the main uses of artificial intelligence in games is to perform _path planning_, the search for a sequence of movements through the virtual environment that gets an agent from one location to another without running into any obstacles. For now we will assume static obstacles. In order for an agent to engage in path planning, there must be a topography for the agent to traverse that is represented in a form that can be efficiently reasoned about.

Grid topologies discretize the environment and assumes an agent can be in one discrete cell or another. However, for many games such as 1st-person shooters, a more continuous model of space is beneficial. Depending on the granularity of the grid, a lot of space around obstacles becomes inaccessible in grid-based approaches. Finally, grids result in unneccessarily large number of cell transitions.

A **path network** is a set of path nodes and edges that facilitates obstacle avoidance. The path network discretizes a continuous space into a small number of points and edges that allow transitions between points. However, unlike a grid topology, a path network does not require the agent to be at one of the path nodes at all times. The agent can be at any point in the terrain. When the agent needs to move to a different location and an obstacle is in the way, the agent can move to the nearest path node accessible by straight-line movement and then find a path through the edges of the path network to another path node near to the desired destination.

[![](pathnet.png)](navmesh1.png)

In this assignment, you will be provided with different terrains with obstacles and hard-coded path nodes. You must write the code to generate the path network, as a set of edges between path nodes. An edge between path nodes exists when (a) there is no obstacle between the two path nodes, and (b) there is sufficient space on either side of the edge so that an agent can follow the line without colliding with any obstacles.

We will test path network using a random-walk navigator that moves the agent to the nearest path node and then follows a randomly generated path---sequence of adjacent path nodes.

* * *

## What you need to know

Please consult [homework 1](Homework1.md) for background on the Game Engine. In addition to the information about the game engine provided there, the following elements will be used.

### PathNetworkNavigator

PathNetworkNavigator is defined in core.py. A PathNetworkNavigator is a specialization of a Navigator that works on path networks and contains the smarts for how to get around in the game world. Its primary function is to compute a path between two points that steers the Agent clear of any obstacles.

Member variables:

*   pathnodes: a list of points of the form (x, y) that comprise a path network.
*   pathnetwork: a list of lines of the form ((x1, y1), (x2, y2)) that comprise a path network.

Member functions:

*   computePath(source, destination): Find a path through the path network (causing path to be not None) and call back to the Agent to start moving. This default functionality just instructs the agent to move to the destination.

### RandomNavigator

RandomNavigator is defined in randomnavigator.py. The RandomNavigator causes the Agent to perform a random walk of the path network. The random path terminates after 100 path nodes and the Agent moves directly to its destination from the last random point reached. Thus, the Agent can possibly collide with obstacles if random path does not reach the destination before the threshold is reached.

Member functions:

*   computePath(source, destination): Find a path through the path network (causing path to be not None) and call back to the Agent to start moving. This default functionality just instructs the agent to move to the destination. The path is created by finding the closest path nodes to the source and then randomly selecting successor path nodes in the path network until the closest node to the destination is found. If the path length exceeds 100, then the Agent will be sent to its destination without further collision avoidance.

### Miscellaneous utility functions

Miscellaneous utility functions are found in utils.py.

*   minimumDistance(line, point): returns the shortest distance between a point (x, y) and a line ((x1, y1), (x2, y2)).
*   findClosestUnobstructed(point, nodes, lines): returns the point in nodes that is closest to the given point for which none of the given lines comes between the found point and the given point.

* * *

## Instructions

To complete this assignment, you must (1) implement code to generate a path network for a set of given path nodes in a given terrain. The path network should guarantee that an agent will not collide with an obstacle between any starting point and any destination point in the world. Because we haven't gotten to the part where the Agent can be controlled intelligently, we will use a RandomNavigator, which walks randomly around for a while before proceeding directly to its destination.

To run the project code, use the following commands:

**> python runrandomnavigator0.py  
> python runrandomnavigator1.py  
> python runrandomnavigator2.py  
> python runrandomnavigator3.py  
> python runrandomnavigator4.py**

**Step 1:** Create the edges in the path network.

Modify mybuildpathnetwork.py and complete the myBuildPathNetwork() function. myBuildPathNetwork() takes in a list of pathnodes, a reference to the GameWorld object, and a reference to the agent doing the navigation. myBuildPathNetwork() must return a list of lines between any path nodes that should be considered adjacent. The list of lines must be computed such that each line originates and terminates at a path node (use shallow copies so the game engine can correlate the list of pathnodes and the list of edges) and an agent following the line will not collide with any obstacle.

* * *

## Grading

We will grade your solution based on the following criterion:

*   **Reachability (5 points):** the path network should be such that an agent can navigate from any path node to any other path node along any edge in the network without colliding with an obstacle. We will run a number of tests between randomly chosen path nodes and deduct points for each collision.

* * *

## Hints

Make sure any edge in the path network is traversable by an agent that has physical size. That is, edges in the path network should never come too close to any Obstacle such that an agent blindly following the path edge collides with an Obstacle (or the edges of the map).

* * *

## Submission

To submit your solution, upload your modified mybuildpathnetwork.py. All work should be done within this file.

You should not modify any other files in the game engine.

DO NOT upload the entire game engine.