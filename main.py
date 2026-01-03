import pygame
import sys
import random

from config import *
from tetromino import Tetromino
from assets import init_assets, sounds, background_music_sound, sound_on
from game_logic import load_highscore, save_highscore, create_grid, valid_move, clear_lines, get_fall_speed
from drawing import (
    draw_block, draw_grid_lines, draw_piece, draw_main_frame, draw_sidebar,
    draw_control_buttons, draw_start_screen, draw_pause_screen,
    draw_new_game_over, draw_confirm_quit
)

# === KHỞI TẠO PYGAME ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xếp Hình Tetris")
clock = pygame.time.Clock()

# Load font và âm thanh
font_title_big, font_big, font_medium = init_assets()

# === BIẾN ÂM THANH ===
last_move_sound_time = 0
MOVE_SOUND_COOLDOWN = 0.08

bg_channel = None

def play_sound(key):
    global last_move_sound_time
    if not sound_on or key not in sounds:
        return
    current_time = pygame.time.get_ticks() / 1000.0
    if key == 'move_rotate':
        if current_time - last_move_sound_time < MOVE_SOUND_COOLDOWN:
            return
        last_move_sound_time = current_time
    sounds[key].stop()
    sounds[key].play()

def play_background_music():
    global bg_channel
    if background_music_sound and sound_on:
        if bg_channel:
            bg_channel.stop()
        bg_channel = background_music_sound.play(-1)

def stop_background_music():
    global bg_channel
    if bg_channel:
        bg_channel.stop()
        bg_channel = None

# === TRẠNG THÁI GAME ===
def reset_game():
    global current_piece, next_piece, locked, score, highscore, fall_time, fall_speed, current_level
    global in_start_screen, paused, game_over, confirm_quit

    current_piece = Tetromino()
    next_piece = Tetromino()
    locked = {}
    score = 0
    highscore = load_highscore()
    fall_time = 0
    fall_speed = get_fall_speed(score)
    current_level = 1

    in_start_screen = True
    paused = False
    game_over = False
    confirm_quit = False

# Biến toàn cục
reset_game()
das_delay = 0.15
arr_speed = 0.05
das_left_time = das_delay
das_right_time = das_delay

play_background_music()

# === VÒNG LẬP CHÍNH ===
running = True
while running:
    clock.tick(60)
    fall_time += clock.get_delta() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Nút âm thanh, pause, thoát ở góc trên phải
            if not in_start_screen and not paused and not game_over and not confirm_quit:
                volume_rect = pygame.Rect(SCREEN_WIDTH - 170, 25, 40, 40)
                pause_rect = pygame.Rect(SCREEN_WIDTH - 115, 25, 40, 40)
                exit_rect = pygame.Rect(SCREEN_WIDTH - 60, 25, 40, 40)

                if volume_rect.collidepoint(mx, my):
                    sound_on = not sound_on
                    if sound_on:
                        play_background_music()
                    else:
                        stop_background_music()
                        pygame.mixer.stop()
                if pause_rect.collidepoint(mx, my):
                    paused = True
                if exit_rect.collidepoint(mx, my):
                    confirm_quit = True

            # Xác nhận thoát
            if confirm_quit and yes_rect and no_rect:
                if yes_rect.collidepoint(mx, my):
                    in_start_screen = True
                    reset_game()
                    confirm_quit = False
                elif no_rect.collidepoint(mx, my):
                    confirm_quit = False

            # Màn hình bắt đầu
            if in_start_screen:
                if SCREEN_WIDTH // 2 - 50 <= mx <= SCREEN_WIDTH // 2 + 50 and 400 <= my <= 500:
                    in_start_screen = False
                    reset_game()
                continue

            # Màn hình tạm dừng
            if paused:
                if SCREEN_WIDTH // 2 - 50 <= mx <= SCREEN_WIDTH // 2 + 50 and 400 <= my <= 500:
                    paused = False
                continue

            # Game over - nút home
            if game_over:
                home_rect = pygame.Rect(SCREEN_WIDTH // 2 - 43, 570, 80, 80)
                if home_rect.collidepoint(mx, my):
                    play_sound('button')
                    stop_background_music()
                    pygame.mixer.stop()
                    in_start_screen = True
                    reset_game()
                continue

        if event.type == pygame.KEYDOWN:
            if in_start_screen:
                in_start_screen = False
                reset_game()
                continue

            if paused and (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT):
                paused = False
                continue

            if not paused and not game_over and not confirm_quit:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    paused = True

                if event.key == pygame.K_DOWN:
                    fall_speed = 0.05  # soft drop

                if event.key == pygame.K_UP:
                    old = [row[:] for row in current_piece.shape]
                    current_piece.rotate()
                    if not valid_move(current_piece, create_grid(locked)):
                        current_piece.shape = old
                    else:
                        play_sound('move_rotate')

                if event.key == pygame.K_LEFT and valid_move(current_piece, create_grid(locked), -1):
                    current_piece.x -= 1
                    das_left_time = das_delay
                    play_sound('move_rotate')

                if event.key == pygame.K_RIGHT and valid_move(current_piece, create_grid(locked), 1):
                    current_piece.x += 1
                    das_right_time = das_delay
                    play_sound('move_rotate')

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                fall_speed = get_fall_speed(score)

    # DAS (Delayed Auto Shift)
    if not in_start_screen and not paused and not game_over and not confirm_quit:
        keys = pygame.key.get_pressed()
        dt = clock.get_delta() / 1000.0

        if keys[pygame.K_LEFT]:
            das_left_time -= dt
            if das_left_time <= 0 and valid_move(current_piece, create_grid(locked), -1):
                current_piece.x -= 1
                das_left_time = arr_speed
        else:
            das_left_time = das_delay

        if keys[pygame.K_RIGHT]:
            das_right_time -= dt
            if das_right_time <= 0 and valid_move(current_piece, create_grid(locked), 1):
                current_piece.x += 1
                das_right_time = arr_speed
        else:
            das_right_time = das_delay

    # VẼ MÀN HÌNH
    if in_start_screen:
        draw_start_screen(screen, font_title_big)

    elif paused:
        draw_pause_screen(screen, font_title_big)

    elif game_over:
        draw_new_game_over(screen, current_level, score, highscore, font_title_big, font_medium, font_big)

    elif confirm_quit:
        screen.fill(DARK_BLUE)
        draw_main_frame(screen)
        draw_grid_lines(screen)
        for (gx, gy), color in locked.items():
            draw_block(screen, color, gx, gy)
        draw_piece(screen, current_piece)
        draw_sidebar(screen, next_piece, score, highscore, font_big, font_medium)
        draw_control_buttons(screen, sound_on)
        yes_rect, no_rect = draw_confirm_quit(screen, font_big)

    else:
        screen.fill(DARK_BLUE)
        draw_main_frame(screen)
        draw_grid_lines(screen)
        for (gx, gy), color in locked.items():
            draw_block(screen, color, gx, gy)
        draw_piece(screen, current_piece)
        draw_sidebar(screen, next_piece, score, highscore, font_big, font_medium)
        draw_control_buttons(screen, sound_on)

        # Rơi tự động
        if fall_time >= fall_speed:
            fall_time = 0
            if valid_move(current_piece, create_grid(locked), dy=1):
                current_piece.y += 1
            else:
                # Khóa khối
                for iy, row in enumerate(current_piece.shape):
                    for ix, cell in enumerate(row):
                        if cell:
                            locked[(current_piece.x + ix, current_piece.y + iy)] = current_piece.color

                # Xóa dòng
                lines, locked = clear_lines(locked)
                points = [0, 50, 200, 300, 400]
                if 0 < lines <= 4:
                    score += points[lines]
                    if lines == 1:
                        play_sound('clear_single')
                    elif lines >= 2:
                        play_sound('clear_multi')

                # Cập nhật điểm cao
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)
                    play_sound('new_record')

                # Cập nhật tốc độ và level
                fall_speed = get_fall_speed(score)
                current_level = 1 + (score // 1000)

                # Tạo khối mới
                current_piece = next_piece
                next_piece = Tetromino()

                # Game over?
                if not valid_move(current_piece, create_grid(locked)):
                    game_over = True
                    stop_background_music()
                    play_sound('gameover')

    pygame.display.update()

# Thoát game
stop_background_music()
pygame.quit()
sys.exit()