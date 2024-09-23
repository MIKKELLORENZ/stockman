import pygame
import sys,os
import random
import numpy as np
import time 
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Import variables from variables.py
from variables import fictional_stocks, news_dict, graph_time_scales, cheesy_slogans
from funcs import get_day_suffix, catmull_rom_points, get_catmull_rom_chain
from sounds import menu_music, game_music, sell_sound, buy_sound, date_increment_sound, quantity_change_sound, account_beep, day_ending_tick, small_click_sound


# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Updated Color Scheme
WHITE = (236, 240, 241)
GRAY = (149, 165, 166)
LIGHT_GRAY = (189, 195, 199)
DARK_GRAY = (44, 62, 80)
BLACK = (18, 18, 18)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
DARK_RED = (200, 46, 30)
BLUE = (52, 152, 219)
ORANGE = (243, 156, 18)
PAPER_YELLOW = (241, 196, 15)

# Paths to resources
SRC_PATH = os.path.dirname(os.path.abspath(__file__))

# Fonts
FONT_TINY = pygame.font.SysFont('Veranda', 20)
FONT_SMALL = pygame.font.SysFont('Veranda', 26)
FONT_MEDIUM = pygame.font.SysFont('Veranda', 36)
FONT_LARGE = pygame.font.SysFont('Veranda', 70)

# Calendar Fonts
CALENDER_FONT = pygame.font.SysFont("LCD2 Normal", 20) 
NEWS_FONT = pygame.font.SysFont("LCD Normal", 20) 
SLOGAN_FONT =  pygame.font.SysFont("VCR OSD Mono", 20) 
# Money pouring speed
money_pouring_speed = 0.05  # seconds between each increment


# Reformat cheesy slogans
random.shuffle(cheesy_slogans)
cheesy_slogans = " ".join(cheesy_slogans)

# Load background image
try:
    background_image = pygame.image.load("wallpaper.webp")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_wallpaper = pygame.image.load("menu_wallpaper.png")
    menu_wallpaper = pygame.transform.scale(menu_wallpaper, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background_image = None

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Game clock
clock = pygame.time.Clock()

# Game Variables
start_year = 1985
current_year = start_year
current_month_index = 7  # July
current_day_in_month = 1
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_days = [31, 28, 31, 30, 31, 30,
              31, 31, 30, 31, 30, 31]

current_day = 1
days_in_year = 365
day_progress = 0
start_capital = 2000.0
account_fee = 30
capital = start_capital
broker_fee = 5.0
stocks = []
player_portfolio = {}
market_index = []
news_list = list(news_dict.keys())
current_news = ""
last_news = ""
sentiment_effects = {}
day_ending_sound_played = False
total_number_of_stocks = 0
for k,v in fictional_stocks.items():
    total_number_of_stocks += len(v)

net_worth_history = []
market_index_history = []
selected_time_scale = "1 week"
time_scale_options = list(graph_time_scales.keys())

# Define seasonal trends
monthly_market_effects = {
    0: 0.1,   # January effect
    8: -0.1,  # September underperform
    9: -0.1,  # October volatility
    10: 0.1,  # November boost
    11: 0.1,  # December rally
}

industry_monthly_effects = {
    'Retail': {10: 0.2, 11: 0.2},
    'Agriculture': {5: 0.2, 6: 0.2},
    'Energy': {0: 0.2, 1: 0.2, 6: 0.2, 7: 0.2},
    'Hospitality': {5: 0.2, 6: 0.5, 7: 0.2},
    'Fashion': {1: 0.2, 8: 0.2},
    'Entertainment': {5: 0.2, 6: 0.2, 11: 0.2},
    'Tech': {8: 0.2, 9: 0.2},
    'Automotive': {8: 0.2, 9: 0.2},
    'Education': {7: 0.2, 8: 0.2},
    'Real Estate': {3: 0.2, 4: 0.2, 5: 0.2},
    'Transportation': {5: 0.2, 6: 0.2, 11: 0.2},
    'Luxury Goods': {10: 0.2, 11: 0.2},
    'Consumer Goods': {10: 0.2, 11: 0.2},
    'E-commerce': {10: 0.2, 11: 0.2},
    'Pharmaceutical': {0: 0.2, 1: 0.2, 2: 0.2},
    'Gaming': {10: 0.2, 11: 0.2},
    'Media': {5: 0.2, 6: 0.2},
    'Insurance': {11: 0.2},
    'Finance': {11: 0.2},
}

def get_seasonal_effect(category, month_index):
    month_effect = 0
    industry_effect = 0

    if random.uniform(0,1) < 0.05:
        month_effect = monthly_market_effects.get(month_index, 0)

    if random.uniform(0,1) < 0.10:
        industry_effect = industry_monthly_effects.get(category, {}).get(month_index, 0)
    total_seasonal_effect = month_effect + industry_effect
    return total_seasonal_effect


def draw_background_gradient(screen, color, height):
    """Draw a gradient that starts from the bottom of the screen, becoming darker as it goes up."""
    gradient_surface = pygame.Surface((SCREEN_WIDTH, height), pygame.SRCALPHA)  # Create a surface with alpha channel

    # Gradient colors (dark navy blue / gray, starting from transparent at the bottom)
    bottom_color = (0, 0, 0, 0)  # Fully transparent at the bottom
    top_color = color  # Dark navy blue/gray at the top

    for y in range(height):
        ratio = y / height  # As y increases, the color becomes less transparent
        r = int(bottom_color[0] * (1 - ratio) + top_color[0] * ratio)
        g = int(bottom_color[1] * (1 - ratio) + top_color[1] * ratio)
        b = int(bottom_color[2] * (1 - ratio) + top_color[2] * ratio)
        a = int(255 * ratio)  # Alpha increases as it goes up (more opaque as it rises)
        pygame.draw.line(gradient_surface, (r, g, b, a), (0, y), (SCREEN_WIDTH, y))

    screen.blit(gradient_surface, (0, SCREEN_HEIGHT - height))  # Draw the gradient at the bottom of the screen



def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draw a vertical gradient from top_color to bottom_color on the given surface."""
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = top_color[0] * (1 - ratio) + bottom_color[0] * ratio
        g = top_color[1] * (1 - ratio) + bottom_color[1] * ratio
        b = top_color[2] * (1 - ratio) + bottom_color[2] * ratio
        pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (surface.get_width(), y))

class Stock:
    def __init__(self, name, category, price):
        self.name = name
        self.category = category
        self.price = price
        self.display_price = price  # For displaying in the stock list
        self.history = [(0, price)]
        self.dividend_yield = random.uniform(0, 5)  # in percentage

    def update_price(self, current_time, current_month_index):
        sentiment = 0
        # Get market sentiment
        market_sentiment = sentiment_effects.get(('Market', ''), (0, 0))[0]
        sentiment += market_sentiment
        # Get category sentiment
        category_sentiment = sentiment_effects.get(('Category', self.category), (0, 0))[0]
        sentiment += category_sentiment
        # Get stock sentiment
        stock_sentiment = sentiment_effects.get(('Stock', self.name), (0, 0))[0]
        sentiment += stock_sentiment

        change = random.uniform(-0.2, 0.2) + 0.0020 + sentiment * 0.1

        # Apply seasonal effects
        seasonal_effect = get_seasonal_effect(self.category, current_month_index)
        change += seasonal_effect

        self.price += change
        if self.price < 0.1:
            self.price = 0.1
        self.history.append((current_time, self.price))

    def update_display_price(self):
        self.display_price = self.price

class Scrollbar:
    def __init__(self, track_rect, surface_pos, content_height, visible_height, scroll_offset):
        self.track_rect = track_rect
        self.surface_pos = surface_pos
        self.content_height = content_height
        self.visible_height = visible_height
        self.scroll_offset = scroll_offset

        self.scroll_bar_width = 15
        self.scroll_bar_min_height = 20

        self.scroll_bar_rect = self.calculate_scroll_bar_rect()
        self.dragging = False
        self.drag_start_y = 0
        self.scroll_start_offset = 0

    def calculate_scroll_bar_rect(self):
        if self.content_height <= self.visible_height:
            return None

        visible_ratio = self.visible_height / self.content_height
        scroll_bar_height = max(self.scroll_bar_min_height, self.track_rect.height * visible_ratio)

        scroll_ratio = -self.scroll_offset / (self.content_height - self.visible_height)
        scroll_ratio = max(0, min(1, scroll_ratio))

        scroll_bar_y = self.track_rect.top + scroll_ratio * (self.track_rect.height - scroll_bar_height)

        return pygame.Rect(
            self.track_rect.right - self.scroll_bar_width + self.surface_pos[0],
            self.track_rect.top + scroll_ratio * (self.track_rect.height - scroll_bar_height) + self.surface_pos[1],
            self.scroll_bar_width,
            scroll_bar_height
        )

    def handle_event(self, event):
        if self.scroll_bar_rect is None:
            return

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.scroll_bar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_start_y = event.pos[1]
                    self.scroll_start_offset = self.scroll_offset
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                dy = event.pos[1] - self.drag_start_y
                track_movable_height = self.track_rect.height - self.scroll_bar_rect.height
                content_scrollable_height = self.content_height - self.visible_height
                if content_scrollable_height == 0:
                    return
                scroll_ratio = dy / track_movable_height
                self.scroll_offset = self.scroll_start_offset - scroll_ratio * content_scrollable_height
                self.scroll_offset = min(0, max(-content_scrollable_height, self.scroll_offset))

    def update(self, content_height, visible_height, scroll_offset):
        self.content_height = content_height
        self.visible_height = visible_height
        self.scroll_offset = scroll_offset
        self.scroll_bar_rect = self.calculate_scroll_bar_rect()

    def draw(self, surface):
        if self.scroll_bar_rect:
            local_rect = pygame.Rect(
                self.scroll_bar_rect.x - self.surface_pos[0],
                self.scroll_bar_rect.y - self.surface_pos[1],
                self.scroll_bar_rect.width,
                self.scroll_bar_rect.height
            )
            pygame.draw.rect(surface, GRAY, local_rect)

# Initialize stocks
stock_list = []

for category, stock_names in fictional_stocks.items():
    for name in stock_names:
        price = np.random.lognormal(mean=np.log(40), sigma=0.6)

        stock_list.append(Stock(name, category, price))
stocks = sorted(stock_list, key=lambda s: s.name)

# Helper functions
def get_graph_data(history, total_time, time_scale):
    if time_scale == "history" or graph_time_scales[time_scale] is None:
        return history
    else:
        time_duration = graph_time_scales[time_scale]
        start_time = total_time - time_duration
        if start_time < 0:
            start_time = 0
        data = [(t, v) for (t, v) in history if t >= start_time]
        return data

def draw_graph(surface, rect, data, color, min_reference=None, split_color=False):
    times = [t for (t, v) in data]
    values = [v for (t, v) in data]
    if len(times) < 2:
        return
    min_time = min(times)
    max_time = max(times)
    min_value = min(values)
    max_value = max(values)
    time_span = max_time - min_time
    value_span = max_value - min_value
    if time_span == 0:
        time_span = 1
    if value_span == 0:
        value_span = 1

    # Define margins as a percentage of the rect dimensions
    margin_x = 0.05 * rect.width  # 5% margin on x-axis
    margin_y = 0.05 * rect.height  # 5% margin on y-axis

    points = []
    for t, v in data:
        x = rect.left + margin_x + ((t - min_time) / time_span) * (rect.width - 2 * margin_x)
        y = rect.bottom - margin_y - ((v - min_value) / value_span) * (rect.height - 2 * margin_y)
        x = max(rect.left + margin_x, min(rect.right - margin_x, x))
        y = max(rect.top + margin_y, min(rect.bottom - margin_y, y))
        points.append((x, y))
    num_labels = 4
    label_values = [min_value + i * (max_value - min_value) / (num_labels - 1) for i in range(num_labels)]
    for label_value in label_values:
        y = rect.bottom - margin_y - ((label_value - min_value) / value_span) * (rect.height - 2 * margin_y)
        y = max(rect.top + margin_y, min(rect.bottom - margin_y, y))
        label_text = FONT_TINY.render(f"${label_value:.1f}", True, WHITE)
        surface.blit(label_text, (rect.left + 5, y - label_text.get_height() / 2))
        pygame.draw.line(surface, GRAY, (rect.left + margin_x, y), (rect.right - margin_x, y), 1)
    if split_color and min_reference is not None:
        for i in range(len(points) - 1):
            v1 = data[i][1]
            v2 = data[i+1][1]
            p1 = points[i]
            p2 = points[i+1]
            if v1 >= min_reference and v2 >= min_reference:
                segment_color = GREEN
            elif v1 < min_reference and v2 < min_reference:
                segment_color = RED
            else:
                t_cross = (min_reference - v1) / (v2 - v1) if v2 != v1 else 0
                t_cross = max(0, min(1, t_cross))
                x_int = p1[0] + t_cross * (p2[0] - p1[0])
                y_int = p1[1] + t_cross * (p2[1] - p1[1])
                x_int = max(rect.left + margin_x, min(rect.right - margin_x, x_int))
                y_int = max(rect.top + margin_y, min(rect.bottom - margin_y, y_int))
                if v1 < min_reference:
                    pygame.draw.line(surface, RED, p1, (x_int, y_int), 2)
                    pygame.draw.line(surface, GREEN, (x_int, y_int), p2, 2)
                else:
                    pygame.draw.line(surface, GREEN, p1, (x_int, y_int), 2)
                    pygame.draw.line(surface, RED, (x_int, y_int), p2, 2)
                continue
            pygame.draw.line(surface, segment_color, p1, p2, 2)
    else:
        if len(points) >=4:
            extended_points = [points[0]] + points + [points[-1]]
            spline_points = get_catmull_rom_chain(extended_points, 10)
            clipped_spline_points = [(max(rect.left + margin_x, min(rect.right - margin_x, x)), max(rect.top + margin_y, min(rect.bottom - margin_y, y))) for x, y in spline_points]
            pygame.draw.lines(surface, color, False, clipped_spline_points, 2)
        else:
            pygame.draw.lines(surface, color, False, points, 2)


def main_menu():
    menu_music.play(-1)

    # Added: Slogan management
    class Slogan:
        def __init__(self, text, font, color, y, speed):
            self.text = text
            self.font = font
            self.color = color
            self.y = y
            self.speed = speed
            self.x = SCREEN_WIDTH
            self.rendered_text = self.font.render(self.text, True, self.color)
            self.width = self.rendered_text.get_width()
        
        def update(self, dt):
            self.x -= self.speed * dt
        
        def draw(self, surface):
            surface.blit(self.rendered_text, (self.x, self.y))

    slogans = []
    slogan_spawn_timer = 90 + 60 + 70 + 90
    slogan_spawn_interval = 90  + 60 + 70 + 90# seconds between spawns
    slogan_speed = 90  # pixels per second
    slogan_font = SLOGAN_FONT  # You can choose a different font size if desired
    slogan_color = DARK_GRAY
    slogan_y = 664

    while True:
        screen.fill(BLACK)
        if background_image:
            screen.blit(menu_wallpaper, (0, 0))
        else:
            draw_vertical_gradient(screen, DARK_GRAY, BLACK)

        # Update and draw slogans
        dt = clock.tick(60) / 1000  # Delta time in seconds
        slogan_spawn_timer += dt

        if slogan_spawn_timer >= slogan_spawn_interval:
            slogan_text = cheesy_slogans
            slogans.append(Slogan(slogan_text, slogan_font, slogan_color, slogan_y, slogan_speed))
            slogan_spawn_timer = 0

        for slogan in slogans[:]:
            slogan.update(dt)
            slogan.draw(screen)
            if slogan.x + slogan.width < 0:
                slogans.remove(slogan)

        # Draw the title, start button, exit button etc.
        #title_text = FONT_LARGE.render("Stock Man", True, WHITE)
        start_text = FONT_MEDIUM.render("Start", True, WHITE)
        exit_text = FONT_MEDIUM.render("Exit", True, WHITE)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_clicked = True

        # Start Button
        start_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2, 200, 50)
        if start_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, DARK_RED, start_rect)
            if mouse_clicked:
                menu_music.stop()
                game_loop()
        else:
            pygame.draw.rect(screen, RED, start_rect)
        screen.blit(start_text, (SCREEN_WIDTH/2 - start_text.get_width()/2, SCREEN_HEIGHT/2 + 10))

       # screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/4))

        pygame.display.flip()
        clock.tick(60)

def game_loop():
    global current_day, day_progress, net_worth, capital, day_ending_sound_played, selected_time_scale, sentiment_effects, current_year, current_month_index, current_day_in_month
    selected_stock = None
    buy_quantity = 1
    sell_quantity = 1
    game_music.play(-1)

    day_ending_sound_played = False

    stock_list_rect = pygame.Rect(10, 50, 250, SCREEN_HEIGHT - 200)
    stock_list_surface = pygame.Surface((stock_list_rect.width, stock_list_rect.height))
    stock_list_surface.fill(DARK_GRAY)

    portfolio_rect = pygame.Rect(SCREEN_WIDTH - 320, 50, 300, SCREEN_HEIGHT - 200)
    portfolio_surface = pygame.Surface((portfolio_rect.width, portfolio_rect.height))
    portfolio_surface.fill(DARK_GRAY)

    # Move buttons up by 50 pixels
    button_y = SCREEN_HEIGHT - 150 + 100 - 50  # Adjusted Y-position
    # Ensure buttons stay within the screen
    if button_y + 40 > SCREEN_HEIGHT - 10:  # 10 pixels padding
        button_y = SCREEN_HEIGHT - 40 - 10  # Adjust to fit

    # Buy Button and Quantity Changers
    buy_button_rect = pygame.Rect(stock_list_rect.left + 10, button_y, 80, 40)
    buy_max_button_rect = pygame.Rect(buy_button_rect.right + 10, button_y + 5, 60, 30)  # New "Max" button for Buy
    buy_plus_button_rect = pygame.Rect(buy_max_button_rect.right + 10, button_y, 40, 40)
    buy_minus_button_rect = pygame.Rect(buy_plus_button_rect.right + 10, button_y, 40, 40)
    buy_quantity_label_rect = pygame.Rect(buy_button_rect.right + 10, buy_button_rect.top - 20, 80, 20)

    # Sell Button and Quantity Changers
    sell_button_rect = pygame.Rect(portfolio_rect.left + 10, button_y, 80, 40)
    sell_max_button_rect = pygame.Rect(sell_button_rect.right + 10, button_y + 5, 60, 30)  # New "Max" button for Sell
    sell_plus_button_rect = pygame.Rect(sell_max_button_rect.right + 10, button_y, 40, 40)
    sell_minus_button_rect = pygame.Rect(sell_plus_button_rect.right + 10, button_y, 40, 40)
    sell_quantity_label_rect = pygame.Rect(sell_button_rect.right + 10, sell_button_rect.top - 20, 80, 20)

    money_pouring = False
    money_pouring_amount = 0
    money_pouring_timer = 0

    news_x = SCREEN_WIDTH
    news_speed = 70  # pixels per second
 
    current_news = random.choice(news_list)
    target_type, target_name, news_sentiment = news_dict[current_news]
    news_text = NEWS_FONT.render(current_news, True, PAPER_YELLOW)
    last_news = ""
    sentiment_duration = random.uniform(0.5,2.75)
    sentiment_effects[(target_type, target_name)] = (news_sentiment, sentiment_duration)

    stock_update_timer = 0
    stock_update_interval = 1.0  # Update stocks every second for graphs

    stock_display_update_timer = 0
    stock_display_update_interval = random.uniform(2, 3)  # Update displayed stock prices every 2-4 seconds

    day_timer = 0
    day_length = 20  # seconds per day

    total_time = 0
    net_worth_timer = 0

    time_scale_button_rects = []
    button_x = 210
    button_y_graph = SCREEN_HEIGHT / 2 + 20 - 35
    for option in time_scale_options:
        rect = pygame.Rect(200 + button_x, button_y_graph - 5, 80, 30)
        time_scale_button_rects.append((rect, option))
        button_x += 90

    day_end_pause = False
    day_end_pause_timer = 0

    content_height_stock = len(stocks) * 30
    visible_height_stock = stock_list_surface.get_height() - 30  # Adjusted for "All" option

    stock_scrollbar_track_rect = pygame.Rect(
        stock_list_rect.width - 15, 30, 15, stock_list_rect.height - 30
    )
    stock_scrollbar = Scrollbar(
        stock_scrollbar_track_rect,
        stock_list_rect.topleft,
        content_height_stock,
        visible_height_stock,
        0
    )

    content_height_portfolio = len(player_portfolio) * 30 + 80
    visible_height_portfolio = portfolio_surface.get_height()

    portfolio_scrollbar_track_rect = pygame.Rect(
        portfolio_rect.width - 15, 0, 15, portfolio_rect.height
    )
    portfolio_scrollbar = Scrollbar(
        portfolio_scrollbar_track_rect,
        portfolio_rect.topleft,
        content_height_portfolio,
        visible_height_portfolio,
        0
    )

    pending_news = []
    fee_deducted_today = False

    # Define the "All (Market performance)" button rect (fixed position)
    all_button_rect = pygame.Rect(stock_list_rect.left, stock_list_rect.top, stock_list_rect.width, 30)

    while True:
        screen.fill(BLACK)
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            draw_vertical_gradient(screen, DARK_GRAY, BLACK)
        draw_background_gradient(screen, DARK_GRAY, 100)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_clicked = True
                if event.button == 4:  # Scroll up
                    stock_scrollbar.scroll_offset += 30
                    stock_scrollbar.scroll_offset = min(0, stock_scrollbar.scroll_offset)
                    portfolio_scrollbar.scroll_offset += 30
                    portfolio_scrollbar.scroll_offset = min(0, portfolio_scrollbar.scroll_offset)
                if event.button == 5:  # Scroll down
                    stock_scrollbar.scroll_offset -= 30
                    stock_scrollbar.scroll_offset = max(-max(content_height_stock - visible_height_stock, 0), stock_scrollbar.scroll_offset)
                    portfolio_scrollbar.scroll_offset -= 30
                    portfolio_scrollbar.scroll_offset = max(-max(content_height_portfolio - visible_height_portfolio, 0), portfolio_scrollbar.scroll_offset)
                if event.button == 1:  # Left mouse button
                    # Handle scrollbar dragging
                    if stock_scrollbar.scroll_bar_rect and stock_scrollbar.scroll_bar_rect.collidepoint(mouse_pos):
                        stock_scrollbar.dragging = True
                        stock_scrollbar.drag_start_y = mouse_pos[1]
                        stock_scrollbar.scroll_start_offset = stock_scrollbar.scroll_offset
                    elif portfolio_scrollbar.scroll_bar_rect and portfolio_scrollbar.scroll_bar_rect.collidepoint(mouse_pos):
                        portfolio_scrollbar.dragging = True
                        portfolio_scrollbar.drag_start_y = mouse_pos[1]
                        portfolio_scrollbar.scroll_start_offset = portfolio_scrollbar.scroll_offset
                    else:
                        # Check if "All" button is clicked
                        if all_button_rect.collidepoint(mouse_pos):
                            selected_stock = None
                            buy_quantity = 1
                            sell_quantity = 1
                            small_click_sound.play()
                        # Stock selection from stock list
                        elif stock_list_rect.collidepoint(mouse_pos):
                            relative_mouse_y = mouse_pos[1] - stock_list_rect.y
                            relative_mouse_y += -stock_scrollbar.scroll_offset
                            index = int(relative_mouse_y // 30)
                            if 0 <= index < len(stocks):
                                new_selected_stock = stocks[index]
                                if new_selected_stock != selected_stock:
                                    selected_stock = new_selected_stock
                                    buy_quantity = 1
                                    sell_quantity = 1
                                    small_click_sound.play()
                        # Stock selection from portfolio
                        elif portfolio_rect.collidepoint(mouse_pos):
                            # Calculate the relative Y position within the portfolio surface
                            relative_mouse_y = mouse_pos[1] - portfolio_rect.y - portfolio_scrollbar.scroll_offset

                            y_offset_portfolio = 10
                            y_offset_portfolio += 20  # Capital text
                            y_offset_portfolio += 30  # Net worth text
                            y_offset_portfolio += 40  # Portfolio title

                            index = int((relative_mouse_y - y_offset_portfolio) // 30)
                            portfolio_items = sorted(player_portfolio.values(), key=lambda item: item['stock'].name)
                            if 0 <= index < len(portfolio_items):
                                selected_stock = portfolio_items[index]['stock']
                                buy_quantity = 1
                                sell_quantity = 1
                                small_click_sound.play()
                            else:
                                # Clicked outside portfolio items
                                pass

                        # Buy quantity adjustment
                        if buy_plus_button_rect.collidepoint(mouse_pos):
                            if selected_stock:
                                max_buy = int((capital - broker_fee) / selected_stock.price)
                                if buy_quantity < max_buy:
                                    buy_quantity += 1
                                    quantity_change_sound.play()
                        if buy_minus_button_rect.collidepoint(mouse_pos):
                            if buy_quantity > 1:
                                buy_quantity -= 1
                                quantity_change_sound.play()
                        # Buy "Max" button
                        if buy_max_button_rect.collidepoint(mouse_pos):
                            if selected_stock:
                                max_buy = int((capital - broker_fee) / selected_stock.price)
                                if max_buy > 0:
                                    buy_quantity = max_buy
                                    quantity_change_sound.play()
                        # Buy button
                        if buy_button_rect.collidepoint(mouse_pos):
                            if selected_stock:
                                total_price = selected_stock.price * buy_quantity + broker_fee
                                if capital >= total_price:
                                    capital -= total_price
                                    buy_sound.play()
                                    if selected_stock.name in player_portfolio:
                                        player_portfolio[selected_stock.name]['quantity'] += buy_quantity
                                    else:
                                        player_portfolio[selected_stock.name] = {'stock': selected_stock, 'quantity': buy_quantity}
                                    content_height_portfolio = len(player_portfolio) * 30 + 80
                                    portfolio_scrollbar.update(content_height_portfolio, visible_height_portfolio, portfolio_scrollbar.scroll_offset)
                        # Sell quantity adjustment
                        if sell_plus_button_rect.collidepoint(mouse_pos):
                            if selected_stock and selected_stock.name in player_portfolio:
                                max_sell = player_portfolio[selected_stock.name]['quantity']
                                if sell_quantity < max_sell:
                                    sell_quantity +=1
                                    quantity_change_sound.play()
                        if sell_minus_button_rect.collidepoint(mouse_pos):
                            if sell_quantity >1:
                                sell_quantity -=1
                                quantity_change_sound.play()
                        # Sell "Max" button
                        if sell_max_button_rect.collidepoint(mouse_pos):
                            if selected_stock and selected_stock.name in player_portfolio:
                                max_sell = player_portfolio[selected_stock.name]['quantity']
                                if max_sell > 0:
                                    sell_quantity = max_sell
                                    quantity_change_sound.play()
                        # Sell button
                        if sell_button_rect.collidepoint(mouse_pos):
                            if selected_stock and selected_stock.name in player_portfolio:
                                if player_portfolio[selected_stock.name]['quantity'] >= sell_quantity:
                                    player_portfolio[selected_stock.name]['quantity'] -= sell_quantity
                                    if player_portfolio[selected_stock.name]['quantity'] ==0:
                                        del player_portfolio[selected_stock.name]
                                    money_pouring = True
                                    money_pouring_amount += selected_stock.price * sell_quantity - broker_fee
                                    sell_sound.play()
                                    content_height_portfolio = len(player_portfolio) * 30 + 80
                                    portfolio_scrollbar.update(content_height_portfolio, visible_height_portfolio, portfolio_scrollbar.scroll_offset)
                        # Time scale selection
                        for rect, option in time_scale_button_rects:
                            if rect.collidepoint(mouse_pos):
                                selected_time_scale = option
                                small_click_sound.play()

            if event.type == MOUSEBUTTONUP:
                if event.button ==1:
                    stock_scrollbar.dragging = False
                    portfolio_scrollbar.dragging = False
            if event.type == MOUSEMOTION:
                if stock_scrollbar.dragging:
                    dy = event.pos[1] - stock_scrollbar.drag_start_y
                    track_movable_height = stock_scrollbar.track_rect.height - (stock_scrollbar.scroll_bar_rect.height if stock_scrollbar.scroll_bar_rect else 0)
                    content_scrollable_height = stock_scrollbar.content_height - stock_scrollbar.visible_height
                    if content_scrollable_height >0:
                        scroll_ratio = dy / track_movable_height
                        stock_scrollbar.scroll_offset = stock_scrollbar.scroll_start_offset - scroll_ratio * content_scrollable_height
                        stock_scrollbar.scroll_offset = min(0, max(-content_scrollable_height, stock_scrollbar.scroll_offset))
                if portfolio_scrollbar.dragging:
                    dy = event.pos[1] - portfolio_scrollbar.drag_start_y
                    track_movable_height = portfolio_scrollbar.track_rect.height - (portfolio_scrollbar.scroll_bar_rect.height if portfolio_scrollbar.scroll_bar_rect else 0)
                    content_scrollable_height = portfolio_scrollbar.content_height - portfolio_scrollbar.visible_height
                    if content_scrollable_height >0:
                        scroll_ratio = dy / track_movable_height
                        portfolio_scrollbar.scroll_offset = portfolio_scrollbar.scroll_start_offset - scroll_ratio * content_scrollable_height
                        portfolio_scrollbar.scroll_offset = min(0, max(-content_scrollable_height, portfolio_scrollbar.scroll_offset))

        # Update Scrollbars
        stock_scrollbar.update(content_height_stock, visible_height_stock, stock_scrollbar.scroll_offset)
        portfolio_scrollbar.update(content_height_portfolio, visible_height_portfolio, portfolio_scrollbar.scroll_offset)

        # Update Timers
        dt = clock.tick(60) / 1000
        total_time += dt
        net_worth_timer += dt
        stock_update_timer += dt
        stock_display_update_timer += dt

        if day_end_pause:
            day_end_pause_timer += dt
            if day_end_pause_timer >=1.0:
                day_end_pause = False
                num_stocks_to_adjust = int(total_number_of_stocks * 0.15)
                num_stocks_to_adjust = min(num_stocks_to_adjust, len(stocks))
                stocks_to_adjust = random.sample(stocks, num_stocks_to_adjust)
                for stock in stocks_to_adjust:
                    adjustment = random.uniform(-2.0, 2.0)
                    stock.price += adjustment
                    if stock.price <0.1:
                        stock.price =0.1
                    stock.history.append((total_time, stock.price))
        else:
            day_timer += dt
            day_progress = day_timer / day_length

        if money_pouring:
            money_pouring_timer += dt
            if money_pouring_timer >= money_pouring_speed:
                increment = min(10, money_pouring_amount)
                capital += increment
                money_pouring_amount -= increment
                money_pouring_timer =0
                account_beep.play()
                if money_pouring_amount <=0:
                    money_pouring = False

        if (day_length - day_timer) <=5 and not day_ending_sound_played and not day_end_pause:
            day_ending_tick.play()
            day_ending_sound_played = True

        if day_timer >= day_length and not day_end_pause:
            day_timer =0
            day_ending_sound_played = False
            current_day +=1
            date_increment_sound.play()

            current_day_in_month +=1
            days_in_current_month = month_days[current_month_index]
            if current_day_in_month > days_in_current_month:
                current_day_in_month =1
                current_month_index +=1
                if current_month_index >=12:
                    current_month_index =0
                    current_year +=1

            if current_day_in_month ==1 and not fee_deducted_today:
                # Pay dividends
                total_dividends = 0
                for item in player_portfolio.values():
                    stock = item['stock']
                    qty = item['quantity']
                    dividend_payment = (stock.price * (stock.dividend_yield / 100)) * qty / 12
                    dividend_payment = round(dividend_payment, 2)
                    total_dividends += dividend_payment
                    if dividend_payment > 0:
                        capital += dividend_payment
                        pending_news.append(f"Received ${dividend_payment:.2f} in dividends from {stock.name}.")
                # Deduct account fee
                capital -= account_fee
                pending_news.append(f"Account fees of ${account_fee:.2f} have been deducted.")
                fee_deducted_today = True
            elif current_day_in_month !=1:
                fee_deducted_today = False

            if current_day_in_month >= days_in_current_month -1:
                if f"Account fees of ${account_fee:.2f} will be deducted on the 1st of next month." not in pending_news:
                    pending_news.append(f"Account fees of ${account_fee:.2f} will be deducted on the 1st of next month.")

            keys_to_remove = []
            for key in sentiment_effects:
                sentiment, duration = sentiment_effects[key]
                duration -= 1
                if duration <= 0:
                    keys_to_remove.append(key)
                else:
                    sentiment_effects[key] = (sentiment, duration)
            for key in keys_to_remove:
                del sentiment_effects[key]

            day_end_pause = True
            day_end_pause_timer =0
            day_progress =1

        if stock_update_timer >= stock_update_interval:
            stock_update_timer =0
            for stock in stocks:
                stock.update_price(total_time, current_month_index)  # Pass current_month_index

        if stock_display_update_timer >= stock_display_update_interval:
            stock_display_update_timer = 0
            stock_display_update_interval = 2
            for stock in stocks:
                stock.update_display_price()

        news_x -= news_speed * dt
        if news_x + news_text.get_width() <0:
            if pending_news:
                current_news = pending_news.pop(0)
                news_text = NEWS_FONT.render(current_news, True, PAPER_YELLOW)
                news_x = SCREEN_WIDTH - 150
            else:
                last_news = current_news
                current_news = random.choice(news_list)
                while current_news == last_news:
                    current_news = random.choice(news_list)
                target_type, target_name, news_sentiment = news_dict[current_news]
                news_text = NEWS_FONT.render(current_news, True, PAPER_YELLOW)
                news_x = SCREEN_WIDTH - 150
        sentiment_duration = random.uniform(0.5,2.75)
        sentiment_effects[(target_type, target_name)] = (news_sentiment, sentiment_duration)

        net_worth_display = capital + money_pouring_amount + sum(item['stock'].price * item['quantity'] for item in player_portfolio.values())
        net_worth = net_worth_display

        if net_worth_timer >=1.0:
            net_worth_history.append((total_time, net_worth_display))
            market_index_value = sum(stock.price for stock in stocks) / len(stocks)
            market_index_history.append((total_time, market_index_value))
            net_worth_timer =0

        # Draw Stocks List
        stock_list_surface.fill(DARK_GRAY)
        y_offset =0  # Start from top

        # "All" is now drawn separately, so no need to draw it here

        y_offset += stock_scrollbar.scroll_offset

        for idx, stock in enumerate(stocks):
            stock_text = FONT_SMALL.render(f"{stock.name}: ${stock.display_price:.1f}", True, WHITE)
            stock_list_surface.blit(stock_text, (10, y_offset))
            if selected_stock == stock:
                pygame.draw.rect(stock_list_surface, LIGHT_GRAY, pygame.Rect(0, y_offset -5, stock_list_rect.width, 30), 2)
            y_offset +=30

        stock_scrollbar.update(content_height_stock, visible_height_stock, stock_scrollbar.scroll_offset)
        stock_scrollbar.draw(stock_list_surface)

        screen.blit(stock_list_surface, stock_list_rect.topleft)

        # Draw "All (Market performance)" on top of stock list and scrollbar
        pygame.draw.rect(screen, GRAY, all_button_rect, 0)  # Fully filled background
        all_text = FONT_SMALL.render("All (Market performance)", True, WHITE)
        screen.blit(all_text, (all_button_rect.x + 10, all_button_rect.y + 5))
        if selected_stock is None:
            pygame.draw.rect(screen, LIGHT_GRAY, all_button_rect, 2)

        # Draw Buy Quantity and Buttons
        # Buy Quantity Label
        buy_quantity_text = FONT_SMALL.render(f"Qty: {buy_quantity}", True, WHITE)
        screen.blit(buy_quantity_text, (buy_quantity_label_rect.x, buy_quantity_label_rect.y-10))

        # Buy Plus and Minus Buttons
        pygame.draw.rect(screen, GRAY, buy_plus_button_rect)
        pygame.draw.rect(screen, GRAY, buy_minus_button_rect)
        plus_text = FONT_SMALL.render("+", True, PAPER_YELLOW)
        minus_text = FONT_SMALL.render("-", True, PAPER_YELLOW)
        screen.blit(plus_text, (buy_plus_button_rect.x + 15, buy_plus_button_rect.y +5))
        screen.blit(minus_text, (buy_minus_button_rect.x +15, buy_minus_button_rect.y +5))

        # Buy "Max" Button
        pygame.draw.rect(screen, ORANGE, buy_max_button_rect)
        max_buy_text = FONT_SMALL.render("Max", True, BLACK)
        screen.blit(max_buy_text, (buy_max_button_rect.x + (buy_max_button_rect.width - max_buy_text.get_width()) / 2,
                                   buy_max_button_rect.y + (buy_max_button_rect.height - max_buy_text.get_height()) / 2))

        # Buy Button
        pygame.draw.rect(screen, GREEN, buy_button_rect)
        buy_text = FONT_SMALL.render("Buy", True, BLACK)
        screen.blit(buy_text, (buy_button_rect.x + (buy_button_rect.width - buy_text.get_width())//2,
                               buy_button_rect.y + (buy_button_rect.height - buy_text.get_height())//2))

        # **New Code Start: Display Total Buy Amount Including Broker Fee**
        if selected_stock:
            total_buy = selected_stock.price * buy_quantity + broker_fee
            buy_total_text = FONT_SMALL.render(f"Total Buy: ${total_buy:.2f}", True, WHITE)
        else:
            buy_total_text = FONT_SMALL.render(f"Total Buy: $0.00", True, WHITE)
        # Position the total buy text below the Buy button
        screen.blit(buy_total_text, (buy_button_rect.x, buy_button_rect.y + buy_button_rect.height + 5))
        # **New Code End**

        # Draw Sell Quantity and Buttons
        # Sell Quantity Label
        sell_quantity_text = FONT_SMALL.render(f"Qty: {sell_quantity}", True, WHITE)
        screen.blit(sell_quantity_text, (sell_quantity_label_rect.x, sell_quantity_label_rect.y-10))

        # Sell Plus and Minus Buttons
        pygame.draw.rect(screen, GRAY, sell_plus_button_rect)
        pygame.draw.rect(screen, GRAY, sell_minus_button_rect)
        sell_plus_text = FONT_SMALL.render("+", True, PAPER_YELLOW)
        sell_minus_text = FONT_SMALL.render("-", True, PAPER_YELLOW)
        screen.blit(sell_plus_text, (sell_plus_button_rect.x +15, sell_plus_button_rect.y +5))
        screen.blit(sell_minus_text, (sell_minus_button_rect.x +15, sell_minus_button_rect.y +5))

        # Sell "Max" Button
        pygame.draw.rect(screen, ORANGE, sell_max_button_rect)
        max_sell_text = FONT_SMALL.render("Max", True, BLACK)
        screen.blit(max_sell_text, (sell_max_button_rect.x + (sell_max_button_rect.width - max_sell_text.get_width()) / 2,
                                    sell_max_button_rect.y + (sell_max_button_rect.height - max_sell_text.get_height()) / 2))

        # Sell Button
        pygame.draw.rect(screen, RED, sell_button_rect)
        sell_text = FONT_SMALL.render("Sell", True, BLACK)
        screen.blit(sell_text, (sell_button_rect.x + (sell_button_rect.width - sell_text.get_width())//2,
                                sell_button_rect.y + (sell_button_rect.height - sell_text.get_height())//2))

        # **New Code Start: Display Total Sell Amount Including Broker Fee**
        if selected_stock and selected_stock.name in player_portfolio:
            total_sell = selected_stock.price * sell_quantity
            # Ensure that total_sell is not negative
            if total_sell < 0:
                total_sell = 0.00
            sell_total_text = FONT_SMALL.render(f"Total Sell: ${total_sell:.2f} (-${broker_fee} Broker fee)", True, PAPER_YELLOW)
        else:
            sell_total_text = FONT_SMALL.render(f"Total Sell: $0.00", True, PAPER_YELLOW)
        # Position the total sell text below the Sell button
        screen.blit(sell_total_text, (sell_button_rect.x, sell_button_rect.y + sell_button_rect.height + 5))
        # **New Code End**

        # Draw Portfolio
        portfolio_surface.fill(DARK_GRAY)
        y_offset_portfolio =10

        capital_text = FONT_SMALL.render(f"Capital: ${capital:.2f}", True, WHITE)
        net_worth_text = FONT_SMALL.render(f"Net Worth: ${net_worth:.2f}", True, WHITE)
        portfolio_surface.blit(capital_text, (10, y_offset_portfolio))
        y_offset_portfolio +=20
        portfolio_surface.blit(net_worth_text, (10, y_offset_portfolio))
        y_offset_portfolio +=30

        portfolio_text = FONT_MEDIUM.render("Portfolio", True, WHITE)
        portfolio_surface.blit(portfolio_text, (10, y_offset_portfolio))
        y_offset_portfolio +=40

        y_offset_portfolio += portfolio_scrollbar.scroll_offset

        # Sort portfolio items alphabetically for consistent ordering
        portfolio_items = sorted(player_portfolio.values(), key=lambda item: item['stock'].name)
        for item in portfolio_items:
            stock = item['stock']
            qty = item['quantity']
            text = FONT_SMALL.render(f"{stock.name}: {qty} shares (${stock.price:.1f}/share)", True, WHITE)
            portfolio_surface.blit(text, (10, y_offset_portfolio))
            if selected_stock == stock:
                pygame.draw.rect(portfolio_surface, LIGHT_GRAY, pygame.Rect(0, y_offset_portfolio -5, 300, 30), 2)
            y_offset_portfolio += 30

        portfolio_scrollbar.update(content_height_portfolio, visible_height_portfolio, portfolio_scrollbar.scroll_offset)
        portfolio_scrollbar.draw(portfolio_surface)

        screen.blit(portfolio_surface, portfolio_rect.topleft)

        # Draw News Bar
        news_bar = pygame.Surface((SCREEN_WIDTH, 30))
        news_bar.fill(DARK_GRAY)
        news_bar.blit(news_text, (news_x, 5))
        screen.blit(news_bar, (0, 0))

        # Draw "News" label with background on the main screen
        news_label_rect = pygame.Rect(0,0,80,30)
        pygame.draw.rect(screen, DARK_GRAY, news_label_rect)  # Draw on screen to cover news behind
        news_label_text = NEWS_FONT.render("News", True, PAPER_YELLOW)
        screen.blit(news_label_text, (10,5))

        # Draw date label with background on the main screen
        date_label_rect = pygame.Rect(SCREEN_WIDTH -150,0,200,30)
        pygame.draw.rect(screen, DARK_GRAY, date_label_rect)  # Draw on screen to cover news behind
        date_str = f"{current_day_in_month}{get_day_suffix(current_day_in_month)} {months[current_month_index]}, {current_year}"
        date_label_text = CALENDER_FONT.render(date_str, True, PAPER_YELLOW)
        text_width = date_label_text.get_width()
        screen.blit(date_label_text, (SCREEN_WIDTH - text_width -10, 5))

        # Draw Day Progress Bar
        progress_bar_width = SCREEN_WIDTH -20
        progress_bar = pygame.Rect(10, SCREEN_HEIGHT -30, progress_bar_width * day_progress, 20)
        if day_ending_sound_played or day_end_pause:
            bar_color = ORANGE
        else:
            bar_color = GREEN
        pygame.draw.rect(screen, bar_color, progress_bar)
        pygame.draw.rect(screen, WHITE, (10, SCREEN_HEIGHT -30, progress_bar_width, 20), 2)

        # Draw Time Scale Buttons
        for rect, option in time_scale_button_rects:
            if selected_time_scale == option:
                pygame.draw.rect(screen, LIGHT_GRAY, rect)
            else:
                pygame.draw.rect(screen, DARK_GRAY, rect)
            text = FONT_SMALL.render(option, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        # Adjust graph rects
        graph_left_margin =60

        # Draw Net Worth Graph
        net_worth_graph_rect = pygame.Rect(210 + graph_left_margin, SCREEN_HEIGHT /2 +20, SCREEN_WIDTH -530 - graph_left_margin, SCREEN_HEIGHT /2 -70)
        pygame.draw.rect(screen, DARK_GRAY, net_worth_graph_rect)
        pygame.draw.rect(screen, WHITE, net_worth_graph_rect, 2)

        net_worth_data = get_graph_data(net_worth_history, total_time, selected_time_scale)
        if len(net_worth_data) >1:
            draw_graph(screen, net_worth_graph_rect, net_worth_data, BLUE, min_reference=start_capital, split_color=True)

        # Draw Market Index or Stock Price Graph
        if selected_stock is None:
            graph_title = "Market Index"
            market_graph_rect = pygame.Rect(210 + graph_left_margin, 70, SCREEN_WIDTH -530 - graph_left_margin, SCREEN_HEIGHT /2 -100)
            pygame.draw.rect(screen, DARK_GRAY, market_graph_rect)
            pygame.draw.rect(screen, WHITE, market_graph_rect, 2)

            market_index_data = get_graph_data(market_index_history, total_time, selected_time_scale)
            if len(market_index_data) >1:
                draw_graph(screen, market_graph_rect, market_index_data, RED)
        else:
            graph_title = f"{selected_stock.name} Price"
            stock_graph_rect = pygame.Rect(210 + graph_left_margin, 70, SCREEN_WIDTH -530 - graph_left_margin, SCREEN_HEIGHT /2 -100)
            pygame.draw.rect(screen, DARK_GRAY, stock_graph_rect)
            pygame.draw.rect(screen, WHITE, stock_graph_rect, 2)

            stock_data = get_graph_data(selected_stock.history, total_time, selected_time_scale)
            if len(stock_data) >1:
                line_color = GREEN if net_worth_display >=1000 else RED
                draw_graph(screen, stock_graph_rect, stock_data, line_color, min_reference=1000, split_color=True)

        # Draw Graph Title
        graph_title_text = FONT_MEDIUM.render(graph_title, True, WHITE)
        screen.blit(graph_title_text, (280, 30))

        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
