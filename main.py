
import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 302
WINDOW_HEIGHT = 600
GAME_WIDTH = 250
INFO_WIDTH = 52
SQUARE_SIZE = 60
SECTORS = 4
SECTOR_WIDTH = GAME_WIDTH // SECTORS
CLICK_SENSITIVITY = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
BACKGROUND_COLOR = WHITE

BASE_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
    (0, 0, 128), (128, 128, 0)
]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Color Squares")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 29)  # Reduced font for time
        self.small_font = pygame.font.Font(None, 18)  # Reduced font for buttons
        self.level_font = pygame.font.Font(None, 24)  # Larger font for level numbers
        self.green_mode = 0  # 0 - off, 1-3 levels
        self.blue_mode = 0   # 0 - off, 1-3 levels
        self.purple_mode = 0 # 0 - off, 1-3 levels
        self.pink_mode = 0   # 0 - off, 1-3 levels
        self.reset_game()

    def create_square(self):
        if self.is_delayed:
            return None
            
        sector = random.randint(0, SECTORS - 1)
        x = sector * SECTOR_WIDTH
        color = random.choice(self.get_current_colors())
        return {'x': x, 'y': 0, 'color': color, 'sector': sector}

    def get_current_colors(self):
        def get_shades(base_color, mode):
            if mode == 1:
                brightnesses = [1.0, 0.8, 0.6, 0.4]
            elif mode == 2:
                brightnesses = [1.0, 0.9, 0.8, 0.7]
            else:  # level 3
                brightnesses = [1.0, 0.95, 0.8, 0.85]
            return [tuple(int(c * b) for c in base_color) for b in brightnesses]

        if self.green_mode > 0:
            return get_shades((0, 255, 0), self.green_mode)
        elif self.blue_mode > 0:
            return get_shades((0, 0, 255), self.blue_mode)
        elif self.purple_mode > 0:
            return get_shades((128, 0, 128), self.purple_mode)
        elif self.pink_mode > 0:
            return get_shades((255, 192, 203), self.pink_mode)
        if self.sensitivity > 0:
            base_color = random.choice(BASE_COLORS[:10])
            shades = []
            for i in range(self.color_count):
                factor = 0.5 + (i / self.color_count)
                shade = tuple(int(c * factor) for c in base_color)
                shades.append(shade)
            return shades
        return BASE_COLORS[:self.color_count]

    def reset_game(self):
        self.game_over = False
        self.dragging = False
        self.squares = []
        self.current_square = None
        self.start_time = None
        self.elapsed_time = 0
        self.show_time = True
        self.last_blink = time.time()
        self.color_count = 4
        self.speed_level = 15
        self.sensitivity = 0
        self.fall_speed = 30 * (1 + (self.speed_level - 1) * 0.3)  # mm per second
        self.delay_start = None
        self.is_delayed = False

    def draw_info_panel(self):
        # Draw info panel background
        pygame.draw.rect(self.screen, LIGHT_BLUE, (GAME_WIDTH, 0, INFO_WIDTH, WINDOW_HEIGHT))
        
        # Draw time
        if self.show_time:
            time_text = self.font.render(f"{int(self.elapsed_time)}", True, BLACK)
            self.screen.blit(time_text, (GAME_WIDTH + 5, 10))

        # Color icon (circle with sectors)
        center = (GAME_WIDTH + INFO_WIDTH//2, 160)
        radius = 15
        colors = self.get_current_colors()[:4]
        for i, color in enumerate(colors):
            start_angle = i * 90
            pygame.draw.arc(self.screen, color, (center[0]-radius, center[1]-radius, radius*2, radius*2), 
                          start_angle * 3.14/180, (start_angle + 90) * 3.14/180, radius)

        # Draw buttons
        button_y = 200
        for text, color in [
            (f"C:{self.color_count}", WHITE),
            (f"V:{self.speed_level}", WHITE),
            ("Start", (255, 0, 0)),  # Red color for Start
            ("Stop", WHITE),
            (f"{self.green_mode if self.green_mode > 0 else '-'}", (0, 255, 0)),  # Green button
            (f"{self.blue_mode if self.blue_mode > 0 else '-'}", (0, 0, 255)),    # Blue button
            (f"{self.purple_mode if self.purple_mode > 0 else '-'}", (128, 0, 128)), # Purple button
            (f"{self.pink_mode if self.pink_mode > 0 else '-'}", (255, 192, 203))  # Pink button
        ]:
            button_rect = pygame.draw.rect(self.screen, color, 
                                         (GAME_WIDTH + 2, button_y, INFO_WIDTH - 4, 30))
            font_to_use = self.level_font if text.isdigit() or text == '-' else self.small_font
            text_surface = font_to_use.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
            button_y += 40

    def handle_click(self, pos):
        x, y = pos
        if x >= GAME_WIDTH:  # Clicked in info panel
            button_y = 200
            for action in ["color", "speed", "start", "stop", "green", "blue", "purple", "pink"]:
                button_rect = pygame.Rect(GAME_WIDTH + 2, button_y, INFO_WIDTH - 4, 30)
                if button_rect.collidepoint(pos):
                    self.handle_button(action)
                button_y += 40
        elif self.current_square and not self.dragging:
            square_center = self.current_square['x'] + SQUARE_SIZE // 2
            if x > square_center:
                self.move_square(1)
            elif x < square_center:
                self.move_square(-1)

    def handle_button(self, action):
        if action == "color":
            self.color_count = (self.color_count % 15) + 1 if self.color_count < 15 else 4
        elif action == "speed":
            self.speed_level = self.speed_level - 1 if self.speed_level > 1 else 15
            self.fall_speed = 30 * (1 + (self.speed_level - 1) * 0.3)
        elif action == "sensitivity":
            self.sensitivity = (self.sensitivity + 1) % 6
        elif action == "green":
            self.green_mode = (self.green_mode + 1) % 4
            self.blue_mode = 0
            self.purple_mode = 0
            self.pink_mode = 0
        elif action == "blue":
            self.blue_mode = (self.blue_mode + 1) % 4
            self.green_mode = 0
            self.purple_mode = 0
            self.pink_mode = 0
        elif action == "purple":
            self.purple_mode = (self.purple_mode + 1) % 4
            self.green_mode = 0
            self.blue_mode = 0
            self.pink_mode = 0
        elif action == "pink":
            self.pink_mode = (self.pink_mode + 1) % 4
            self.green_mode = 0
            self.blue_mode = 0
            self.purple_mode = 0
        elif action == "start":
            if self.game_over:
                self.reset_game()
            if not self.start_time:
                self.start_time = time.time()
                self.current_square = self.create_square()
        elif action == "stop":
            self.reset_game()

    def move_square(self, direction):
        if self.current_square:
            new_x = self.current_square['x'] + direction * SECTOR_WIDTH
            if 0 <= new_x <= GAME_WIDTH - SQUARE_SIZE:
                self.current_square['x'] = new_x
                self.current_square['sector'] = new_x // SECTOR_WIDTH

    def update(self):
        if not self.start_time or self.game_over:
            return

        current_time = time.time()
        
        if self.game_over:
            if current_time - self.last_blink >= 0.5:
                self.show_time = not self.show_time
                self.last_blink = current_time
            return

        self.elapsed_time = current_time - self.start_time

        if not self.current_square:
            self.current_square = self.create_square()
            self.is_delayed = True
            self.delay_start = current_time
            return

        if self.is_delayed:
            if current_time - self.delay_start >= 2:
                self.is_delayed = False
            return

        movement = self.fall_speed * self.clock.get_time() / 1000.0
        self.current_square['y'] += movement

        # Check collision
        if self.current_square['y'] + SQUARE_SIZE >= WINDOW_HEIGHT:
            self.squares.append(self.current_square)
            self.current_square = None
        else:
            for square in self.squares:
                if (abs(square['x'] - self.current_square['x']) < SQUARE_SIZE and
                    square['y'] - (self.current_square['y'] + SQUARE_SIZE) <= 0):
                    if square['color'] == self.current_square['color']:
                        self.squares.remove(square)
                    else:
                        self.squares.append(self.current_square)
                    self.current_square = None
                    break

        # Check game over
        if any(len([s for s in self.squares if s['x'] == x * SECTOR_WIDTH]) >= 9 
               for x in range(SECTORS)):
            self.game_over = True

    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw squares
        for square in self.squares:
            pygame.draw.rect(self.screen, square['color'], 
                           (square['x'], square['y'], SQUARE_SIZE, SQUARE_SIZE))

        if self.current_square:
            pygame.draw.rect(self.screen, self.current_square['color'],
                           (self.current_square['x'], self.current_square['y'], 
                            SQUARE_SIZE, SQUARE_SIZE))

        self.draw_info_panel()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
