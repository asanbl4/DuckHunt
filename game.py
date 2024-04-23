import pygame
import random
import sys
import math

pygame.init()
# set the size of game
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
# upload the sprites
DUCK_SPRITES = ['./game design/blue1.png', './game design/green1.png', './game design/purple1.png']
KILLED_DUCK_IMAGES = {
    './game design/blue1.png': './game design/blue3.png',
    './game design/green1.png': './game design/green3.png',
    './game design/purple1.png': './game design/purple3.png'
}
background_image = pygame.image.load('./game design/bg.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
shotgun_sound = pygame.mixer.Sound('./sounds/shotgun.mp3')
game_over_sound = pygame.mixer.Sound('./sounds/game_over.mp3')
pygame.mixer.music.load('./sounds/bg_music.mp3')
pygame.mixer.music.play(loops=-1)

# duck class
class Duck(pygame.sprite.Sprite):
    def __init__(self, image_path, movement_type):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(image_path) # load of image
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect() # rectangle for checking the collision
        self.rect.x = 0 - self.rect.width
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = random.randint(1, 3)  # different speeds
        self.movement_type = movement_type
        self.direction = 1  # direction of vertical movement
        self.angle = 0  # angle for sine function movement
        self.killed = False
        self.killed_timer = 0

    def fall_dead(self):
        if self.killed:
            # fall to the bottom of the screen
            if self.rect.y < SCREEN_HEIGHT - self.rect.height:
                self.rect.y += 5

    def update(self):
        if self.killed:

            if self.killed_timer < 120:  # 60 frames per second * 2 seconds
                self.rect.y += 1
                self.killed_timer += 1
            else:
                self.kill()  # remove the duck sprite from the group
        else:
            self.rect.x += self.speed
            if self.rect.x > SCREEN_WIDTH:
                self.rect.x = 0 - self.rect.width
                self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
                self.speed = random.randint(1, 3)  # Adjust this range for different speeds
                self.direction = 1  # Reset direction
                self.angle = 0  # Reset angle
            if self.movement_type == "straight":
                pass  # No additional movement
            elif self.movement_type == "abs":
                self.rect.y += self.speed * self.direction
                if self.rect.y <= 0 or self.rect.y >= SCREEN_HEIGHT - self.rect.height:
                    self.direction *= -1  # Reverse direction if the duck reaches top or bottom
            elif self.movement_type == "sine":
                sine_value = math.sin(self.angle)  # Sine function
                self.rect.y += 5 * sine_value  # Adjust speed as needed
                self.angle += 0.1  # Increment angle for sine curve


# Crosshair class
class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./game design/mishen.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()


class Michen(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('./game design/mishen.png')
        self.image = pygame.transform.scale(self.image, (1, 1))
        mouse = pygame.mouse.get_pos()
        self.rect = pygame.Rect(mouse[0], mouse[1], 1, 1)

    def update(self):
        self.rect.center = pygame.mouse.get_pos()


# terminate function
def terminate():
    pygame.quit()
    sys.exit()


# create game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Hunt")

# load killed duck images
killed_duck_images = {duck: pygame.image.load(img_path) for duck, img_path in KILLED_DUCK_IMAGES.items()}
killed_duck_images = {duck: pygame.transform.scale(image, (50, 50)) for duck, image in killed_duck_images.items()}

# create sprite groups
all_sprites = pygame.sprite.Group()
ducks = pygame.sprite.Group()
crosshair = Crosshair()
all_sprites.add(crosshair)
# variable for making the sprite of the duck to collide with the point
michen = Michen()
all_sprites.add(michen)


# add ducks with different movement types
def add_ducks():
    duck_counts = {"straight": 2, "abs": 1, "sine": 1}  # adjust counts as needed
    for movement_type, count in duck_counts.items():
        for _ in range(count):
            duck_image_index = random.randint(0, 2)
            duck_image = DUCK_SPRITES[duck_image_index]  # select a random duck image
            duck = Duck(duck_image, movement_type)  # pass the image path to Duck constructor
            all_sprites.add(duck)
            ducks.add(duck)


add_ducks()

# dictionary to store killed ducks and their positions
killed_ducks = {}

# initialize life and duck counters
lives = 5
ducks_shot = 0

# font for displaying counters
font = pygame.font.Font(None, 36)

# main game loop
clock = pygame.time.Clock()
score = 0

while True:
    screen.blit(background_image, (0, 0))  # blit background image onto the screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            hits = pygame.sprite.spritecollide(michen, ducks, True)
            if not hits:
                lives -= 1  # reduce lives if the shot misses
            for hit in hits:
                hit.killed = True
                killed_ducks[hit] = hit.rect.topleft
                ducks_shot += 1
            shotgun_sound.play()

    # update sprites
    ducks.update()
    all_sprites.update()

    # draw sprites
    ducks.draw(screen)
    all_sprites.draw(screen)

    # draw killed ducks
    for duck, pos in killed_ducks.items():
        screen.blit(killed_duck_images[duck.image_path], pos)
        if pos[1] < SCREEN_HEIGHT - duck.rect.height:
            killed_ducks[duck] = (pos[0], pos[1] + 5)  # Use the image path of the duck

    life_x = 10
    life_y = 10
    # Draw life counter as red squares
    for i in range(lives):
        heart_image = pygame.image.load('./game design/heart.png')
        heart_image = pygame.transform.scale(heart_image, (60, 60))
        screen.blit(heart_image, (life_x, life_y, 20, 20))
        life_x += 40

    # draw duck counter as blue squares
    duck_x = 10
    duck_y = 50
    for duck in killed_ducks:
        screen.blit(killed_duck_images[duck.image_path], (duck_x, duck_y))
        duck_x += 40

    # check if all lives are gone
    if lives <= 0:
        screen.fill(RED)  # Fill the screen with red color
        game_over_sound.play()
        game_over_text = font.render("Game Over", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)
        terminate()

    pygame.display.flip()
    clock.tick(60)

    if len(ducks) == 0:
        add_ducks()
