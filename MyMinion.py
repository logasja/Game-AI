__author__ = "jacob logas"
'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from moba import *

# Counts number of defenders
squads = {'defend': 0, 'backup': 0, 'attacking': 0}
# minion_cnt = 0

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		# self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.target = None
		# If the state has finished
		self.states = [Idle, Attack, Move, Moving, Pursue, Patrol]
		
		# self.squad = 'backup'

		self.squad = np.random.choice(squads.keys(), 1, p=[0.1,0.3,0.6])[0]
		if squads['defend'] > 5 and self.squad == 'defend':
			self.squad = 'attacking'
		if squads['backup'] > 5 and self.squad == 'backup':
			self.squad = 'attacking'
		squads[self.squad] += 1
		# global minion_cnt
		# minion_cnt += 1
		# print minion_cnt
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)

	def die(self):
		squads[self.squad] -= 1
		Minion.die(self)


############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		agent = self.agent

		# Then if you have a target and its in range, attack it or pursue if not in range
		if agent.target:
			dist = distance(agent.target.position, agent.position)
			# If in shooting range, shoot at enemy
			if dist < BULLETRANGE:
				agent.changeState(Attack)
			# If not in range and a backup squad character, pursue enemy
			elif agent.squad == 'backup' and dist > BULLETRANGE/2:
				agent.changeState(Pursue)
			# If any other type of character, forget your target
			else:
				agent.target = None
		# If no targets are available, look for one or move
		else:
			agent.changeState(Move, agent.squad, agent.getTeam())
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		State.execute(self, delta)
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

def getOptimalEnemy(agent):
	if agent.target and agent.target.alive and distance(agent.getLocation(), agent.target.getLocation()) < BULLETRANGE:
		return agent.target
	towers = filter(lambda x, agent=agent: x.getTeam() != agent.getTeam() and distance(x.getLocation(), agent.getLocation()) < BULLETRANGE, agent.getVisibleType(Tower))
	if towers:
		return min(towers, key=lambda x: x.getHitpoints())
	bases = filter(lambda x, agent=agent: x.getTeam() != agent.getTeam() and distance(x.getLocation(), agent.getLocation()) < BULLETRANGE, agent.getVisibleType(Base))
	if bases:
		return min(bases, key=lambda x: x.getHitpoints())
	enemies = filter(lambda x, agent=agent: x.getTeam() != agent.getTeam() and distance(x.getLocation(), agent.getLocation()) < BULLETRANGE, agent.getVisibleType(Minion))
	if enemies:
		return min(enemies, key=lambda x: x.getHitpoints())
	return None

# Find list of nodes within the radius of a provided point
def getPointInRadius(p, r_out, r_inner, possibleDests):
	points = filter(lambda x, p=p, r_out=r_out, r_inner=r_inner: distance(x,p) <= r_out and distance(x,p) >= r_inner, possibleDests)
	# print points
	return points[np.random.choice(len(points), 1)[0]]

##############################
### Attack
###
### Shoots at the minion's target
### 

class Attack(State):
	def parseArgs(self, args):
		pass
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		# Shoot at the target
		agent = self.agent
		if not agent.target or not agent.target.alive:
			agent.target = getOptimalEnemy(agent)
			agent.changeState(Idle)
			return

		if agent.canfire:
			agent.turnToFace(agent.target.getLocation())
			agent.shoot()
		if agent.squad == 'defend':
			agent.changeState(Patrol)
		else:
			agent.changeState(Idle)		

##############################
### Move
###
### Move to the given position
### interruptable: argument that if true allows the
### agent to disregard its direction

class Move(State):
	def parseArgs(self, args):
		self.squad = args[0]
		self.team = args[1]
		self.time = 0
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		agent = self.agent
		world = self.agent.world
		possibleDests = agent.getPossibleDestinations()
		# TODO: If you are offense, support low health allies or continue toward base
		if self.squad == 'attacking':
			enemy_towers = world.getEnemyTowers(self.team)
			if enemy_towers:
				agent.target = np.random.choice(enemy_towers, 1)[0]
			else:
				enemy_bases = world.getEnemyBases(self.team)
				agent.target = np.random.choice(enemy_bases, 1)[0]
			agent.navigateTo(getPointInRadius(agent.target.getLocation(), BULLETRANGE-1, agent.target.getMaxRadius(), possibleDests))
			agent.changeState(Moving, False)
		# TODO: If you are part of the backup, support medium health attackers or flank
		elif self.squad == 'backup':
			enemy_bases = world.getEnemyBases(self.team)
			base = np.random.choice(enemy_bases, 1)[0]

			agent.navigateTo(getPointInRadius(base.getLocation(), BASEBULLETRANGE, base.getMaxRadius(), possibleDests))
			agent.changeState(Moving, True)
		# If you are defense, stay at the base and wait
		elif self.squad == 'defend':
			# If outside of some radius, move toward it
			my_base_structs = [world.getBaseForTeam(self.team)] + world.getTowersForTeam(self.team)
			defending = np.random.choice(my_base_structs, 1)[0]
			agent.navigateTo(getPointInRadius(defending.getLocation(), BULLETRANGE, defending.getMaxRadius(), possibleDests))
			agent.changeState(Moving, True)



##############################
### Moving
###
### Moving to a position
### interruptable: argument that if true allows the
### agent to disregard its direction

class Moving(State):
	def parseArgs(self, args):
		self.interruptable = args[0]
		self.time = 0
		self.offset = np.random.randint(500, 1000)

	def execute(self, delta = 0):
		State.execute(self, delta)
		agent = self.agent
		self.time += delta
		if time > self.offset:
			self.time = 0
			# Look for enemies in attack range while moving
			if agent.isMoving() and self.interruptable:
				agent.target = getOptimalEnemy(self.agent)
				if agent.target:
					agent.changeState(Attack)
				return
			# Shoot while passing but do not totally engage
			elif agent.isMoving() and not self.interruptable:
				enemy = getOptimalEnemy(agent)
				if agent.canfire and enemy:
					agent.turnToFace(enemy.getLocation())
					agent.shoot()
				return
			elif agent.squad == 'defend':
				agent.changeState(Patrol)
			else:
				agent.changeState(Idle)


##############################
### Pursue
###
### Follows the target enemy agent within attacking distance
###

class Pursue(State):
	def parseArgs(self, args):
		pass

	def execute(self, delta = 0):
		State.execute(self, delta)
		agent = self.agent
		if agent.target.alive:
			agent.navigateTo(agent.target.getLocation())
			agent.changeState(Moving, False)
		else:
			agent.target = None
			agent.changeState(Idle)
		pass


##############################
### Patrol
###
### Follows the target enemy agent within attacking distance
###

class Patrol(State):
	def parseArgs(self, args):
		self.look_timer = 0
		self.move_frequency = np.random.randint(3000, 5000)
		self.move_timer = 0
		pass

	def execute(self, delta = 0):
		State.execute(self, delta)
		agent = self.agent
		self.look_timer += delta
		self.move_timer += delta
		target = getOptimalEnemy(agent)
		if target:
			agent.changeState(Attack)
		if self.move_timer > self.move_frequency:
			agent.changeState(Move, agent.squad, agent.getTeam())
