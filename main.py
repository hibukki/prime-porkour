import pygame
import random  # For generating random numbers

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prime Porkour")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # For numbers

# Font for displaying numbers
pygame.font.init()  # Initialize font module
number_font = pygame.font.SysFont(None, 36)


# --- Helper Functions ---
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface([50, 50])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - self.rect.width // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Number(pygame.sprite.Sprite):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.image = number_font.render(str(self.value), True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)  # Start off-screen
        self.speed_y = random.randrange(1, 4)  # Falling speed

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10:  # Remove if it goes off bottom
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- Game Setup ---
player = Player()
all_sprites = pygame.sprite.Group()
numbers_group = pygame.sprite.Group()  # Group for numbers
all_sprites.add(player)

# Timer for spawning numbers
SPAWN_NUMBER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_NUMBER_EVENT, 1000)  # Spawn a new number every 1 second

# --- Game Loop ---
running = True
clock = pygame.time.Clock()
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SPAWN_NUMBER_EVENT:
            # For now, spawn a mix of prime and non-prime numbers
            # We'll refine this later to be more game-like
            num_val = random.randint(1, 30)
            new_number = Number(num_val)
            all_sprites.add(new_number)
            numbers_group.add(new_number)

    # Update
    all_sprites.update()

    # Check for collisions between player and numbers
    # For now, let's say collecting any number gives a point
    # We will differentiate prime/non-prime later
    collided_numbers = pygame.sprite.spritecollide(
        player, numbers_group, True
    )  # True to remove collided sprite
    for number_sprite in collided_numbers:
        score += 1  # Just a placeholder for now
        print(f"Collected: {number_sprite.value}, Score: {score}")

    # Draw / Render
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Display score
    score_text = number_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    clock.tick(60)

# Quit Pygame
pygame.quit()
