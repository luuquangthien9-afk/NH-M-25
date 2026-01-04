import pygame
import random
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "sounds")
pygame.init()

sounds = {}
background_music_sound = None
bg_channel = None
sound_on = True  
mixer_available = False

last_move_sound_time = 0
MOVE_SOUND_COOLDOWN = 0.08  

try:
    # Buffer lớn hơn + tần số ổn định để tránh crackle/chồng chéo
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
    pygame.mixer.init()

    sounds['button'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'button.wav'))
    sounds['clear_single'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'clear_single.wav'))
    sounds['clear_multi'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'clear_multi.wav'))
    sounds['move_rotate'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'rotate.wav'))
    sounds['gameover'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'gameover.wav'))
    sounds['new_record'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'newrecord.wav'))
    background_music_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'bgm.wav'))


    # Giảm volume để tránh chồng lấn
    for s in sounds.values():
        s.set_volume(0.5)
    background_music_sound.set_volume(0.25)

    print("Âm thanh đã sẵn sàng! (Đã tối ưu chống lộn xộn)")

except pygame.error as e:
    print("Không thể khởi tạo âm thanh:", e)
    sound_on = False

# Hàm phát âm thanh an toàn với cooldown cho move/rotate
def play_sound(key):
    global last_move_sound_time
    if not sound_on or key not in sounds:
        return
    
    current_time = pygame.time.get_ticks() / 1000.0
    
    # Chỉ áp dụng cooldown cho âm thanh di chuyển/xoay
    if key == 'move_rotate':
        if current_time - last_move_sound_time < MOVE_SOUND_COOLDOWN:
            return
        last_move_sound_time = current_time
    
    # Dừng sound cũ trước khi phát mới (tránh chồng chéo)
    sounds[key].stop()
    sounds[key].play()

# Hàm nhạc nền
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

# Màu sắc
BLACK = (0, 0, 0)
DARK_BLUE = (5, 15, 35)
GLASS_BLUE = (20, 60, 120)
NEON_BLUE = (0, 180, 255)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 50, 200)
NEON_GREEN = (0, 255, 150)
NEON_YELLOW = (255, 255, 50)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)

# Màu các khối
COLORS = [
    NEON_CYAN,       # I
    NEON_YELLOW,     # O
    NEON_PINK,       # T
    NEON_GREEN,      # S
    RED,             # Z
    NEON_BLUE,       # J
    ORANGE           # L
]

# Kích thước
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = 100
GRID_Y = 80

SIDEBAR_X = GRID_X + GRID_WIDTH * BLOCK_SIZE + 50
SCREEN_WIDTH = SIDEBAR_X + 280
SCREEN_HEIGHT = GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 120

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xếp Hình Tetris")
clock = pygame.time.Clock()

# Font chữ
try:
    font_title_big = pygame.font.SysFont("times new roman", 60, bold=True)  
    font_big = pygame.font.SysFont("times new roman", 36, bold=True)        
    font_medium = pygame.font.SysFont("times new roman", 32)                
except:
    font_title_big = pygame.font.SysFont("arial", 60, bold=True)
    font_big = pygame.font.SysFont("arial", 36, bold=True)
    font_medium = pygame.font.SysFont("arial", 32)

# Hình khối
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

class Tetromino:
    def __init__(self):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = [row[:] for row in SHAPES[self.shape_index]]
        self.color = COLORS[self.shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# Load/Save High Score
def load_highscore():
    if os.path.exists('highscore.txt'):
        try:
            with open('highscore.txt', 'r', encoding='utf-8') as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    with open('highscore.txt', 'w', encoding='utf-8') as f:
        f.write(str(score))

def create_grid(locked={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked:
                grid[y][x] = locked[(x, y)]
    return grid

def valid_move(piece, grid, dx=0, dy=0):
    for iy, row in enumerate(piece.shape):
        for ix, cell in enumerate(row):
            if cell:
                nx = piece.x + ix + dx
                ny = piece.y + iy + dy
                if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                    return False
                if ny >= 0 and grid[ny][nx] != BLACK:
                    return False
    return True

def clear_lines(locked):
    grid = create_grid(locked)
    lines_cleared = 0
    new_locked = {}
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK in grid[y]:
            for x in range(GRID_WIDTH):
                if grid[y][x] != BLACK:
                    new_y = y + lines_cleared
                    new_locked[(x, new_y)] = grid[y][x]
        else:
            lines_cleared += 1
    return lines_cleared, new_locked

def draw_grid_lines():
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, (30, 50, 80),
                         (GRID_X + x * BLOCK_SIZE, GRID_Y),
                         (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT * BLOCK_SIZE))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, (30, 50, 80),
                         (GRID_X, GRID_Y + y * BLOCK_SIZE),
                         (GRID_X + GRID_WIDTH * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE))

def draw_block(color, grid_x, grid_y):
    x = GRID_X + grid_x * BLOCK_SIZE
    y = GRID_Y + grid_y * BLOCK_SIZE
    shadow = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 15))
    screen.blit(shadow, (x + 4, y + 4))
    pygame.draw.rect(screen, color, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
    pygame.draw.rect(screen, (255, 255, 255, 50), (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)
    pygame.draw.rect(screen, (255, 255, 255, 80), (x + 4, y + 4, 6, 6))

def draw_next_piece(piece):
    frame_x = SIDEBAR_X + 10
    frame_y = 150
    frame_w = 260
    frame_h = 140
    
    inner_x = frame_x + 30
    inner_y = frame_y + 20
    inner_w = frame_w - 60
    inner_h = frame_h - 40
    
    shape_w = len(piece.shape[0]) * BLOCK_SIZE
    shape_h = len(piece.shape) * BLOCK_SIZE
    
    pos_x = inner_x + (inner_w - shape_w) // 2
    pos_y = inner_y + (inner_h - shape_h) // 2
    
    for iy, row in enumerate(piece.shape):
        for ix, cell in enumerate(row):
            if cell:
                block_x = pos_x + ix * BLOCK_SIZE
                block_y = pos_y + iy * BLOCK_SIZE
                
                shadow = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 15))
                screen.blit(shadow, (block_x + 4, block_y + 4))
                
                pygame.draw.rect(screen, piece.color, 
                                (block_x + 1, block_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                pygame.draw.rect(screen, (255, 255, 255, 50), 
                                (block_x + 1, block_y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)
                pygame.draw.rect(screen, (255, 255, 255, 80), 
                                (block_x + 4, block_y + 4, 6, 6))

def draw_piece(piece, offset_x=0, offset_y=0):
    for iy, row in enumerate(piece.shape):
        for ix, cell in enumerate(row):
            if cell:
                draw_block(piece.color, piece.x + ix + offset_x, piece.y + iy + offset_y)

def draw_glass_frame(x, y, w, h, title=""):
    glass = pygame.Surface((w, h), pygame.SRCALPHA)
    glass.fill((20, 60, 120, 100))
    screen.blit(glass, (x, y))
    pygame.draw.rect(screen, NEON_CYAN, (x, y, w, h), 5)
    pygame.draw.rect(screen, GLASS_BLUE, (x + 5, y + 5, w - 10, h - 10), 3)
    if title:
        title_surf = font_medium.render(title, True, NEON_CYAN)
        screen.blit(title_surf, (x + (w - title_surf.get_width()) // 2, y + 10))

def draw_main_frame():
    frame_w = GRID_WIDTH * BLOCK_SIZE + 30
    frame_h = GRID_HEIGHT * BLOCK_SIZE + 30
    draw_glass_frame(GRID_X - 15, GRID_Y - 15, frame_w, frame_h)
   
    pygame.draw.rect(screen, GLASS_BLUE, (GRID_X - 15, GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 5, frame_w, 20), border_radius=8)
    pygame.draw.rect(screen, NEON_CYAN, (GRID_X - 15, GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 5, frame_w, 20), 4, border_radius=8)

def draw_sidebar(next_piece, score, highscore):
    draw_glass_frame(SIDEBAR_X + 10, 130, 260, 140, "TIẾP")
    draw_next_piece(next_piece)
    
    level = 1 + (score // 500)
    draw_glass_frame(SIDEBAR_X + 10, 290, 260, 100, "CẤP")
    level_text = font_big.render(str(level), True, NEON_BLUE)
    screen.blit(level_text, (SIDEBAR_X + 140 - level_text.get_width() // 2, 330))
    
    draw_glass_frame(SIDEBAR_X + 10, 410, 260, 100, "ĐIỂM CAO NHẤT")
    high_text = font_big.render(str(highscore), True, NEON_BLUE)
    screen.blit(high_text, (SIDEBAR_X + 140 - high_text.get_width() // 2, 460))
    
    draw_glass_frame(SIDEBAR_X + 10, 530, 260, 100, "ĐIỂM HIỆN TẠI")
    score_text = font_big.render(str(score), True, NEON_YELLOW)
    screen.blit(score_text, (SIDEBAR_X + 140 - score_text.get_width() // 2, 580))
    
def draw_control_buttons(sound_on):
    btn_size = 40          
    btn_y = 25             
    
    volume_rect = pygame.Rect(SCREEN_WIDTH - 170, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, volume_rect, border_radius=10)
    pygame.draw.rect(screen, GLASS_BLUE, (volume_rect.x + 3, volume_rect.y + 3, btn_size - 6, btn_size - 6), border_radius=8)
def draw_control_buttons(sound_on):
    btn_size = 40
    btn_y = 25

   # vẽ nút âm lượng
    volume_rect = pygame.Rect(SCREEN_WIDTH - 170, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, volume_rect, border_radius=10)
    pygame.draw.rect(
        screen, GLASS_BLUE,
        (volume_rect.x + 3, volume_rect.y + 3, btn_size - 6, btn_size - 6),
        border_radius=8
    )

    cx, cy = volume_rect.center

    # Thân loa
    speaker = [
        (cx - 10, cy - 6),
        (cx - 4, cy - 6),
        (cx + 2, cy - 12),
        (cx + 2, cy + 12),
        (cx - 4, cy + 6),
        (cx - 10, cy + 6)
    ]
    pygame.draw.polygon(screen, NEON_YELLOW, speaker)

    if sound_on:
        # Sóng âm
        pygame.draw.arc(
            screen, NEON_YELLOW,
            (cx - 7, cy - 14, 18, 28), -0.8, 0.8, 2
        )
        pygame.draw.arc(
            screen, NEON_YELLOW,
            (cx - 6, cy - 18, 24, 36), -0.8, 0.8, 2
        )
    else:
        # Dấu X khi tắt
        pygame.draw.line(
            screen, NEON_YELLOW,
            (cx + 4, cy - 10),
            (cx + 18, cy + 10), 3
        )
        pygame.draw.line(
            screen, NEON_YELLOW,
            (cx + 18, cy - 10),
            (cx + 4, cy + 10), 3
        )

    # ===== PAUSE BUTTON =====
    pause_rect = pygame.Rect(SCREEN_WIDTH - 115, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, pause_rect, border_radius=10)
    pygame.draw.rect(
        screen, GLASS_BLUE,
        (pause_rect.x + 3, pause_rect.y + 3, btn_size - 6, btn_size - 6),
        border_radius=8
    )
    pygame.draw.rect(screen, NEON_YELLOW, (pause_rect.x + 10, pause_rect.y + 10, 6, 20), border_radius=2)
    pygame.draw.rect(screen, NEON_YELLOW, (pause_rect.x + 24, pause_rect.y + 10, 6, 20), border_radius=2)

    # ===== EXIT BUTTON =====
    exit_rect = pygame.Rect(SCREEN_WIDTH - 60, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, exit_rect, border_radius=10)
    pygame.draw.rect(
        screen, GLASS_BLUE,
        (exit_rect.x + 3, exit_rect.y + 3, btn_size - 6, btn_size - 6),
        border_radius=8
    )
    pygame.draw.line(screen, NEON_YELLOW, (exit_rect.x + 10, exit_rect.y + 10),
                     (exit_rect.x + 30, exit_rect.y + 30), 4)
    pygame.draw.line(screen, NEON_YELLOW, (exit_rect.x + 30, exit_rect.y + 10),
                     (exit_rect.x + 10, exit_rect.y + 30), 4)

    
    pause_rect = pygame.Rect(SCREEN_WIDTH - 115, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, pause_rect, border_radius=10)
    pygame.draw.rect(screen, GLASS_BLUE, (pause_rect.x + 3, pause_rect.y + 3, btn_size - 6, btn_size - 6), border_radius=8)
    pygame.draw.rect(screen, NEON_YELLOW, (pause_rect.x + 10, pause_rect.y + 10, 6, 20), border_radius=2)
    pygame.draw.rect(screen, NEON_YELLOW, (pause_rect.x + 24, pause_rect.y + 10, 6, 20), border_radius=2)
    
    exit_rect = pygame.Rect(SCREEN_WIDTH - 60, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, exit_rect, border_radius=10)
    pygame.draw.rect(screen, GLASS_BLUE, (exit_rect.x + 3, exit_rect.y + 3, btn_size - 6, btn_size - 6), border_radius=8)
    pygame.draw.line(screen, NEON_YELLOW, (exit_rect.x + 10, exit_rect.y + 10), (exit_rect.x + 30, exit_rect.y + 30), 4)
    pygame.draw.line(screen, NEON_YELLOW, (exit_rect.x + 30, exit_rect.y + 10), (exit_rect.x + 10, exit_rect.y + 30), 4)

def draw_start_screen():
    screen.fill(DARK_BLUE)
    title1 = font_title_big.render("XẾP HÌNH", True, ORANGE)
    screen.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 200))
    
    play_x = SCREEN_WIDTH // 2 - 50
    play_y = 400
    pygame.draw.rect(screen, NEON_BLUE, (play_x, play_y, 100, 100), border_radius=20)
    pygame.draw.rect(screen, GLASS_BLUE, (play_x + 5, play_y + 5, 90, 90), border_radius=15)
    pygame.draw.polygon(screen, NEON_YELLOW, [(play_x + 30, play_y + 20), (play_x + 30, play_y + 80), (play_x + 80, play_y + 50)])

def draw_pause_screen():
    screen.fill(DARK_BLUE)
    title = font_title_big.render("TẠM DỪNG", True, ORANGE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
    continue_x = SCREEN_WIDTH // 2 - 50
    continue_y = 400
    pygame.draw.rect(screen, NEON_BLUE, (continue_x, continue_y, 100, 100), border_radius=20)
    pygame.draw.rect(screen, GLASS_BLUE, (continue_x + 5, continue_y + 5, 90, 90), border_radius=15)
    pygame.draw.polygon(screen, NEON_YELLOW, [(continue_x + 25, continue_y + 20), (continue_x + 25, continue_y + 80), (continue_x + 55, continue_y + 50)])
    pygame.draw.polygon(screen, NEON_YELLOW, [(continue_x + 55, continue_y + 20), (continue_x + 55, continue_y + 80), (continue_x + 85, continue_y + 50)])

def draw_new_game_over(level, score, highscore):
    screen.fill(DARK_BLUE)
    
    go_text = font_title_big.render("GAME OVER", True, NEON_YELLOW)
    screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 100))
    
    cap_text = font_medium.render("CẤP", True, NEON_CYAN)
    high_text = font_medium.render("ĐIỂM CAO NHẤT", True, NEON_CYAN)
    
    total_width = cap_text.get_width() + high_text.get_width() + 120
    start_x = SCREEN_WIDTH // 2 - total_width // 2
    
    screen.blit(cap_text, (start_x, 220))
    screen.blit(high_text, (start_x + cap_text.get_width() + 120, 220))
    
    level_text = font_big.render(str(level), True, NEON_YELLOW)
    highscore_text = font_big.render(str(highscore), True, NEON_YELLOW)
    
    screen.blit(level_text, (start_x + cap_text.get_width() // 2 - level_text.get_width() // 2, 280))
    screen.blit(highscore_text, (start_x + cap_text.get_width() + 120 + high_text.get_width() // 2 - highscore_text.get_width() // 2, 280))
    
    your_score_text = font_medium.render("ĐIỂM CỦA BẠN", True, NEON_CYAN)
    score_text = font_big.render(str(score), True, NEON_YELLOW)
    screen.blit(your_score_text, (SCREEN_WIDTH // 2 - your_score_text.get_width() // 2, 420))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 480))
    
    home_x = SCREEN_WIDTH // 2 - 33
    home_y = 580
    pygame.draw.rect(screen, GLASS_BLUE, (home_x - 10, home_y - 10, 80, 80), border_radius=15)
    pygame.draw.rect(screen, NEON_BLUE, (home_x - 10, home_y - 10, 80, 80), 5, border_radius=15)
    house_offset_x = -10
    house_offset_y = -5
    
    pygame.draw.polygon(screen, NEON_YELLOW, [
        (home_x + 40 + house_offset_x, home_y + 5 + house_offset_y),
        (home_x + 10 + house_offset_x, home_y + 35 + house_offset_y),
        (home_x + 70 + house_offset_x, home_y + 35 + house_offset_y)
    ])
    pygame.draw.rect(screen, NEON_YELLOW, 
                     (home_x + 20 + house_offset_x, home_y + 35 + house_offset_y, 40, 35))
    
def draw_confirm_quit():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    box_w = 400
    box_h = 200
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = SCREEN_HEIGHT // 2 - box_h // 2
    
    draw_glass_frame(box_x, box_y, box_w, box_h)
    
    text = font_big.render("BẠN CHẮC THOÁT?", True, NEON_YELLOW)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, box_y + 50))
    
    yes_x = SCREEN_WIDTH // 2 - 90
    yes_y = box_y + 110
    yes_rect = pygame.Rect(yes_x, yes_y, 70, 70)
    pygame.draw.rect(screen, NEON_GREEN, yes_rect, border_radius=15)
    pygame.draw.rect(screen, GLASS_BLUE, (yes_x + 5, yes_y + 5, 60, 60), border_radius=10)
    pygame.draw.line(screen, NEON_YELLOW, (yes_x + 15, yes_y + 35), (yes_x + 30, yes_y + 50), 6)
    pygame.draw.line(screen, NEON_YELLOW, (yes_x + 30, yes_y + 50), (yes_x + 55, yes_y + 20), 6)
    
    no_x = SCREEN_WIDTH // 2 + 20
    no_y = box_y + 110
    no_rect = pygame.Rect(no_x, no_y, 70, 70)
    pygame.draw.rect(screen, RED, no_rect, border_radius=15)
    pygame.draw.rect(screen, GLASS_BLUE, (no_x + 5, no_y + 5, 60, 60), border_radius=10)
    pygame.draw.line(screen, NEON_YELLOW, (no_x + 15, no_y + 15), (no_x + 55, no_y + 55), 6)
    pygame.draw.line(screen, NEON_YELLOW, (no_x + 55, no_y + 15), (no_x + 15, no_y + 55), 6)
    
    return yes_rect, no_rect

def get_fall_speed(score):
    level = 1 + (score // 500)
    if level == 1:
        return 0.8
    else:
        return max(0.45 - 0.05 * (level - 2), 0.05)

def main():
    global sound_on, bg_channel
    highscore = load_highscore()

    def reset_game():
        nonlocal score, locked, current_piece, next_piece, fall_time, fall_speed, game_over, paused, current_level
        score = 0
        locked = {}
        current_piece = Tetromino()
        next_piece = Tetromino()
        fall_time = 0
        fall_speed = 0.5
        game_over = False
        paused = False
        current_level = 1
        play_background_music()

    reset_game()
    in_start_screen = True
    confirm_quit = False

    play_background_music()

    das_left_time = 0
    das_right_time = 0
    das_delay = 0.15
    arr_speed = 0.04

    yes_rect = None
    no_rect = None

    while True:
        clock.tick(120)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_background_music()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if sound_on:
                    play_sound('button')

                if confirm_quit and yes_rect and no_rect:
                    if yes_rect.collidepoint(mx, my):
                        in_start_screen = True
                        reset_game()
                        confirm_quit = False
                    elif no_rect.collidepoint(mx, my):
                        confirm_quit = False

                if not in_start_screen and not paused and not game_over and not confirm_quit:
                    volume_rect = pygame.Rect(SCREEN_WIDTH - 170, 25, 40, 40)
                    pause_rect = pygame.Rect(SCREEN_WIDTH - 115, 25, 40, 40)
                    exit_rect = pygame.Rect(SCREEN_WIDTH - 60, 25, 40, 40)
                    
                    if volume_rect.collidepoint(mx, my):
                        
                        sound_on = not sound_on
                        if sound_on:
                            play_sound('button')
                            play_background_music()
                           
                        else:
                            stop_background_music()
                    if pause_rect.collidepoint(mx, my):
                        paused = True
                    if exit_rect.collidepoint(mx, my):
                        confirm_quit = True

            if in_start_screen:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if SCREEN_WIDTH // 2 - 50 <= mx <= SCREEN_WIDTH // 2 + 50 and 400 <= my <= 500:
                        in_start_screen = False
                        reset_game()
                continue

            if paused:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if SCREEN_WIDTH // 2 - 50 <= mx <= SCREEN_WIDTH // 2 + 50 and 400 <= my <= 500:
                        paused = False
                continue

            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    home_rect = pygame.Rect(SCREEN_WIDTH // 2 - 43, 570, 80, 80)
                    if home_rect.collidepoint(mx, my):
                        if sound_on:
                            play_sound('button')
                        stop_background_music()        
                        pygame.mixer.stop()
                        in_start_screen = True
                        reset_game()
                continue

            if not confirm_quit:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:          
                     paused = not paused
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

                keys = pygame.key.get_pressed()
                
                dt = clock.get_time() / 1000.0
            
                SOFT_DROP_SPEED = 0.02  
                if keys[pygame.K_DOWN]:
                 fall_speed = SOFT_DROP_SPEED
                else:
                    fall_speed = get_fall_speed(score)  # Tốc độ bình thường theo level
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

        if in_start_screen:
            draw_start_screen()

        elif paused:
            draw_pause_screen()

        elif game_over:
            draw_new_game_over(current_level, score, highscore)

        elif confirm_quit:
            screen.fill(DARK_BLUE)
            draw_main_frame()
            draw_grid_lines()
            for (gx, gy), color in locked.items():
                draw_block(color, gx, gy)
            draw_piece(current_piece)
            draw_sidebar(next_piece, score, highscore)
            draw_control_buttons(sound_on)
            yes_rect, no_rect = draw_confirm_quit()

        else:
            screen.fill(DARK_BLUE)
            draw_main_frame()
            draw_grid_lines()
            for (gx, gy), color in locked.items():
                draw_block(color, gx, gy)
            draw_piece(current_piece)
            draw_sidebar(next_piece, score, highscore)
            draw_control_buttons(sound_on)

            fall_time += clock.get_time() / 1000.0
            if fall_time >= fall_speed:
                fall_time = 0
                if valid_move(current_piece, create_grid(locked), dy=1):
                    current_piece.y += 1
                else:
                    for iy, row in enumerate(current_piece.shape):
                        for ix, cell in enumerate(row):
                            if cell:
                                locked[(current_piece.x + ix, current_piece.y + iy)] = current_piece.color
                    
                    lines, locked = clear_lines(locked)
                    points = [0, 50, 200, 300, 400]
                    if 0 < lines <= 4:
                        score += points[lines]
                        if sound_on:
                            if lines == 1:
                                play_sound('clear_single')
                            elif lines >= 2:
                                play_sound('clear_multi')

                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)
                        play_sound('new_record')
                    
                    fall_speed = get_fall_speed(score)
                    current_level = 1 + (score // 500)
                    current_piece = next_piece
                    next_piece = Tetromino()
                    
                    if not valid_move(current_piece, create_grid(locked)):
                        game_over = True
                        stop_background_music()
                        play_sound('gameover')

        pygame.display.update()

if __name__ == "__main__":
    main()