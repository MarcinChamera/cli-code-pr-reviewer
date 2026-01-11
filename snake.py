import pygame
import random
import time
import numpy as np
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
SPEED = 10

# Mandelbrot parameters
MAX_ITER = 64
mandelbrot_center_x = -0.747
mandelbrot_center_y = 0.1
mandelbrot_zoom = 200.0
mandelbrot_zoom_speed = 1.003

# Colors (Modern Palette)
BG_COLOR = (15, 15, 15)
SNAKE_COLOR = (46, 204, 113)
SNAKE_HEAD_COLOR = (39, 174, 96)
FOOD_COLOR = (231, 76, 60)
TEXT_COLOR = (236, 240, 241)

# Cache for mandelbrot surface
mandelbrot_surface = None

# Pre-computed color palette for performance
COLOR_PALETTE = []
for i in range(256):
    t = i / 256.0
    r = int(9 * (1 - t) * t * t * t * 255)
    g = int(15 * (1 - t) * (1 - t) * t * t * 255)
    b = int(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255)
    COLOR_PALETTE.append((r, g, b))

# Background rendering optimization
RENDER_SCALE = 4
RENDER_WIDTH = WIDTH // RENDER_SCALE
RENDER_HEIGHT = HEIGHT // RENDER_SCALE


def render_mandelbrot_background(zoom_level, center_x, center_y):
    """Render mandelbrot set to a surface with given zoom level."""
    effective_max_iter = 48

    y, x = np.ogrid[RENDER_HEIGHT:0:-1, 0:RENDER_WIDTH]
    scale_factor = zoom_level / RENDER_SCALE
    x = (x - RENDER_WIDTH / 2) / scale_factor + center_x
    y = (y - RENDER_HEIGHT / 2) / scale_factor + center_y
    c = x + 1j * y
    z = np.zeros_like(c)
    div_time = np.zeros(z.shape, dtype=np.int32)

    for i in range(effective_max_iter):
        mask = np.abs(z) <= 2
        if not np.any(mask):
            div_time[div_time == 0] = effective_max_iter
            break
        z[mask] = z[mask] * z[mask] + c[mask]
        div_time[mask & (np.abs(z) > 2)] = i

    small_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
    rgb_array = np.zeros((RENDER_WIDTH, RENDER_HEIGHT, 3), dtype=np.uint8)
    normalized = (div_time * 255 // effective_max_iter).clip(0, 255).T
    palette_array = np.array(COLOR_PALETTE, dtype=np.uint8)

    for i in range(min(effective_max_iter, len(COLOR_PALETTE))):
        mask = normalized == i
        if np.any(mask):
            rgb_array[mask] = palette_array[i]

    mask_inside = (div_time >= effective_max_iter).T
    if np.any(mask_inside):
        rgb_array[mask_inside] = (0, 0, 0)

    pygame.surfarray.blit_array(small_surface, rgb_array)
    return pygame.transform.scale(small_surface, (WIDTH, HEIGHT))


# ==================== FIREWORKS ANIMATION ====================

class FireworkParticle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.03)
        self.gravity = 0.05

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + self.gravity)
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color[:3], (int(self.x), int(self.y)), max(1, int(self.life * 4)))


class Rocket:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 10
        self.target_y = random.randint(50, HEIGHT - 150)
        self.speed = random.uniform(3, 6)
        self.color = (random.randint(150, 255), random.randint(100, 200), random.randint(50, 150))
        self.trail = []
        self.exploded = False
        self.particles = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        if not self.exploded:
            self.y -= self.speed
            if self.y <= self.target_y:
                self.explode()
        else:
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

    def explode(self):
        self.exploded = True
        num_particles = random.randint(30, 50)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 6)
            velocity = (speed * math.cos(angle), speed * math.sin(angle))
            self.particles.append(FireworkParticle(self.x, self.y, self.color, velocity))

    def is_done(self):
        return self.exploded and len(self.particles) == 0

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * i / len(self.trail))
            color = list(self.color) + [alpha]
            pygame.draw.circle(surface, color[:3], (int(tx), int(ty)), max(1, 4 - i // 3))

        if not self.exploded:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)
            pygame.draw.circle(surface, (255, 255, 200), (int(self.x), int(self.y)), 2)
        else:
            for p in self.particles:
                p.draw(surface)


class FireworksManager:
    def __init__(self):
        self.rockets = []
        self.spawn_timer = 0
        self.spawn_rate = 40
        for _ in range(2):
            rocket = Rocket()
            rocket.y = random.randint(HEIGHT // 2, HEIGHT)
            self.rockets.append(rocket)

    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            self.rockets.append(Rocket())

        for rocket in self.rockets[:]:
            rocket.update()
            if rocket.is_done():
                self.rockets.remove(rocket)

    def draw(self, surface):
        for rocket in self.rockets:
            rocket.draw(surface)


# Background types
BACKGROUND_MANDELBROT = "mandelbrot"
BACKGROUND_FIREWORKS = "fireworks"
current_background = BACKGROUND_MANDELBROT

# ==================== GOTHIC UI ====================

# Font settings - Gothic/Roman style
font_style = pygame.font.SysFont("georgia", 35, bold=True)
score_font = pygame.font.SysFont("georgia", 22, bold=True)
small_font = pygame.font.SysFont("georgia", 18, bold=True)


def show_score(score, elapsed_time=0, apples_eaten=0):
    surface = pygame.display.get_surface()
    start_y = 80
    row_height = 45
    start_x = 100

    # Score
    value = score_font.render(f"SCORE: {score}", True, (255, 215, 0))
    score_rect = value.get_rect(topleft=(start_x, start_y))
    pygame.draw.rect(surface, (80, 60, 30), score_rect.inflate(24, 12), border_radius=3)
    pygame.draw.rect(surface, (180, 140, 60), score_rect.inflate(24, 12), width=2, border_radius=3)
    surface.blit(value, [start_x, start_y])

    # Time
    time_value = score_font.render(f"TIME: {int(elapsed_time)}s", True, (255, 215, 0))
    time_rect = time_value.get_rect(topleft=(start_x, start_y + row_height))
    pygame.draw.rect(surface, (80, 60, 30), time_rect.inflate(24, 12), border_radius=3)
    pygame.draw.rect(surface, (180, 140, 60), time_rect.inflate(24, 12), width=2, border_radius=3)
    surface.blit(time_value, [start_x, start_y + row_height])

    # Background name
    bg_color = (100, 255, 100) if current_background == BACKGROUND_MANDELBROT else (255, 100, 100)
    bg_name = "Mandelbrot" if current_background == BACKGROUND_MANDELBROT else "Fireworks"
    bg_surf = small_font.render(bg_name, True, bg_color)
    bg_rect = bg_surf.get_rect(topleft=(start_x, start_y + row_height * 2 + 10))
    surface.blit(bg_surf, bg_rect)

    # Progress: apples collected out of required (5)
    required = 5
    if current_background == BACKGROUND_MANDELBROT:
        progress_surf = small_font.render(f"{apples_eaten}/{required} apples", True, (150, 150, 150))
        progress_rect = progress_surf.get_rect(topleft=(start_x, start_y + row_height * 2 + 35))
        surface.blit(progress_surf, progress_rect)


def draw_roman_border(surface):
    """Draw an elaborate Roman/Greek-style decorative border with roses and gold."""
    gold = (218, 165, 32)
    gold_light = (255, 215, 0)
    gold_dark = (139, 90, 20)
    dark_brown = (60, 40, 15)
    rose_red = (180, 40, 60)
    rose_dark = (120, 20, 30)

    border_width = 30

    # Outer dark brown border
    pygame.draw.rect(surface, dark_brown, (0, 0, WIDTH, HEIGHT), border_width)

    # Gold inner frame
    pygame.draw.rect(surface, gold_dark, (border_width//2, border_width//2,
                                          WIDTH - border_width, HEIGHT - border_width), 4)
    pygame.draw.rect(surface, gold, (border_width//2 + 2, border_width//2 + 2,
                                     WIDTH - border_width - 4, HEIGHT - border_width - 4), 2)

    # Outer gold line
    pygame.draw.rect(surface, gold_light, (border_width - 6, border_width - 6,
                                           WIDTH - (border_width - 6) * 2,
                                           HEIGHT - (border_width - 6) * 2), 3)

    # Corner ornaments
    def draw_corner_ornament(x, y):
        pygame.draw.circle(surface, gold, (x, y), 12)
        pygame.draw.circle(surface, gold_dark, (x, y), 10, 2)
        pygame.draw.circle(surface, gold_light, (x, y), 6)

    draw_corner_ornament(border_width + 15, border_width + 15)
    draw_corner_ornament(WIDTH - border_width - 15, border_width + 15)
    draw_corner_ornament(border_width + 15, HEIGHT - border_width - 15)
    draw_corner_ornament(WIDTH - border_width - 15, HEIGHT - border_width - 15)

    # Roses at corners
    def draw_rose(x, y, scale=1.0):
        size = int(8 * scale)
        pygame.draw.circle(surface, rose_red, (x, y), size)
        pygame.draw.circle(surface, rose_dark, (x, y), size - 2, 2)
        pygame.draw.circle(surface, gold_light, (x, y), 2)

    rose_offset = border_width + 35
    draw_rose(rose_offset, rose_offset, 0.8)
    draw_rose(WIDTH - rose_offset, rose_offset, 0.8)
    draw_rose(rose_offset, HEIGHT - rose_offset, 0.8)
    draw_rose(WIDTH - rose_offset, HEIGHT - rose_offset, 0.8)

    # Decorative lines
    line_y = border_width + 15
    pygame.draw.line(surface, gold, (rose_offset + 20, line_y),
                     (WIDTH - rose_offset - 20, line_y), 2)
    pygame.draw.line(surface, gold, (rose_offset + 20, line_y + 8),
                     (WIDTH - rose_offset - 20, line_y + 8), 1)
    pygame.draw.line(surface, gold, (rose_offset + 20, HEIGHT - line_y),
                     (WIDTH - rose_offset - 20, HEIGHT - line_y), 2)
    pygame.draw.line(surface, gold, (rose_offset + 20, HEIGHT - line_y - 8),
                     (WIDTH - rose_offset - 20, HEIGHT - line_y - 8), 1)
    pygame.draw.line(surface, gold, (line_y, rose_offset + 20),
                     (line_y, HEIGHT - rose_offset - 20), 2)
    pygame.draw.line(surface, gold, (line_y + 8, rose_offset + 20),
                     (line_y + 8, HEIGHT - rose_offset - 20), 1)
    pygame.draw.line(surface, gold, (WIDTH - line_y, rose_offset + 20),
                     (WIDTH - line_y, HEIGHT - rose_offset - 20), 2)
    pygame.draw.line(surface, gold, (WIDTH - line_y - 8, rose_offset + 20),
                     (WIDTH - line_y - 8, HEIGHT - rose_offset - 20), 1)


def message(msg, color, y_displace=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(WIDTH / 2, HEIGHT / 2 + y_displace))
    shadow = font_style.render(msg, True, (30, 20, 10))
    pygame.display.get_surface().blit(shadow, (text_rect.x + 3, text_rect.y + 3))
    pygame.display.get_surface().blit(mesg, text_rect)


def draw_snake(block_size, snake_list):
    for i, x in enumerate(snake_list):
        color = SNAKE_HEAD_COLOR if i == len(snake_list) - 1 else SNAKE_COLOR
        pygame.draw.rect(pygame.display.get_surface(), color, [x[0], x[1], block_size, block_size], border_radius=4)

        if i == len(snake_list) - 1:
            pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (x[0] + 5, x[1] + 5), 2)
            pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (x[0] + 15, x[1] + 5), 2)


def game_loop():
    global current_background, mandelbrot_zoom, mandelbrot_surface

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
    apples_eaten = 0

    start_time = time.time()
    final_time = 0

    foodx = round(random.randrange(40, WIDTH - 40 - BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(40, HEIGHT - 40 - BLOCK_SIZE) / 20.0) * 20.0

    current_speed = SPEED

    frame_counter = 0
    fireworks_manager = FireworksManager()

    while not game_over:
        frame_counter += 1

        mandelbrot_zoom *= mandelbrot_zoom_speed

        if mandelbrot_zoom > 1e10:
            mandelbrot_zoom = 200.0

        if frame_counter % 8 == 0 or mandelbrot_surface is None:
            mandelbrot_surface = render_mandelbrot_background(
                mandelbrot_zoom, mandelbrot_center_x, mandelbrot_center_y
            )

        while game_close:
            if current_background == BACKGROUND_MANDELBROT:
                display.blit(mandelbrot_surface, (0, 0))
            else:
                display.fill((5, 5, 15))
                fireworks_manager.draw(display)

            message("GAME OVER", FOOD_COLOR, -50)
            message(f"Final Score: {length_of_snake - 1}", TEXT_COLOR, 10)
            message(f"Time: {int(final_time)}s", TEXT_COLOR, 40)
            message("Press C-Play Again or Q-Quit", SNAKE_COLOR, 80)

            show_score(length_of_snake - 1, final_time, apples_eaten)
            draw_roman_border(display)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        mandelbrot_zoom = 200.0
                        current_background = BACKGROUND_MANDELBROT
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

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            final_time = time.time() - start_time
            game_close = True

        x1 += x1_change
        y1 += y1_change

        if current_background == BACKGROUND_MANDELBROT:
            display.blit(mandelbrot_surface, (0, 0))
        else:
            display.fill((5, 5, 15))
            fireworks_manager.update()
            fireworks_manager.draw(display)

        pygame.draw.circle(display, FOOD_COLOR, (int(foodx + BLOCK_SIZE/2), int(foody + BLOCK_SIZE/2)), 8)

        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                final_time = time.time() - start_time
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        elapsed_time = time.time() - start_time
        show_score(length_of_snake - 1, elapsed_time, apples_eaten)
        draw_roman_border(display)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(40, WIDTH - 40 - BLOCK_SIZE) / 20.0) * 20.0
            foody = round(random.randrange(40, HEIGHT - 40 - BLOCK_SIZE) / 20.0) * 20.0
            length_of_snake += 1
            apples_eaten += 1

            if apples_eaten >= 5 and current_background == BACKGROUND_MANDELBROT:
                current_background = BACKGROUND_FIREWORKS
                fireworks_manager = FireworksManager()

            if length_of_snake % 5 == 0:
                current_speed += 1

        clock.tick(current_speed)

    pygame.quit()
    quit()


if __name__ == "__main__":
    game_loop()
