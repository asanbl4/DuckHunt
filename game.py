import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

DUCK_SPRITES = ['./game design/blue1.png', './game design/green1.png', './game design/purple1.png']
KILLED_DUCK_IMAGES = {
    './game design/blue1.png': './game design/blue3.png',
    './game design/green1.png': './game design/green3.png',
    './game design/purple1.png': './game design/purple3.png'
}
background_image = pygame.image.load('./game design/bg.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


# Duck class
class Duck(pygame.sprite.Sprite):
    def __init__(self, image_path, movement_type):
        super().__init__()
        self.image_path = image_path  # Store the image path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = 0 - self.rect.width
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = random.randint(1, 3)  # different speeds
        self.movement_type = movement_type
        self.direction = 1  # Direction of vertical movement
        self.angle = 0  # Angle for sine function movement
        self.killed = False
        self.killed_timer = 0

    def update(self):
        if self.killed:
            # Slowly fall down and disappear after 2 seconds
            if self.killed_timer < 120:  # 60 frames per second * 2 seconds
                self.rect.y += 1
                self.killed_timer += 1
            else:
                self.kill()  # Remove the duck sprite from the group
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


# Terminate function
def terminate():
    pygame.quit()
    sys.exit()


# Create game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Hunt")

# Load killed duck images
killed_duck_images = {duck: pygame.image.load(img_path) for duck, img_path in KILLED_DUCK_IMAGES.items()}
killed_duck_images = {duck: pygame.transform.scale(image, (50, 50)) for duck, image in killed_duck_images.items()}

# Create sprite groups
all_sprites = pygame.sprite.Group()
ducks = pygame.sprite.Group()
crosshair = Crosshair()
all_sprites.add(crosshair)


# Add ducks with different movement types
def add_ducks():
    duck_counts = {"straight": 2, "abs": 1, "sine": 1}  # Adjust counts as needed
    for movement_type, count in duck_counts.items():
        for _ in range(count):
            duck_image = random.choice(DUCK_SPRITES)  # Select a random duck image
            duck = Duck(duck_image, movement_type)  # Pass the image path to Duck constructor
            all_sprites.add(duck)
            ducks.add(duck)


add_ducks()

# Dictionary to store killed ducks and their positions
killed_ducks = {}

# Initialize life and duck counters
lives = 5
ducks_shot = 0

# Font for displaying counters
font = pygame.font.Font(None, 36)

# Main game loop
clock = pygame.time.Clock()
score = 0

while True:
    screen.blit(background_image, (0, 0))  # Blit background image onto the screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            hits = pygame.sprite.spritecollide(crosshair, ducks, True)
            if not hits:
                lives -= 1  # Reduce lives if the shot misses
            for hit in hits:
                hit.killed = True
                killed_ducks[hit] = hit.rect.topleft
                ducks_shot += 1

    # Update sprites
    ducks.update()
    all_sprites.update()

    # Draw sprites
    ducks.draw(screen)
    all_sprites.draw(screen)

    # Draw killed ducks
    for duck, pos in killed_ducks.items():
        screen.blit(killed_duck_images[duck.image_path], pos)  # Use the image path of the duck

    # Draw life counter as red squares
    for i in range(lives):
        life_x = 10 + i * 30
        life_y = 10
        pygame.draw.rect(screen, RED, (life_x, life_y, 20, 20))

    # Draw duck counter as blue squares
    for i in range(ducks_shot):
        duck_x = 10 + i * 30
        duck_y = 50
        pygame.draw.rect(screen, BLUE, (duck_x, duck_y, 20, 20))

    # Check if all lives are gone
    if lives <= 0:
        screen.fill(RED)  # Fill the screen with red color
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
