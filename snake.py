import pygame
import random
import time
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
SPEED = 15

# Mandelbrot parameters
MAX_ITER = 128  # More iterations for better detail
# Seahorse Valley - known for detailed spiral patterns
mandelbrot_center_x = -0.747
mandelbrot_center_y = 0.1
mandelbrot_zoom = 200.0  # Initial zoom level
mandelbrot_zoom_speed = 1.003  # Very slow zoom for visible patterns

# Colors (Modern Palette)
BG_COLOR = (15, 15, 15)  # Dark Gray/Black
SNAKE_COLOR = (46, 204, 113)  # Emerald Green
SNAKE_HEAD_COLOR = (39, 174, 96)  # Darker Green
FOOD_COLOR = (231, 76, 60)  # Alizarin Red
TEXT_COLOR = (236, 240, 241)  # Clouds/White
GLOW_COLOR = (46, 204, 113, 100) # Semi-transparent green

# Cache for mandelbrot surface
mandelbrot_surface = None
mandelbrot_surface_zoom = 0

# Pre-computed color palette for performance
COLOR_PALETTE = []
for i in range(256):
    t = i / 256.0
    r = int(9 * (1 - t) * t * t * t * 255)
    g = int(15 * (1 - t) * (1 - t) * t * t * 255)
    b = int(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255)
    COLOR_PALETTE.append((r, g, b))

# Background rendering optimization
RENDER_SCALE = 2  # Render at 1/2 resolution for better quality
RENDER_WIDTH = WIDTH // RENDER_SCALE
RENDER_HEIGHT = HEIGHT // RENDER_SCALE

def render_mandelbrot_background(zoom_level, center_x, center_y):
    """Render mandelbrot set to a surface with given zoom level."""
    global MAX_ITER

    # Use lower iteration count for better performance at high zoom
    effective_max_iter = max(48, int(MAX_ITER - np.log2(zoom_level / 200)))

    y, x = np.ogrid[RENDER_HEIGHT:0:-1, 0:RENDER_WIDTH]
    scale_factor = zoom_level / RENDER_SCALE
    x = (x - RENDER_WIDTH / 2) / scale_factor + center_x
    y = (y - RENDER_HEIGHT / 2) / scale_factor + center_y
    c = x + 1j * y
    z = np.zeros_like(c)
    div_time = np.zeros(z.shape, dtype=np.int32)

    # Vectorized iteration - more efficient
    for i in range(effective_max_iter):
        mask = np.abs(z) <= 2
        if not np.any(mask):
            div_time[div_time == 0] = effective_max_iter
            break
        z[mask] = z[mask] * z[mask] + c[mask]
        div_time[mask & (np.abs(z) > 2)] = i

    # Create small surface
    small_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))

    # Create RGB array - optimized direct assignment
    rgb_array = np.zeros((RENDER_WIDTH, RENDER_HEIGHT, 3), dtype=np.uint8)

    # Use numpy advanced indexing for faster colorization
    normalized = (div_time * 255 // effective_max_iter).clip(0, 255).T  # Transpose for (width, height)

    # Build color lookup
    palette_array = np.array(COLOR_PALETTE, dtype=np.uint8)

    # Assign colors using advanced indexing
    for i in range(min(effective_max_iter, len(COLOR_PALETTE))):
        mask = normalized == i
        if np.any(mask):
            rgb_array[mask] = palette_array[i]

    # Handle inside points
    mask_inside = (div_time >= effective_max_iter).T
    if np.any(mask_inside):
        rgb_array[mask_inside] = (0, 0, 0)

    pygame.surfarray.blit_array(small_surface, rgb_array)

    # Scale up to full size
    return pygame.transform.scale(small_surface, (WIDTH, HEIGHT))

# Font settings
font_style = pygame.font.SysFont("outfit", 35)
score_font = pygame.font.SysFont("outfit", 25)

def show_score(score, elapsed_time=0):
    value = score_font.render(f"SCORE: {score}", True, SNAKE_COLOR)
    # Background for score
    score_rect = value.get_rect(topleft=(20, 20))
    pygame.draw.rect(pygame.display.get_surface(), (30, 30, 30), score_rect.inflate(20, 10), border_radius=5)
    pygame.display.get_surface().blit(value, [20, 20])

    # Display timer
    time_value = score_font.render(f"TIME: {int(elapsed_time)}s", True, SNAKE_COLOR)
    time_rect = time_value.get_rect(topleft=(20, 50))
    pygame.draw.rect(pygame.display.get_surface(), (30, 30, 30), time_rect.inflate(20, 10), border_radius=5)
    pygame.display.get_surface().blit(time_value, [20, 50])

def draw_snake(block_size, snake_list):
    for i, x in enumerate(snake_list):
        color = SNAKE_HEAD_COLOR if i == len(snake_list) - 1 else SNAKE_COLOR
        # Draw snake segment with slight rounding effect
        pygame.draw.rect(pygame.display.get_surface(), color, [x[0], x[1], block_size, block_size], border_radius=4)
        
        # Add a small shine/detail to the head
        if i == len(snake_list) - 1:
            pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (x[0] + 5, x[1] + 5), 2)
            pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (x[0] + 15, x[1] + 5), 2)

def message(msg, color, y_displace=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_displace))
    pygame.display.get_surface().blit(mesg, text_rect)

def game_loop():
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Antigravity Snake')

    clock = pygame.time.Clock()

    game_over = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1

    # Timer tracking
    start_time = time.time()
    final_time = 0

    # Place food
    foodx = round(random.randrange(40, WIDTH - 40 - BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(40, HEIGHT - 40 - BLOCK_SIZE) / 20.0) * 20.0

    current_speed = SPEED

    frame_counter = 0
    while not game_over:
        frame_counter += 1

        # Update mandelbrot zoom continuously
        global mandelbrot_zoom, mandelbrot_surface
        mandelbrot_zoom *= mandelbrot_zoom_speed

        # Reset zoom when it gets too deep
        if mandelbrot_zoom > 1e10:
            mandelbrot_zoom = 200.0

        # Only re-render mandelbrot every 4 frames for performance
        if frame_counter % 4 == 0 or mandelbrot_surface is None:
            mandelbrot_surface = render_mandelbrot_background(
                mandelbrot_zoom, mandelbrot_center_x, mandelbrot_center_y
            )

        while game_close:
            display.blit(mandelbrot_surface, (0, 0))
            message("GAME OVER", FOOD_COLOR, -50)
            message(f"Final Score: {length_of_snake - 1}", TEXT_COLOR, 10)
            message(f"Time: {int(final_time)}s", TEXT_COLOR, 40)
            message("Press C-Play Again or Q-Quit", SNAKE_COLOR, 80)

            show_score(length_of_snake - 1, final_time)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        # Reset mandelbrot zoom
                        mandelbrot_zoom = 200.0
                        game_loop()
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # Boundary check
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            final_time = time.time() - start_time
            game_close = True

        x1 += x1_change
        y1 += y1_change

        # Draw mandelbrot background
        display.blit(mandelbrot_surface, (0, 0))

        # Draw food with a glow/circle effect
        pygame.draw.circle(display, FOOD_COLOR, (int(foodx + BLOCK_SIZE/2), int(foody + BLOCK_SIZE/2)), 8)

        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check self-collision
        for x in snake_list[:-1]:
            if x == snake_head:
                final_time = time.time() - start_time
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        elapsed_time = time.time() - start_time
        show_score(length_of_snake - 1, elapsed_time)

        # Draw zoom level indicator
        zoom_text = score_font.render(f"Zoom: {mandelbrot_zoom:.1e}", True, (150, 150, 150))
        display.blit(zoom_text, (WIDTH - 150, 10))

        pygame.display.update()

        # Check collision with food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(40, WIDTH - 40 - BLOCK_SIZE) / 20.0) * 20.0
            foody = round(random.randrange(40, HEIGHT - 40 - BLOCK_SIZE) / 20.0) * 20.0
            length_of_snake += 1
            # Increase speed slightly
            if length_of_snake % 5 == 0:
                current_speed += 1

        clock.tick(current_speed)

    pygame.quit()
    quit()

if __name__ == "__main__":
    game_loop()
