import pygame as pg
pg.font.init()
# import neat

import os, sys, random

WIN_WIDTH = 500
WIN_HEIGHT = 800

FLOOR = 600

BIRD_IMGS = [pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird1.png"))), pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird2.png"))), pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "base.png")))
BG_IMGS = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bg.png")))

STATS_FONT = pg.font.SysFont("comicsans", 50)

WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption("Flappy Bird")


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
		self.velocity = -9.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		d = self.velocity * self.tick_count + 1.5 * self.tick_count**2

		if d >= 16:
			d = 16

		if d < 0 :
			d -= 2
		self.y = self.y + d

		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION

		else :
			if self.tilt > -90:
				self.tilt = self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

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

		rotated_image = pg.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pg.mask.from_surface(self.img)


class Pipe:
	GAP = 200
	VEL = 5
	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0

		self.PIPE_TOP = pg.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG
		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(40, 450)
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

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point :
			return True
		return False


class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width() 
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


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


def main():
	bird = Bird(200, 150)
	base = Base(FLOOR)
	pipes = [Pipe(FLOOR)]

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
				if event.key == pg.K_SPACE:
					bird.jump()

		if game_ended != True:
			bird.move()
		removed_pipes = []
		add_pipe = False
		for pipe in pipes:
			if pipe.collide(bird) or bird.y >= FLOOR:
				bird = Bird(-2000, -2000)
				game_ended = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0 :
				removed_pipes.append(pipe)
			
			if not pipe.passed and pipe.x < bird.x - 50:
				pipe.passed = True
				add_pipe = True

			if game_ended != True:
				pipe.move()

		if add_pipe:
			score += 1
			pipes.append(Pipe(550))

		for removed_pipe in removed_pipes:
			pipes.remove(removed_pipe)

		if bird.y + bird.img.get_height() > FLOOR:
			pass

		if game_ended != True:
			base.move()
		draw_window(WIN, bird, pipes, base, score, game_ended)

	pg.quit()
	sys.exit()
if __name__ == '__main__':
	main()