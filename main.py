import pygame
import random
import math
import time

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 900  # Expanded height by 100 pixels
GAME_HEIGHT = 800  # Original game area height
TIMER_AREA_HEIGHT = 100  # New area for timer
ROWS = 4
COLS = 4

RECT_HEIGHT = GAME_HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)
TIMER_BG_COLOR = (250, 248, 239)
MENU_BG_COLOR = (250, 248, 239)
SELECTED_COLOR = (237, 224, 200)
BUTTON_COLOR = (143, 122, 102)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
TIMER_FONT = pygame.font.SysFont("arial", 36, bold=True)
TITLE_FONT = pygame.font.SysFont("comicsans", 100, bold=True)
MENU_FONT = pygame.font.SysFont("arial", 40, bold=True)
MOVE_VEL = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT + TIMER_AREA_HEIGHT  # Offset by timer area

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil((self.y - TIMER_AREA_HEIGHT) / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor((self.y - TIMER_AREA_HEIGHT) / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_start_screen(window, selected_option):
    window.fill(MENU_BG_COLOR)
    
    # Draw title
    title_text = TITLE_FONT.render("2048", True, FONT_COLOR)
    title_x = (WIDTH - title_text.get_width()) // 2
    window.blit(title_text, (title_x, 150))
    
    # Menu options
    options = [
        "1. Start a Normal Game",
        "2. Start a Timed Mode",
        "3. Exit Game"
    ]
    
    for i, option in enumerate(options):
        color = BUTTON_COLOR if i == selected_option else FONT_COLOR
        bg_color = SELECTED_COLOR if i == selected_option else None
        
        text = MENU_FONT.render(option, True, color)
        text_x = (WIDTH - text.get_width()) // 2
        text_y = 350 + i * 80
        
        if bg_color:
            padding = 20
            pygame.draw.rect(window, bg_color, 
                           (text_x - padding, text_y - padding//2, 
                            text.get_width() + padding*2, text.get_height() + padding))
        
        window.blit(text, (text_x, text_y))
    
    # Instructions
    instructions = "Use UP/DOWN arrows to navigate, ENTER to select"
    inst_text = pygame.font.SysFont("arial", 24).render(instructions, True, FONT_COLOR)
    inst_x = (WIDTH - inst_text.get_width()) // 2
    window.blit(inst_text, (inst_x, HEIGHT - 100))
    
    pygame.display.update()


def draw_grid(window):
    # Draw horizontal lines
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT + TIMER_AREA_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    # Draw vertical lines
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, TIMER_AREA_HEIGHT), (x, HEIGHT), OUTLINE_THICKNESS)

    # Draw game area border
    pygame.draw.rect(window, OUTLINE_COLOR, (0, TIMER_AREA_HEIGHT, WIDTH, GAME_HEIGHT), OUTLINE_THICKNESS)


def draw_timer(window, start_time, game_won, game_mode, time_limit=None):
    # Fill timer area background
    pygame.draw.rect(window, TIMER_BG_COLOR, (0, 0, WIDTH, TIMER_AREA_HEIGHT))
    
    if game_won:
        if game_mode == "timed":
            elapsed_time = time.time() - start_time
            remaining_time = max(0, time_limit - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            timer_text = f"Winner! Time left: {minutes:02d}:{seconds:02d}"
        else:
            timer_text = "Winner!"
        color = (46, 125, 50)  # Green color for winner
    elif game_mode == "timed":
        elapsed_time = time.time() - start_time
        remaining_time = max(0, time_limit - elapsed_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        if remaining_time <= 0:
            timer_text = "Time's Up!"
            color = (211, 47, 47)  # Red color for time up
        else:
            timer_text = f"Time: {minutes:02d}:{seconds:02d}"
            color = FONT_COLOR
    else:
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        color = FONT_COLOR
    
    text_surface = TIMER_FONT.render(timer_text, True, color)
    window.blit(text_surface, (20, 30))  # Position at top-left with some padding
    
    # Show mode in top right
    mode_text = "Timed Mode" if game_mode == "timed" else "Normal Mode"
    mode_surface = pygame.font.SysFont("arial", 24).render(mode_text, True, FONT_COLOR)
    window.blit(mode_surface, (WIDTH - mode_surface.get_width() - 20, 35))
    
    # Draw separator line
    pygame.draw.line(window, OUTLINE_COLOR, (0, TIMER_AREA_HEIGHT), (WIDTH, TIMER_AREA_HEIGHT), 3)


def draw(window, tiles, start_time, game_won, game_mode, time_limit=None):
    window.fill(BACKGROUND_COLOR)
    
    # Draw timer area
    draw_timer(window, start_time, game_won, game_mode, time_limit)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    pygame.display.update()


def check_for_2048(tiles):
    """Check if any tile has reached 2048"""
    for tile in tiles.values():
        if tile.value >= 2048:
            return True
    return False


def check_time_up(start_time, time_limit):
    """Check if time limit has been reached"""
    elapsed_time = time.time() - start_time
    return elapsed_time >= time_limit


def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


def move_tiles(window, tiles, clock, direction, start_time, game_won, game_mode, time_limit=None):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles, start_time, game_won, game_mode, time_limit)

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"

    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def update_tiles(window, tiles, sorted_tiles, start_time, game_won, game_mode, time_limit=None):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles, start_time, game_won, game_mode, time_limit)


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles


def start_screen():
    clock = pygame.time.Clock()
    selected_option = 0
    
    while True:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "normal"
                    elif selected_option == 1:
                        return "timed"
                    elif selected_option == 2:
                        return "exit"
        
        draw_start_screen(WINDOW, selected_option)


def game_loop(window, game_mode):
    clock = pygame.time.Clock()
    run = True
    start_time = time.time()
    game_won = False
    time_limit = 90 if game_mode == "timed" else None
    game_over = False

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)
        
        # Check for 2048 tile
        if not game_won and check_for_2048(tiles):
            game_won = True
        
        # Check for time limit in timed mode
        if game_mode == "timed" and not game_won and not game_over:
            if check_time_up(start_time, time_limit):
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart the game
                    tiles = generate_tiles()
                    start_time = time.time()
                    game_won = False
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    # Return to menu
                    return "menu"
                elif not game_won and not game_over:
                    if event.key == pygame.K_LEFT:
                        move_tiles(window, tiles, clock, "left", start_time, game_won, game_mode, time_limit)
                    elif event.key == pygame.K_RIGHT:
                        move_tiles(window, tiles, clock, "right", start_time, game_won, game_mode, time_limit)
                    elif event.key == pygame.K_UP:
                        move_tiles(window, tiles, clock, "up", start_time, game_won, game_mode, time_limit)
                    elif event.key == pygame.K_DOWN:
                        move_tiles(window, tiles, clock, "down", start_time, game_won, game_mode, time_limit)

        draw(window, tiles, start_time, game_won, game_mode, time_limit)

    return "exit"


def main():
    while True:
        choice = start_screen()
        
        if choice == "exit":
            break
        elif choice == "normal":
            result = game_loop(WINDOW, "normal")
            if result == "exit":
                break
        elif choice == "timed":
            result = game_loop(WINDOW, "timed")
            if result == "exit":
                break
    
    pygame.quit()


if __name__ == "__main__":
    main()
