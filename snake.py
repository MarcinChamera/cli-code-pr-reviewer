import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
SPEED = 15

# Colors (Modern Palette)
BG_COLOR = (15, 15, 15)  # Dark Gray/Black
SNAKE_COLOR = (46, 204, 113)  # Emerald Green
SNAKE_HEAD_COLOR = (39, 174, 96)  # Darker Green
FOOD_COLOR = (231, 76, 60)  # Alizarin Red
TEXT_COLOR = (236, 240, 241)  # Clouds/White
GLOW_COLOR = (46, 204, 113, 100) # Semi-transparent green

# Font settings
font_style = pygame.font.SysFont("outfit", 35)
score_font = pygame.font.SysFont("outfit", 25)

def show_score(score, elapsed_time=0):
    value = score_font.render(f"SCORE: {score}", True, SNAKE_COLOR)
    # Background for score
    score_rect = value.get_rect(topleft=(20, 20))
    pygame.draw.rect(pygame.display.get_surface(), (30, 30, 30), score_rect.inflate(20, 10), border_radius=5)
    pygame.display.get_surface().blit(value, [20, 20])

    # Display timer below score
    time_value = score_font.render(f"TIME: {elapsed_time}s", True, SNAKE_COLOR)
    pygame.draw.rect(pygame.display.get_surface(), (30, 30, 30), time_value.get_rect(topleft=(20, 50)).inflate(20, 10), border_radius=5)
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

    # Track start time for timer
    start_time = time.time()

    # Place food
    foodx = round(random.randrange(40, WIDTH - 40 - BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(40, HEIGHT - 40 - BLOCK_SIZE) / 20.0) * 20.0

    current_speed = SPEED

    while not game_over:

        while game_close:
            display.fill(BG_COLOR)
            message("GAME OVER", FOOD_COLOR, -50)
            message(f"Final Score: {length_of_snake - 1}", TEXT_COLOR, 10)
            message("Press C-Play Again or Q-Quit", SNAKE_COLOR, 70)

            elapsed_time = int(time.time() - start_time)
            show_score(length_of_snake - 1, elapsed_time)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
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
            game_close = True
        
        x1 += x1_change
        y1 += y1_change
        
        display.fill(BG_COLOR)
        
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
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        elapsed_time = int(time.time() - start_time)
        show_score(length_of_snake - 1, elapsed_time)

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
