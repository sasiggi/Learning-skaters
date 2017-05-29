import random
import math
from learning import LearningEngine

import plotly 
import plotly.graph_objs as go
import numpy as np

def collides_sub(a, b):
	distx = math.fabs(a[0] - b[0])
	disty = math.fabs(a[1] - b[1])
	dist = math.sqrt((distx*distx) + (disty*disty))
	return dist < collision_radius
	
def collides(a, b):
	#take care of the cases when they are on opposite sides of the edges
	return (collides_sub(a,b) or 
			collides_sub([a[0]+width, a[1]], b) or		# when a is low x and b is high x
			collides_sub([a[0], a[1]+height], b) or		# when a is low y and b is high y 
			collides_sub(a, [b[0]+width, b[1]]) or		# when b is low x and a is high x 
			collides_sub(a, [b[0], b[1]+height])		# when b is low y and a is high y 
			)
	
def get_destination (pos, angle):
	destx = ( pos[0] + (math.cos(math.radians(angles[angle])) * stepsize ) ) % width
	desty = ( pos[1] + (math.sin(math.radians(angles[angle])) * stepsize ) ) % height
	return [destx,desty]
	

# initialize variables


width = 1600	# rink width
height = 1600	# rink height
num_of_angles = 6
angle_res = 360/num_of_angles	# angle resolution
num_of_skaters = 20	# number of skaters
collision_radius = 100		# collision radius
stepsize = 100				# stepsize, should be < 2*collision_radius so it can't move over it
max_iterations = 100000


angles = []		# possible angles
angle = 0
while angle < 360:
	angles.append(angle)
	angle = angle + angle_res;	
print(angles)

positions = []		# skater positions
for skater in range(num_of_skaters):
	positions.append([random.uniform(0,width), random.uniform(0,height)]);

# skating loop
def run_algorithm (visualize):
	engine = LearningEngine(num_of_skaters, num_of_angles) 	# the learning engine

	collisions_per_round = [0 for x in range(max_iterations)]
	iterations = 0
	while True:
		print("Iteration nr. "+ str(iterations+1))
		i = 0
		for skater in positions:
			angle = engine.choose(i)
			will_collide = False
			j = 0
			# check for collisions
			for skater2 in positions:
				if i != j:
					if collides(get_destination(skater, angle), skater2):
						will_collide = True
						collisions_per_round[iterations] = collisions_per_round[iterations] + 1
						break
				j += 1
				
			# move
			if not will_collide:
				positions[i] = get_destination(skater, angle)
			
			# learn
			engine.learn(i, angle, not will_collide)
			
			i += 1
			
		print(collisions_per_round[iterations])
		iterations += 1
		if iterations >= max_iterations:
			break
			
	if visualize:
		engine.visualize_history(angle_res)
	
	return engine

def run_test():
	
	test_iterations = 5
	convergence_metric = [0 for x in range(num_of_skaters)]
	for i in range(test_iterations):
		engine = run_algorithm(True)
		[t_max, avg_rewards, angle_distribution] = engine.get_meta()
		highest = 0
		# find the maximum amount of skaters skating in the same direction at the last time step
		for choice in angle_distribution:
			if choice[-1] > highest:
				highest = choice[-1]
			
		convergence_metric[highest-1] += 1
	
	# number of skaters for each angle over time
	x_axis = list(range(1,num_of_skaters+1))

	# Create traces
	data = []
	y_axis = convergence_metric
	trace = go.Bar(
		x = x_axis,
		y = y_axis,
	)
	data.append(trace)
	layout = go.Layout(
			xaxis=dict(
				autorange=True
			),
			yaxis=dict(
				autorange=True
			)
		)
	fig = go.Figure(data=data, layout=layout)
	plotly.offline.plot(fig, filename='hist.html')	
	
	
run_test()

	
	
	
	
	
	
	
	
	