import pygame
import os

sounds = {}
background_music_sound = None
bg_channel = None
sound_on = True

font_title_big = None
font_big = None
font_medium = None

def init_assets():
    global font_title_big, font_big, font_medium, sounds, background_music_sound

    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()

        sounds['button'] = pygame.mixer.Sound('sounds/button.wav')
        sounds['clear_single'] = pygame.mixer.Sound('sounds/clear_single.wav')
        sounds['clear_multi'] = pygame.mixer.Sound('sounds/clear_multi.wav')
        sounds['move_rotate'] = pygame.mixer.Sound('sounds/rotate.wav')
        sounds['gameover'] = pygame.mixer.Sound('sounds/gameover.wav')
        sounds['new_record'] = pygame.mixer.Sound('sounds/newrecord.wav')
        background_music_sound = pygame.mixer.Sound('sounds/bgm.wav')

        for s in sounds.values():
            s.set_volume(0.5)
        background_music_sound.set_volume(0.25)

    except pygame.error as e:
        print("Không thể khởi tạo âm thanh:", e)
        global sound_on
        sound_on = False

    # Font
    try:
        font_title_big = pygame.font.SysFont("times new roman", 60, bold=True)
        font_big = pygame.font.SysFont("times new roman", 36, bold=True)
        font_medium = pygame.font.SysFont("times new roman", 32)
    except:
        font_title_big = pygame.font.SysFont("arial", 60, bold=True)
        font_big = pygame.font.SysFont("arial", 36, bold=True)
        font_medium = pygame.font.SysFont("arial", 32)

    return font_title_big, font_big, font_medium