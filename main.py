import pygame
import random
import os  # For path joining

# Initialize Pygame (mixer specifically for sound)
pygame.mixer.pre_init(44100, -16, 2, 512)  # Optimize buffer for less delay
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prime Porkour")

# Asset loading
ASSETS_DIR = "assets"
PLAYER_IMAGE_FILENAME = "pig.png"
COLLECT_PRIME_SOUND_FILENAME = "collect_prime.wav"
GAME_OVER_SOUND_FILENAME = "game_over.wav"

# Attempt to load player image
try:
    player_image_path = os.path.join(ASSETS_DIR, PLAYER_IMAGE_FILENAME)
    # Check if file exists before attempting to load, to give a clearer custom message
    if not os.path.exists(player_image_path):
        raise FileNotFoundError(f"Player image not found at: {player_image_path}")
    original_player_image = pygame.image.load(player_image_path).convert_alpha()
    # Scale the image
    img_width = original_player_image.get_width()
    img_height = original_player_image.get_height()
    scale = 50 / img_height  # Target height of 50px
    loaded_player_image = pygame.transform.scale(
        original_player_image, (int(img_width * scale), 50)
    )
except (pygame.error, FileNotFoundError) as e:
    print(
        f"Error loading player image '{PLAYER_IMAGE_FILENAME}': {e}. Using fallback rectangle."
    )
    loaded_player_image = None  # Will be handled in Player class


# Attempt to load sounds
def load_sound(filename):
    sound_path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(sound_path):
            raise FileNotFoundError(f"Sound file not found at: {sound_path}")
        sound = pygame.mixer.Sound(sound_path)
        return sound
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sound '{filename}': {e}. Sound will not play.")
        return None


collect_prime_sound = load_sound(COLLECT_PRIME_SOUND_FILENAME)
game_over_sound = load_sound(GAME_OVER_SOUND_FILENAME)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Player
# GREEN = (0, 255, 0) # Prime numbers -- REMOVED
# GRAY = (128, 128, 128) # Non-prime numbers -- REMOVED

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
        if loaded_player_image:
            self.image = loaded_player_image
        else:
            # Fallback if image loading failed
            self.image = pygame.Surface([50, 50])
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
        # color = GREEN if self.is_prime_val else GRAY -- REMOVED
        self.image = main_font.render(
            str(self.value), True, BLACK
        )  # All numbers are BLACK
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
        global game_over  # Allow modification of global game_over state
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            if self.is_prime_val:  # If a prime number is missed
                print(f"Missed PRIME: {self.value}, GAME OVER!")
                if game_over_sound:
                    game_over_sound.play()
                game_over = True
            self.kill()  # Remove if it goes off bottom


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
                score += number_sprite.value
                if collect_prime_sound:
                    collect_prime_sound.play()
                # print(f"Collected PRIME: {number_sprite.value}, Score: {score}") # Less verbose console
            else:
                if game_over_sound:
                    game_over_sound.play()
                print(f"Collected NON-PRIME: {number_sprite.value}, GAME OVER!")
                game_over = True

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
