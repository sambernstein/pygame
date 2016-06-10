# Sam Bernstein 8/11/15
# bistable rotating sphere illusion
 
import pygame
import math
import random


def gray(c = 255):
	return (c,c,c)

## Isaac's desired parameters:
dot_size = 2
number_of_dots = 300
rotation_speed = 2
dot_color = gray(255) # 255 is white, 0 is black
##

correct_distribution = True # so that the dots are randomly distributed along the 2D surface of the perceived sphere, and not along the y-axis or starting x-axis

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

edge_buffer = 40 # distance between edge of circle and edge of display window

start =  edge_buffer
end = size[0] - edge_buffer
sphere_radius = (end - start)/2
center = size[0]/2

class Circ(): # dot object
	def __init__(self, x, y, radius = dot_size, speed = rotation_speed):
		self.x = x
		self.y = y
		self.radius = radius

		self.speed = speed
		self.amplitude = math.sqrt(sphere_radius**2 - (y-.5*size[1])**2)
		self.phase_shift = math.asin((self.x - center)/float(sphere_radius))

		self.color = dot_color

	def draw(self):
		unique_time = t - self.phase_shift
		self.x = int(self.amplitude*math.sin(self.speed*unique_time)) + center

		pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 0)

def make_pos(is_y = False): # generates starting dot coordinates
	if is_y:
		r, theta = [math.sqrt(random.randint(0,sphere_radius))*math.sqrt(sphere_radius), 2*math.pi*random.random()]
		y = .5*size[1] + r * math.sin(theta)
		return int(y)
	return int(random.uniform(start, end))

dots = []

for n in range(number_of_dots):
	dots.append(Circ(make_pos(), make_pos(correct_distribution)))
	
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

	
	# --- Logic should go here

	# --- Drawing code should go below here
 
	# First, clear the screen to white. Don't put other drawing commands
	# above this, or they will be erased with this command.
	screen.fill(BLACK)


	for circle in dots:
		circle.draw() # what actually draws every circle before each update
 
	# --- Go ahead and update the screen with what we've drawn.
	pygame.display.flip()
 
	# --- Limit to 60 frames per second
	clock.tick(60)

	t += dt
	cycles += 1
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()