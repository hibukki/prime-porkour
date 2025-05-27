import pygame
import random
import os  # For path joining

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prime Porkour")

# Asset loading
ASSETS_DIR = "assets"
PLAYER_IMAGE_FILENAME = "pig.png"  # Assuming you have this file

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Player
GREEN = (0, 255, 0)  # Prime numbers
GRAY = (128, 128, 128)  # Non-prime numbers

# Font
FONT_SIZE = 36
main_font = pygame.font.SysFont(None, FONT_SIZE)


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
        try:
            self.original_image = pygame.image.load(
                os.path.join(ASSETS_DIR, PLAYER_IMAGE_FILENAME)
            ).convert_alpha()
            # Scale the image if it's too big/small - let's aim for ~50 pixels height
            img_width = self.original_image.get_width()
            img_height = self.original_image.get_height()
            scale = 50 / img_height
            self.image = pygame.transform.scale(
                self.original_image, (int(img_width * scale), 50)
            )
        except pygame.error as e:
            print(f"Error loading player image: {e}. Using fallback rectangle.")
            self.image = pygame.Surface([50, 50])  # Fallback to red square
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - self.rect.width // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 20  # A bit higher from bottom
        self.speed = 7  # Increased speed

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


class Number(pygame.sprite.Sprite):
    def __init__(self, value, existing_numbers_group, *groups):
        super().__init__(*groups)
        self.value = value
        self.is_prime_val = is_prime(self.value)
        color = GREEN if self.is_prime_val else GRAY
        self.image = main_font.render(str(self.value), True, color)
        self.rect = self.image.get_rect()

        # Attempt to avoid horizontal overlap on spawn
        max_attempts = 10
        for attempt in range(max_attempts):
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-120, -60)  # Adjusted spawn Y

            # Check for collision with already existing, recently spawned numbers
            potential_collision = False
            for num_sprite in existing_numbers_group:
                # Only check against numbers that are still near the top
                if (
                    num_sprite.rect.bottom < FONT_SIZE * 2
                ):  # Check numbers close to spawn area
                    if self.rect.colliderect(num_sprite.rect):
                        potential_collision = True
                        break
            if not potential_collision:
                break  # Found a good spot
        # If still colliding after max_attempts, just place it randomly (it might overlap)

        self.speed_y = random.randrange(2, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # Remove if it goes off bottom screen


# --- Game State Variables ---
score = 0
game_over = False

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
numbers_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# --- Timers ---
SPAWN_NUMBER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_NUMBER_EVENT, 700)  # Spawn numbers slightly faster

# --- Game Loop ---
running = True
clock = pygame.time.Clock()


def show_game_over_screen():
    screen.fill(BLACK)
    game_over_text = main_font.render("GAME OVER", True, RED)
    score_text_render = main_font.render(f"Final Score: {score}", True, WHITE)
    restart_text = main_font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(
        game_over_text,
        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3),
    )
    screen.blit(
        score_text_render,
        (SCREEN_WIDTH // 2 - score_text_render.get_width() // 2, SCREEN_HEIGHT // 2),
    )
    screen.blit(
        restart_text,
        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50),
    )
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False  # Quit game
                if event.key == pygame.K_r:
                    return True  # Restart game
        clock.tick(15)


def reset_game():
    global score, game_over, all_sprites, numbers_group, player
    score = 0
    game_over = False

    all_sprites.empty()
    numbers_group.empty()

    player = Player()
    all_sprites.add(player)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_over and event.type == SPAWN_NUMBER_EVENT:
            num_val = random.randint(1, 50)
            # Pass the numbers_group to check for overlaps
            new_number = Number(num_val, numbers_group)
            all_sprites.add(new_number)
            numbers_group.add(new_number)

    if not game_over:
        # Update
        all_sprites.update()

        # Check for collisions
        collided_numbers = pygame.sprite.spritecollide(player, numbers_group, True)
        for number_sprite in collided_numbers:
            if number_sprite.is_prime_val:
                score += number_sprite.value  # Add number's value if prime
                print(f"Collected PRIME: {number_sprite.value}, Score: {score}")
            else:
                print(f"Collected NON-PRIME: {number_sprite.value}, GAME OVER!")
                game_over = True  # Game over if non-prime is collected

        # Draw / Render
        screen.fill(WHITE)
        all_sprites.draw(screen)

        score_display = main_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_display, (10, 10))

        pygame.display.flip()
    else:
        if not show_game_over_screen():  # Returns False if Q is pressed
            running = False
        else:  # Returns True if R is pressed
            reset_game()

    clock.tick(60)

# Quit Pygame
pygame.quit()
