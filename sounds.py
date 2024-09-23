import pygame
import os
import sys

# Initialize pygame mixer
pygame.mixer.init()

# Get the root directory of the game
SRC_PATH = os.path.dirname(os.path.abspath(__file__))

# Load sounds
try:
    menu_music = pygame.mixer.Sound(os.path.join(SRC_PATH, "intro.wav"))
    menu_music.set_volume(0.45)
    game_music = pygame.mixer.Sound(os.path.join(SRC_PATH, "game_music.mp3"))
    game_music.set_volume(0.25)
    sell_sound = pygame.mixer.Sound(os.path.join(SRC_PATH, "sell.mp3"))
    sell_sound.set_volume(0.5)
    buy_sound = pygame.mixer.Sound(os.path.join(SRC_PATH, "buy.mp3"))
    buy_sound.set_volume(0.32)
    date_increment_sound = pygame.mixer.Sound(os.path.join(SRC_PATH, "date_increment.mp3"))
    date_increment_sound.set_volume(0.6)
    quantity_change_sound = pygame.mixer.Sound(os.path.join(SRC_PATH, "quantity_change_sound.mp3"))
    quantity_change_sound.set_volume(0.15)
    account_beep = pygame.mixer.Sound(os.path.join(SRC_PATH, "account_beep.mp3"))
    account_beep.set_volume(0.18)
    day_ending_tick = pygame.mixer.Sound(os.path.join(SRC_PATH, "day_ending_tick.mp3"))
    day_ending_tick.set_volume(0.75)
    small_click_sound = pygame.mixer.Sound(os.path.join(SRC_PATH, "small_click.mp3"))
    small_click_sound.set_volume(0.80)
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    sys.exit()

# Export sounds
__all__ = ['menu_music', 'game_music', 'sell_sound', 'buy_sound', 'date_increment_sound', 
           'quantity_change_sound', 'account_beep', 'day_ending_tick', 'small_click_sound']
