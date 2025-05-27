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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Player fallback

# Font
FONT_SIZE = 36
main_font = pygame.font.SysFont(None, FONT_SIZE)

# --- Game Configuration ---
GROUND_Y = SCREEN_HEIGHT - 80  # Y-coordinate for the ground
PLAYER_START_X = 100
NUMBER_SPEED = 3
PLAYER_GRAVITY = 0.8
PLAYER_JUMP_STRENGTH = -18  # Negative because Y is 0 at top

# Number spawn heights (y-coordinates)
NUMBER_LEVEL_BOTTOM_Y = GROUND_Y - 25  # Numbers appear slightly above ground
NUMBER_LEVEL_TOP_Y = GROUND_Y - 150  # Higher level for numbers


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
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.image = pygame.Surface([40, 50])
            self.image.fill(RED)
            self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_START_X
        # Store a float for precise vertical position
        self.y_float = float(GROUND_Y - self.rect.height)
        self.rect.bottom = GROUND_Y  # Initial rect bottom position

        self.vy = 0  # Vertical velocity
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = PLAYER_JUMP_STRENGTH
            self.on_ground = False

    def update(self):
        # Apply player gravity
        self.vy += PLAYER_GRAVITY
        self.y_float += self.vy
        self.rect.y = int(self.y_float)  # Update rect with integer part

        # Check for ground collision
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.y_float = float(self.rect.y)  # Sync float position with rect
            self.vy = 0
            self.on_ground = True

        # Keep player on screen horizontally (optional, can be fixed)
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
        global game_over
        self.rect.x -= self.speed_x

        if self.rect.right < 0:  # Number has scrolled off screen to the left
            if self.is_prime_val:
                print(f"Missed PRIME by scrolling: {self.value}, GAME OVER!")
                if game_over_sound:
                    game_over_sound.play()
                game_over = True
            self.kill()


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


def reset_game():
    global score, game_over, player
    score = 0
    game_over = False
    # No gravity_direction to reset now

    all_sprites.empty()
    numbers_group.empty()

    player = Player()
    all_sprites.add(player)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

            if event.type == SPAWN_NUMBER_EVENT:
                num_val = random.randint(1, 50)
                level_choice = random.choice(["top", "bottom"])
                new_number = Number(num_val, level_choice)
                all_sprites.add(new_number)
                numbers_group.add(new_number)

    if not game_over:
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

        # Draw / Render
        screen.fill(WHITE)
        # Draw a simple ground line
        pygame.draw.line(screen, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)
        all_sprites.draw(screen)

        score_display = main_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_display, (10, 10))

        pygame.display.flip()
    else:
        if not show_game_over_screen():
            running = False
        else:
            reset_game()

    clock.tick(60)

pygame.quit()
