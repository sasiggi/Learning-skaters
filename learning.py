import random
import math

import plotly 
import plotly.graph_objs as go
import numpy as np


class LearningEngine:
	
	r_success = 1
	r_failure = -5
	
	
	def __init__(self, num_of_players, num_of_choices):
		self.n = num_of_players
		self.c = num_of_choices
		self.history = []
		self.propensities = [[0 for x in range(self.c)] for y in range(self.n)]
		self.avg_propensities = []
		self.counting = [[0 for x in range(self.c)] for y in range(self.n)]
		self.total_collisions = [0 for x in range(self.c)]
		self.total_successes = [0 for x in range(self.c)]
		self.total_choices = [0 for x in range(self.c)]
		for i in range(self.n):
			self.history.append([])
		
	def learn(self, i, choice, success):
		if success:
			reward = LearningEngine.r_success
			self.total_successes[choice] += 1
		else:
			reward = LearningEngine.r_failure
			self.total_collisions[choice] += 1
			
		
		old = self.propensities[i][choice]
		self.counting[i][choice] += 1
		self.propensities[i][choice] = old + (reward - old)/self.counting[i][choice]
		self.history[i].append([choice, reward])
		
		# if this is the last player in the turn then we update the average-propensity history
		if i == self.n - 1:
			avg = [0 for x in range(self.c)]
			for player in range(self.n):
				for choice in range(self.c):
					avg[choice] += self.propensities[player][choice]
			
			for choice in range(self.c):
				avg[choice] = avg[choice] / self.n
			
			self.avg_propensities.append(avg)
		
	def choose_randomly (self, i):
		return random.randint(0,self.c-1)
		
	
	def choose_wisely(self, i):
		eps = 0.05
		# if len(self.history[i]) < 5000:
			# eps = 0.05 
		# else:
			# eps = 0
		if(random.random() < eps):
			return self.choose_randomly(i)

		diff_threshold = 0.0000000001

		max_propensity = -math.inf
		for x in self.propensities[i]:
			if x > max_propensity:
				max_propensity = x
		# break ties randomly
		max_choices = [i for i, j in enumerate(self.propensities[i]) if abs(j - max_propensity) < diff_threshold]
		final_choice = max_choices[random.randint(0,len(max_choices)-1)]
		if False:
			print(self.propensities[i])
			print(max_propensity)
			print(final_choice)
		return final_choice
	
	def choose(self, i):
		choice = self.choose_wisely(i)
		self.total_choices[choice] += 1
		return choice
		
	def get_meta(self):
		t_max = len(self.history[0])		
		avg_rewards = [[0 for x in range(t_max)] for y in range(self.c)]
		angle_distribution = [[0 for x in range(t_max)] for y in range(self.c)]
		# for all time points
		for time in range(t_max):
			# get [sum_reward,count] for each action at time = time over all players
			reward_meta = [[0,0] for x in range(self.c)]		
			for player in self.history:
				angle_choice = player[time][0]
				choice_reward = player[time][1]
				reward_meta[angle_choice][0] += choice_reward
				reward_meta[angle_choice][1] += 1
			# calculate the average rewards
			for choice in range(self.c):
				if reward_meta[choice][1] != 0:
					avg_rewards[choice][time] = reward_meta[choice][0] / reward_meta[choice][1]
					angle_distribution[choice][time] = reward_meta[choice][1]
				else:
					avg_rewards[choice][time] = 0
					angle_distribution[choice][time] = 0
		
		return [t_max, avg_rewards, angle_distribution]
		
	def visualize_history (self, angle_resolution):
		[t_max, avg_rewards, angle_distribution] = self.get_meta()
		
		propensities_by_choices = [[] for x in range(self.c)]
		for time in range(t_max):
			for choice in range(self.c):
				propensities_by_choices[choice].append(self.avg_propensities[time][choice])
			

		# plot for average rewards over time for each angle	
		x_axis = list(range(t_max))

		data = []
		for choice in range(self.c):
			y_axis = propensities_by_choices[choice]
			trace = go.Scatter(
				x = x_axis,
				y = y_axis,
				mode = 'lines',
				name = str(choice*angle_resolution)+'°'
			)
			data.append(trace)

		layout = go.Layout(
			xaxis=dict(
				title = "Iteration",
				autorange=True
			),
			yaxis=dict(
				title = "Average propensity",
				autorange=True
			)
		)
		fig = go.Figure(data=data, layout=layout)

		# number of skaters for each angle over time
		x_axis = list(range(t_max))

		# Create traces
		data = []
		for choice in range(self.c):
			y_axis = angle_distribution[choice]
			trace = go.Scatter(
				x = x_axis,
				y = y_axis,
				mode = 'lines',
				name = str(choice*angle_resolution)+'°'
			)
			data.append(trace)

		layout2 = go.Layout(
			xaxis=dict(
				title = "Iteration",
				autorange=True
			),
			yaxis=dict(
				title = "Number of players per angle",
				autorange=True
			)
		)
		fig2 = go.Figure(data=data, layout=layout2)		
			
		print("Total collisions: " + str(self.total_collisions))
		print("Total successes: " + str(self.total_successes))
		print("Total choices: " + str(self.total_choices))
		plotly.offline.plot(fig, filename='line-mode.html')	
		plotly.offline.plot(fig2, filename='line-mode-2.html')	
		
				

		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
				