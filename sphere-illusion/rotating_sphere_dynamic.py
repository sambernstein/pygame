# Sam Bernstein 7/17/15
# Rotating sphere
 
import pygame
import math
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

PI = 3.141592653

pygame.init()
 
# Set the width and height of the screen [width, height]
size = (750, 750)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Sphere")
 
# Loop until the user clicks the close button.
done = False
pause = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

cycles = 0
t = 0.0
dt = 0.01

showing_depth = False
front_depth = 10
depth_factor = .2

correct_distribution = True

edge_buffer = 40

start =  edge_buffer
end = size[0] - edge_buffer
sphere_radius = (end - start)/2
center = size[0]/2

circ_speed = 2
circ_color = WHITE
class Circ():
	def __init__(self, x, y, radius = 2, speed = circ_speed):
		self.x = x
		self.y = y
		self.radius = radius
		self.radius_base = radius

		self.speed = speed
		self.amplitude = math.sqrt(sphere_radius**2 - (y-.5*size[1])**2)
		self.phase_shift = math.asin((self.x - center)/float(sphere_radius))

		self.color = circ_color

	def calc_depth(self, side):
		return side*math.sqrt(sphere_radius**2 - (self.x - .5*size[1])**2) + sphere_radius + front_depth

	def draw(self):
		unique_time = t - self.phase_shift
		self.x = int(self.amplitude*math.sin(self.speed*unique_time)) + center
		if showing_depth:
			if 0.5*math.pi <= unique_time%(2*math.pi) <= 1.5*math.pi: # it's behind
				self.radius = int(self.radius_base/(depth_factor*(self.calc_depth(-1)**2)))
			else:
				self.radius = int(self.radius_base/(depth_factor*(self.calc_depth(1)**2)))

		pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 0)

def make_pos(is_y = False):
	if is_y:
		r, theta = [math.sqrt(random.randint(0,sphere_radius))*math.sqrt(sphere_radius), 2*math.pi*random.random()]
		y = .5*size[1] + r * math.sin(theta)
		return int(y)
	return int(random.uniform(start, end))

dots = []

for n in range(10):
	dots.append(Circ(make_pos(), make_pos(correct_distribution)))
	
add_amount = 3
how_often = 3
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

	
	# --- Game logic should go here

	if cycles%how_often == 0:
		if add_amount >= 0:
			for n in range(add_amount):
				dots.append(Circ(make_pos(), make_pos(correct_distribution)))
		else:
			for n in range(abs(add_amount)):
				dots.pop(random.randint(0, len(dots) - 1))


	# --- Drawing code should go here
 
	# First, clear the screen to white. Don't put other drawing commands
	# above this, or they will be erased with this command.
	screen.fill(BLACK)


	for circle in dots:
		circle.draw()
 
	# --- Go ahead and update the screen with what we've drawn.
	pygame.display.flip()

	
 
	# --- Limit to 60 frames per second
	clock.tick(60)


	add_amount = int(math.cos(t)*(.2*len(dots) if len(dots) > 5 else 5))
	if add_amount < 0 and (len(dots) < abs(add_amount)):
		add_amount = abs(add_amount)

	t += dt
	cycles += 1
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()