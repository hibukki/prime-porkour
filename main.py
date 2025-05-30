import pygame
import random
import os

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prime Porkour - Platformer")

# Asset loading (paths and fallback handling)
ASSETS_DIR = "assets"
PLAYER_IMAGE_FILENAME = "pig.png"
COLLECT_PRIME_SOUND_FILENAME = "collect_prime.wav"
GAME_OVER_SOUND_FILENAME = "game_over.wav"
# WIN_SOUND_FILENAME = "win.wav" # Optional: Add a win sound


def load_image_scaled(filename, target_height):
    try:
        image_path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(image_path):
            # print(f"Image not found: {image_path}. Using fallback.") # Less verbose
            return None
        original_image = pygame.image.load(image_path).convert_alpha()
        img_width = original_image.get_width()
        img_height = original_image.get_height()
        scale = target_height / img_height
        return pygame.transform.scale(
            original_image, (int(img_width * scale), target_height)
        )
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading image '{filename}': {e}. Using fallback.")
        return None


def load_sound_file(filename):
    sound_path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(sound_path):
            # print(f"Sound file not found: {sound_path}") # Less verbose
            return None
        return pygame.mixer.Sound(sound_path)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sound '{filename}': {e}.")
        return None


loaded_player_image = load_image_scaled(PLAYER_IMAGE_FILENAME, 50)
collect_prime_sound = load_sound_file(COLLECT_PRIME_SOUND_FILENAME)
game_over_sound = load_sound_file(GAME_OVER_SOUND_FILENAME)
# win_sound = load_sound_file(WIN_SOUND_FILENAME) # Optional

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Player fallback
GREEN_WIN = (0, 200, 0)  # For win message

# Font
FONT_SIZE = 36
main_font = pygame.font.SysFont(None, FONT_SIZE)

# --- Game Configuration ---
GROUND_Y = SCREEN_HEIGHT - 80  # Y-coordinate for the ground
CEILING_Y = 80  # Define a ceiling position
PLAYER_START_X = 100
NUMBER_SPEED = 3
PLAYER_GRAVITY_STRENGTH = 0.8  # Renamed for clarity
PLAYER_JUMP_STRENGTH_UP = -18
PLAYER_JUMP_STRENGTH_DOWN = 18

# Number spawn heights (y-coordinates)
NUMBER_LEVEL_BOTTOM_Y = GROUND_Y - 25  # Numbers appear slightly above ground
NUMBER_LEVEL_TOP_Y = GROUND_Y - 150  # Higher level for numbers

WIN_SCORE = 3000

# Difficulty Scaling Parameters
INITIAL_SPAWN_DELAY = 1700  # Start a bit slower
MIN_SPAWN_DELAY = 600
SPAWN_DELAY_DECREMENT = 75

INITIAL_MIN_NUMBER = 10
INITIAL_MAX_NUMBER = 99
MAX_NUMBER_CAP = 500
MAX_NUMBER_INCREMENT = 30

DIFFICULTY_INCREASE_SCORE_INTERVAL = 200

# --- Game State Variables (initialized in reset_game) ---
score = 0
game_over = False
game_won = False
current_spawn_delay = INITIAL_SPAWN_DELAY
current_min_number = INITIAL_MIN_NUMBER
current_max_number_limit = INITIAL_MAX_NUMBER
last_difficulty_increase_score = 0
player_gravity_direction = 1  # 1 for normal (down), -1 for reversed (up)


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

        # Ensure original_image_normal and _flipped are always Surfaces
        if loaded_player_image:
            self.original_image_normal = loaded_player_image
        else:
            # Create a fallback surface if image loading failed
            fallback_surface = pygame.Surface([40, 50])
            fallback_surface.fill(RED)
            self.original_image_normal = fallback_surface

        self.original_image_flipped = pygame.transform.flip(
            self.original_image_normal, False, True
        )

        # Set initial image based on gravity
        self.image = (
            self.original_image_normal
            if player_gravity_direction == 1
            else self.original_image_flipped
        )
        self.mask = pygame.mask.from_surface(
            self.image
        )  # Now self.image is guaranteed to be a Surface

        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_START_X

        self.y_float = 0.0
        # self.set_initial_vertical_pos() will be called from reset_game or after gravity flip
        # but we need a valid rect.y/rect.top/rect.bottom before that for the first placement by group.add
        if player_gravity_direction == 1:
            self.rect.bottom = GROUND_Y
        else:
            self.rect.top = CEILING_Y

        self.vy = 0
        self.on_surface = True

    def set_initial_vertical_pos(self):
        if player_gravity_direction == 1:  # Normal gravity
            self.y_float = float(GROUND_Y - self.rect.height)
            self.rect.bottom = GROUND_Y
            self.image = self.original_image_normal  # Ensure correct image is set
        else:  # Reversed gravity
            self.y_float = float(CEILING_Y)
            self.rect.top = CEILING_Y
            self.image = self.original_image_flipped  # Ensure correct image is set
        self.mask = pygame.mask.from_surface(
            self.image
        )  # Update mask with current image

    def flip_gravity(self):
        global player_gravity_direction
        player_gravity_direction *= -1
        if player_gravity_direction == 1:
            self.y_float = float(GROUND_Y - self.rect.height)
            self.rect.bottom = GROUND_Y
            self.image = self.original_image_normal
        else:
            self.y_float = float(CEILING_Y)
            self.rect.top = CEILING_Y
            self.image = self.original_image_flipped
        self.mask = pygame.mask.from_surface(self.image)
        self.vy = 0
        self.on_surface = True

    def jump(self):
        if self.on_surface:
            if player_gravity_direction == 1:  # Normal gravity, jump up
                self.vy = PLAYER_JUMP_STRENGTH_UP
            else:  # Reversed gravity, jump "down"
                self.vy = PLAYER_JUMP_STRENGTH_DOWN
            self.on_surface = False

    def update(self):
        # Apply player gravity based on direction
        self.vy += PLAYER_GRAVITY_STRENGTH * player_gravity_direction
        self.y_float += self.vy
        self.rect.y = int(self.y_float)

        # Check for ground/ceiling collision
        if player_gravity_direction == 1:  # Normal gravity
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.y_float = float(self.rect.y)
                self.vy = 0
                self.on_surface = True
        else:  # Reversed gravity
            if self.rect.top <= CEILING_Y:
                self.rect.top = CEILING_Y
                self.y_float = float(self.rect.y)
                self.vy = 0
                self.on_surface = True

        # Keep player on screen horizontally (optional)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


class Number(pygame.sprite.Sprite):
    def __init__(self, value, level, *groups):
        super().__init__(*groups)
        self.value = value
        self.is_prime_val = is_prime(self.value)
        self.image = main_font.render(str(self.value), True, BLACK)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # For pixel-perfect collision

        self.rect.x = SCREEN_WIDTH + random.randrange(50, 200)  # Spawn off-screen right
        if level == "top":
            self.rect.centery = NUMBER_LEVEL_TOP_Y
        else:  # bottom
            self.rect.centery = NUMBER_LEVEL_BOTTOM_Y

        self.speed_x = NUMBER_SPEED

    def update(self):
        global game_over, game_won
        self.rect.x -= self.speed_x

        if self.rect.right < 0:  # Number has scrolled off screen to the left
            if self.is_prime_val and not game_over and not game_won:
                print(f"Missed PRIME by scrolling: {self.value}, GAME OVER!")
                if game_over_sound:
                    game_over_sound.play()
                game_over = True
            self.kill()


# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
numbers_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# --- Timers ---
SPAWN_NUMBER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_NUMBER_EVENT, 1500)  # Adjust spawn rate as needed

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
        for event_loop in pygame.event.get():
            if event_loop.type == pygame.QUIT:
                return False
            if event_loop.type == pygame.KEYDOWN:
                if event_loop.key == pygame.K_q:
                    return False
                if event_loop.key == pygame.K_r:
                    return True
        clock.tick(15)


def show_win_screen():
    screen.fill(BLACK)
    win_text_render = main_font.render("!!! YOU WIN !!!", True, GREEN_WIN)
    final_score_text = main_font.render(f"Final Score: {score}", True, WHITE)
    restart_text = main_font.render("Press R to Play Again or Q to Quit", True, WHITE)
    screen.blit(
        win_text_render,
        (SCREEN_WIDTH // 2 - win_text_render.get_width() // 2, SCREEN_HEIGHT // 3),
    )
    screen.blit(
        final_score_text,
        (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2),
    )
    screen.blit(
        restart_text,
        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50),
    )
    pygame.display.flip()
    # Optional: Play win sound
    # if win_sound: win_sound.play()
    waiting_for_input = True
    while waiting_for_input:
        for event_loop in pygame.event.get():
            if event_loop.type == pygame.QUIT:
                return False
            if event_loop.type == pygame.KEYDOWN:
                if event_loop.key == pygame.K_q:
                    return False
                if event_loop.key == pygame.K_r:
                    return True  # Restart
        clock.tick(15)


def reset_game():
    global score, game_over, game_won, player, player_gravity_direction
    global \
        current_spawn_delay, \
        current_min_number, \
        current_max_number_limit, \
        last_difficulty_increase_score

    score = 0
    game_over = False
    game_won = False
    player_gravity_direction = 1  # Reset player gravity to normal

    current_spawn_delay = INITIAL_SPAWN_DELAY
    current_min_number = INITIAL_MIN_NUMBER
    current_max_number_limit = INITIAL_MAX_NUMBER
    last_difficulty_increase_score = 0

    pygame.time.set_timer(SPAWN_NUMBER_EVENT, current_spawn_delay)

    all_sprites.empty()
    numbers_group.empty()

    player = Player()
    player.set_initial_vertical_pos()  # Ensure correct position and orientation
    all_sprites.add(player)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over and not game_won:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_f:  # 'F' to flip player gravity
                    player.flip_gravity()

            if event.type == SPAWN_NUMBER_EVENT:
                num_val = random.randint(current_min_number, current_max_number_limit)
                level_choice = random.choice(["top", "bottom"])
                new_number = Number(num_val, level_choice)
                all_sprites.add(new_number)
                numbers_group.add(new_number)

    if not game_over and not game_won:
        all_sprites.update()

        # Collision detection using masks for pixel-perfect
        collided_numbers = pygame.sprite.spritecollide(
            player, numbers_group, True, pygame.sprite.collide_mask
        )
        for number_sprite in collided_numbers:
            if number_sprite.is_prime_val:
                score += number_sprite.value
                if collect_prime_sound:
                    collect_prime_sound.play()

                # Check for win condition
                if score >= WIN_SCORE:
                    game_won = True
                    # Optional: if win_sound: win_sound.play()
                    print("YOU WIN!")
                    break  # Stop processing further collisions this frame
            else:
                if game_over_sound:
                    game_over_sound.play()
                print(f"Collected NON-PRIME: {number_sprite.value}, GAME OVER!")
                game_over = True
                break  # Stop checking collisions if game over

        if game_over:  # Check again in case collision caused game over
            if not show_game_over_screen():
                running = False
            else:
                reset_game()
            continue  # Skip drawing the main game if game over screen is shown

        # Difficulty Progression (if game is still active)
        if (
            not game_over and not game_won
        ):  # Re-check because collision might have ended game
            if (
                score - last_difficulty_increase_score
                >= DIFFICULTY_INCREASE_SCORE_INTERVAL
            ):
                last_difficulty_increase_score = score

                # Increase spawn rate
                current_spawn_delay = max(
                    MIN_SPAWN_DELAY, current_spawn_delay - SPAWN_DELAY_DECREMENT
                )
                pygame.time.set_timer(SPAWN_NUMBER_EVENT, current_spawn_delay)
                print(f"Difficulty UP! Spawn delay: {current_spawn_delay}ms")

                # Increase number range
                current_max_number_limit = min(
                    MAX_NUMBER_CAP, current_max_number_limit + MAX_NUMBER_INCREMENT
                )
                # Ensure min_number doesn't exceed max_number_limit if it were also dynamic
                # For now, min_number is fixed at 10 for two-digit start
                print(
                    f"Difficulty UP! Number range: {current_min_number}-{current_max_number_limit}"
                )

        # Draw / Render
        screen.fill(WHITE)
        # Draw a simple ground line
        pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)
        pygame.draw.line(
            screen, BLACK, (0, CEILING_Y), (SCREEN_WIDTH, CEILING_Y), 2
        )  # Draw ceiling line
        all_sprites.draw(screen)

        score_display = main_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_display, (10, 10))

        pygame.display.flip()
    else:
        if game_won:
            if not show_win_screen():
                running = False
            else:
                reset_game()
        else:
            if not show_game_over_screen():
                running = False
            else:
                reset_game()

    clock.tick(60)

pygame.quit()
