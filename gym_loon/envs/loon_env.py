import math
import random
import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
# import winds python file to know wind speeds and directions
import winds

class Loon:
	# loon class for balloons
	def __init__(self):
		self.alt = 1
		# loons start at a random location on the map
		self.x = random.randint(1, 1200)
		self.y = random.randint(1, 700)
	def update_pos(self, x, y):
		# update position of loons by the wind
		self.x = x
		self.y = y
	def update_alt(self, alt):
		# update altitude of loons by player control
		self.alt = alt

class LoonEnv(gym.Env):
	# environment for gym to play with
	metadata = {'render.modes': ['human']}
	def __init__(self):
		# call this initialization to make resets easier
		self.init_help()
		self.is_game_over = False
		# observation is the remaining time
		low = np.array([0.0,])
		high = np.array([self.MAX_TIME,])
		self.observation_space = spaces.Box(low, high, dtype=np.float32)
		# store what the agent tried
		self.curr_episode = -1
		self.action_episode_memory = []

	def init_help(self):
		# config variables defining loon game
		self.MAX_TIME = 100
		# dimensions of the game window match human game
		self.xdim = 1200
		self.ydim = 700
		# dimensions of the grid
		self.map_scale = 100
		# radius of each loon
		self.loon_radius = 160
		# how fast the loons move
		self.speed = 5
		# record the min distance from city to any loon for scoring and rewards
		self.mindist = float('inf')
		# game variables defining rewards
		# total time elapsed
		self.curr_step = 0
		# time elapsed where the city has internet
		self.time_over = 0
		# is there a loon over the city now
		self.loon_over = False
		# define what agent can do
		# move loon 1, 2, 3 to levels 1, 2, 3 and also do nothing
		# 1 2 3 moves loon 1, 4 5 6 moves loon 2, 7 8 9 moves loon 3, 10 does nothing
		self.action_space = spaces.Discrete(10)
		# create city
		self.city_x = random.randint(0, self.xdim / self.map_scale - 1)
		self.city_y = random.randint(0, self.ydim / self.map_scale - 1)
		# create loons
		self.loons = []
		loon_0 = Loon()
		loon_1 = Loon()
		loon_2 = Loon()
		self.loons.append(loon_0)
		self.loons.append(loon_1)
		self.loons.append(loon_2)

	def step(self, action):
		# play the game
		if self.is_game_over:
			raise RuntimeError("Episode is done")
		self.curr_step += 1
		# take an action
		self._take_action(action)
		# get reward of that action
		reward = self._get_reward()
		ob = self._get_state()
		return ob, reward, self.is_game_over, {}

	def _take_action(self, action):
		self.action_episode_memory[self.curr_episode].append(action)
		# update position of loons
		this_mindist = float('inf')
		for l in self.loons:
			# update the position of each loon
			this_x = math.floor(l.x / self.map_scale)
			this_y = math.floor(l.y / self.map_scale)
			# make sure don't go past game space
			if this_x == l.x / self.map_scale:
				this_x -= 1
			elif this_y == l.y / self.map_scale:
				this_y -= 1
			# calculate where the winds take you in x and y directions
			dx = winds.winds[l.alt - 1][0][this_y][this_x]
			dy = winds.winds[l.alt - 1][1][this_y][this_x]
			# calculate what new loon position should be
			new_x = l.x + dx * self.speed
			new_y = l.y + dy * self.speed
			# make sure don't go past the game space, loop around if so
			if new_x >= self.xdim:
				new_x = 1
			elif new_x <= 0:
				new_x = self.xdim - 1
			if new_y >= self.ydim:
				new_y = 1
			elif new_y <= 0:
				new_y = self.ydim - 1
			# update position
			l.update_pos(new_x, new_y)
			# check if any loon is over the city
			city_center_x = self.map_scale * self.city_x + self.map_scale / 2
			city_center_y = self.map_scale * self.city_y + self.map_scale / 2
			# use distance formula
			dist = math.sqrt((city_center_x - l.x)**2 + (city_center_y - l.y)**2)
			# update min distance from city for scoring
			if dist < this_mindist:
				this_mindist = dist
			# if loon is over city, update time over city and bool for rewards
			if dist <= self.loon_radius:
				self.loon_over = True
				self.time_over += 1
			else:
				self.loon_over = False
		self.mindist = this_mindist
		# update alt based on action
		# each action either updates altitude of a loon or does nothing
		if action == 0:
			self.loons[0].update_alt(1)
		elif action == 1:
			self.loons[0].update_alt(2)
		elif action == 2:
			self.loons[0].update_alt(3)
		elif action == 3:
			self.loons[1].update_alt(1)
		elif action == 4:
			self.loons[1].update_alt(2)
		elif action == 5:
			self.loons[1].update_alt(3)
		elif action == 6:
			self.loons[2].update_alt(1)
		elif action == 7:
			self.loons[2].update_alt(2)
		elif action == 8:
			self.loons[2].update_alt(3)
		# update total time
		remaining_steps = self.MAX_TIME - self.curr_step
		time_is_over = (remaining_steps <= 0)
		throw_away = time_is_over and not self.is_game_over
		if throw_away:
			self.is_game_over = True

	def _get_reward(self):
		# update reward
		# based on mindist
		# return self.mindist
		# based on percent over city
		if self.curr_step == 0:
			return 0.0
		else:
			return self.time_over / self.curr_step

	def reset(self):
		# reset environment and returns initial observation
		self.curr_step = -1
		self.curr_episode += 1
		self.action_episode_memory.append([])
		self.is_game_over = False
		# init helper function resets easily
		self.init_help()
		return self._get_state()

	def _get_state(self):
		# get the observation
		ob = [self.MAX_TIME - self.curr_step]
		return ob

	def seed(self, seed):
		# seed for rl wrapper
		random.seed(seed)
		np.random.seed

	def render(self, mode='human', close=False):
		# TODO implement this to look cool
		return
