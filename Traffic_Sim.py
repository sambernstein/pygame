import pygame
from pygame.locals import *
import math
import random
import copy

 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def gray(g):
    return (g,g,g)

colors = [WHITE, GREEN, RED, BLUE, gray(180), (44,128,255), (255,128,0)]

GRAY = gray(100)

PI = 3.141592653

pygame.init()
 
# Set the width and height of the screen [width, height]
size = (1250, 700)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Autonomous Traffic Simulator")
 
# Loop until the user clicks the close button.
done = False
pause = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
dt = 0.1

lane_width = 40
class Lane():

	def __init__(self, cars, width = lane_width, color = gray(60)):
		self.cars = cars

		self.width = width
		self.color = color

	def draw_lane(self):
		pygame.draw.rect(screen, self.color ,[0, size[1]/2, size[0], self.width], 0)

car_length = 33
car_width = 22
behind_factor = .1
class Car():
	def __init__(self, x, y, v, a_factor, max_a, color, index, length = car_length, width = car_width):
		self.x = x
		self.v = v
		self.a = 0
		self.a_factor = a_factor
		self.max_a = max_a

		self.length = length
		self.width = width

		self.y = y + .5*(lane_width - self.width)

		self.color = color
		self.index = index

		self.throttle = False

	def calc_acceleration(self):
		global lanes
		lane = lanes[0]

		target_distance = self.length * self.v * behind_factor

		next_index = (self.index+1)%len(lane.cars)

		dist_behind = lane.cars[next_index].x - self.x

		if lane.cars[next_index].x < self.x:
			dist_behind = size[0] - self.x + lane.cars[next_index].x

		self.a = (dist_behind - target_distance) * self.a_factor

		if abs(self.a) > self.max_a:
			self.a = self.max_a*(self.a/(abs(self.a)))

	def update_vectors(self):
		global lanes
		lane = lanes[0]

		next_index = (self.index+1)%len(lane.cars)

		self.v = self.v + self.a*dt
		if self.throttle:
			self.v = 0

		if lane.cars[next_index].x < self.x:
			if size[0] - self.x + lane.cars[next_index].x <= 0:
				self.v = 0
		elif self.x + self.length > lane.cars[next_index].x:
			self.v = 0

		self.x = self.x + self.v*dt

		self.x = self.x%size[0]

	def draw_car(self):
		pygame.draw.rect(screen, self.color, [self.x, self.y, self.length, self.width], 0)

cars_const = []

num_cars = 10.0
space_between = (1/num_cars)*size[0]

max_a_b = (5, 100)
a_bounds = (2, 80)
for f in range(int(num_cars)):
	cars_const.append(Car(f*space_between, size[1]/2, 0, random.randint(a_bounds[0], a_bounds[1]), random.randint(max_a_b[0], max_a_b[1]), colors[f%(len(colors))], f))

lanes = []
cars  = []

for index in range(len(cars_const)):  
    cars.append(None)
    cars[index] = copy.deepcopy(cars_const[index])

lanes.append(Lane(cars))

def reset_lane(lane):
    lanes[lane].cars = copy.deepcopy(cars_const)

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:

	        if event.key == pygame.K_ESCAPE: # quit game
	            pause = False
	            done = True

	        if event.key == pygame.K_p:
	            pause = True

	        while pause:

	            for event in pygame.event.get():
                     if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_p:
                            pause = not pause

                        if event.key == pygame.K_ESCAPE: # quit game
                            pause = not pause
                            done = True

	        if event.key == pygame.K_r:
	        	reset_lane(0)


	    	if event.key == pygame.K_1:
	        	lanes[0].cars[0].throttle = True
	        if event.key == pygame.K_2:
	            lanes[0].cars[1].throttle = True
	        if event.key == pygame.K_3:
	            lanes[0].cars[2].throttle = True
	        if event.key == pygame.K_4:
	            lanes[0].cars[3].throttle = True
	        if event.key == pygame.K_5:
	            lanes[0].cars[4].throttle = True
	        if event.key == pygame.K_6:
	            lanes[0].cars[5].throttle = True
	        if event.key == pygame.K_7:
	            lanes[0].cars[6].throttle = True
	        if event.key == pygame.K_8:
	            lanes[0].cars[7].throttle = True
	        if event.key == pygame.K_9:
	            lanes[0].cars[8].throttle = True
	        if event.key == pygame.K_0:
	            lanes[0].cars[9].throttle = True


        if event.type == pygame.KEYUP:
	    	if event.key == pygame.K_1:
				lanes[0].cars[0].throttle = False
	        if event.key == pygame.K_2:
	            lanes[0].cars[1].throttle = False
	        if event.key == pygame.K_3:
	            lanes[0].cars[2].throttle = False
	        if event.key == pygame.K_4:
	            lanes[0].cars[3].throttle = False
	        if event.key == pygame.K_5:
	            lanes[0].cars[4].throttle = False
	        if event.key == pygame.K_6:
	            lanes[0].cars[5].throttle = False
	        if event.key == pygame.K_7:
	            lanes[0].cars[6].throttle = False
	        if event.key == pygame.K_8:
	            lanes[0].cars[7].throttle = False
	        if event.key == pygame.K_9:
	            lanes[0].cars[8].throttle = False
	        if event.key == pygame.K_0:
	            lanes[0].cars[9].throttle = False

    # --- Game logic should go here
 
 
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(BLACK)

    # --- Drawing code should go here
    for lane in lanes:
	    lane.draw_lane()
	    for car in lane.cars:
	    	car.calc_acceleration()
	    	car.update_vectors()
	    	car.draw_car()
 
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()