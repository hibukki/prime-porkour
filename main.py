import pygame

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
RED = (255, 0, 0)  # Added for the player


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])  # Simple square for now
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - self.rect.width // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10  # Start near the bottom

    def update(self):
        # Player movement logic will go here
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Create player instance
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Game loop
running = True
clock = pygame.time.Clock()  # For controlling frame rate

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # Draw / Render
    screen.fill(WHITE)
    all_sprites.draw(screen)  # Draw all sprites

    pygame.display.flip()

    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()
