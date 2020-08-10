import pygame as pg
pg.font.init()

import os, sys, random

# Initialise Global Constants
WIN_WIDTH = 500
WIN_HEIGHT = 800

FLOOR = 600

# Load Images, Scale them and Store in Global Variables
BIRD_IMGS = [pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird1.png"))), pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird2.png"))), pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "base.png")))
BG_IMGS = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bg.png")))

# Fonts Variable
STATS_FONT = pg.font.SysFont("comicsans", 50)

# Initialise Pygame Window
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption("Flappy Bird")


# Bird Class
class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 40
	ROT_VEL = 10
	ANIM_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.velocity = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.velocity = -9 # Step of 9 pixel in upward direction
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		displacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2 # Formula for calculating displacement for Arc Trajectory

		# Controlling  Bird Position within the Limits
		if displacement >= 16:
			displacement = 16

		if displacement < 0 :
			displacement -= 2

		self.y = self.y + displacement 

		# if going up, tilt the bird upwards
		if displacement < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION

		# else, keep it straight
		else :
			if self.tilt > -90:
				self.tilt = self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

		# Flapping of wings of the bird by switching between the images 1, 2 and 3 and reversed too
		if self.img_count <= self.ANIM_TIME:
			self.img = self.IMGS[0]
		elif self.img_count <= self.ANIM_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIM_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count <= self.ANIM_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIM_TIME*4+1:
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80:
			self.img = self.IMGS[0]
			self.img_count = self.ANIM_TIME*2

		# Rotating the image from Center point
		rotated_image = pg.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pg.mask.from_surface(self.img) # For Masking Collision


class Pipe:
	GAP = 200 # Between Upper Pipe and Lower Pipe
	VEL = 5 # Velocity of pipes moving
	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0

		self.PIPE_TOP = pg.transform.flip(PIPE_IMG, False, True) # Flipping the Pipe Image for Upper Pipe
		self.PIPE_BOTTOM = PIPE_IMG
		self.passed = False # Pipe passed bird or not
		self.set_height()

	def set_height(self):
		self.height = random.randrange(10, 400) # Set pipe height randomly each time between 40 px to 450 px
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pg.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pg.mask.from_surface(self.PIPE_BOTTOM)

		# Top and Bottom Offset for Collision Calculation
		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		# point of contact for top and bottom pipe with bird
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		# if collide, return true, else false
		if t_point or b_point :
			return True
		return False


class Base:
	VEL = 5 # Same as Pipe Velocity
	WIDTH = BASE_IMG.get_width() 
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0 # X coordinates for 1st instance of the Base Img
		self.x2 = self.WIDTH # for 2nd instance of the Base Img

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		# if 1st img moves out of the screen, place it behind the 2nd image for reappearing again
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


# Create GamePLay Window with Bird, Pipe, Base and Background and render Text
def draw_window(win, bird, pipes, base, score, game_ended=False):
	win.blit(BG_IMGS, (0, -200))

	for pipe in pipes:
		pipe.draw(win)

	text = STATS_FONT.render(f'SCORE : {str(score)}', 1, (0, 0, 0))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 50))

	if game_ended == True:
		endText = STATS_FONT.render("GAME OVER", 1, (200, 0, 0))
		win.blit(endText, (WIN_WIDTH - 150 - endText.get_width(), 300))

	base.draw(win)
	bird.draw(win)

	pg.display.update()

# Main Game Loop
def main():

	# Initialise all classes
	bird = Bird(200, 150)
	base = Base(FLOOR)
	pipes = [Pipe(FLOOR + 50)]

	# Control Variables
	clock = pg.time.Clock()
	running = True
	score = 0
	game_ended = False

	while running:
		clock.tick(30)
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:

				# Check for Game Quit
				if event.key == pg.K_ESCAPE:
					running = False

				# Check for Keypress -> Space
				if event.key == pg.K_SPACE:
					bird.jump()

		# Keep Moving the Bird and the Base until the game has ended
		if game_ended != True:
			bird.move()
			base.move()

		removed_pipes = []
		add_pipe = False

		# Loop of Adding Pipes
		for pipe in pipes:
			if pipe.collide(bird) or bird.y >= FLOOR - 50:
				game_ended = True

			# Remove Pipe as soon as it crosses the screen
			if pipe.x + pipe.PIPE_TOP.get_width() < 0 :
				removed_pipes.append(pipe)
			
			# Check if Pipe has passed the bird
			if not pipe.passed and pipe.x < bird.x - 50:
				pipe.passed = True
				add_pipe = True

			if game_ended != True:
				pipe.move()

		# if bird crosses pipe, increase the score and reappear the pipe from starting position
		if add_pipe:
			score += 1
			pipes.append(Pipe(550))

		for removed_pipe in removed_pipes:
			pipes.remove(removed_pipe)

		# Draw the Updated window
		draw_window(WIN, bird, pipes, base, score, game_ended)

	pg.quit()
	sys.exit()

if __name__ == '__main__':
	main()