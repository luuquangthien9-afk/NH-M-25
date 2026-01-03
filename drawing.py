import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_X, GRID_Y, BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT,
    SIDEBAR_X, DARK_BLUE, GLASS_BLUE, NEON_BLUE, NEON_CYAN, NEON_YELLOW,
    NEON_GREEN, RED, ORANGE, font_medium, font_big  # font sẽ được truyền từ main nếu cần
)

def draw_block(screen, color, grid_x, grid_y):
    x = GRID_X + grid_x * BLOCK_SIZE
    y = GRID_Y + grid_y * BLOCK_SIZE
    shadow = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 15))
    screen.blit(shadow, (x + 4, y + 4))
    pygame.draw.rect(screen, color, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
    pygame.draw.rect(screen, (255, 255, 255, 50), (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)
    pygame.draw.rect(screen, (255, 255, 255, 80), (x + 4, y + 4, 6, 6))

def draw_grid_lines(screen):
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, (30, 50, 80),
                         (GRID_X + x * BLOCK_SIZE, GRID_Y),
                         (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT * BLOCK_SIZE))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, (30, 50, 80),
                         (GRID_X, GRID_Y + y * BLOCK_SIZE),
                         (GRID_X + GRID_WIDTH * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE))

def draw_next_piece(screen, piece):
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

def draw_piece(screen, piece, offset_x=0, offset_y=0):
    for iy, row in enumerate(piece.shape):
        for ix, cell in enumerate(row):
            if cell:
                draw_block(screen, piece.color, piece.x + ix + offset_x, piece.y + iy + offset_y)

def draw_glass_frame(screen, x, y, w, h, title=""):
    glass = pygame.Surface((w, h), pygame.SRCALPHA)
    glass.fill((20, 60, 120, 100))
    screen.blit(glass, (x, y))
    pygame.draw.rect(screen, NEON_CYAN, (x, y, w, h), 5)
    pygame.draw.rect(screen, GLASS_BLUE, (x + 5, y + 5, w - 10, h - 10), 3)
    if title:
        title_surf = font_medium.render(title, True, NEON_CYAN)
        screen.blit(title_surf, (x + (w - title_surf.get_width()) // 2, y + 10))

def draw_main_frame(screen):
    frame_w = GRID_WIDTH * BLOCK_SIZE + 30
    frame_h = GRID_HEIGHT * BLOCK_SIZE + 30
    draw_glass_frame(screen, GRID_X - 15, GRID_Y - 15, frame_w, frame_h)
   
    pygame.draw.rect(screen, GLASS_BLUE, (GRID_X - 15, GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 5, frame_w, 20), border_radius=8)
    pygame.draw.rect(screen, NEON_CYAN, (GRID_X - 15, GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 5, frame_w, 20), 4, border_radius=8)

def draw_sidebar(screen, next_piece, score, highscore, font_big, font_medium):
    draw_glass_frame(screen, SIDEBAR_X + 10, 130, 260, 140, "TIẾP")
    draw_next_piece(screen, next_piece)
    
    level = 1 + (score // 1000)
    draw_glass_frame(screen, SIDEBAR_X + 10, 290, 260, 100, "CẤP")
    level_text = font_big.render(str(level), True, NEON_BLUE)
    screen.blit(level_text, (SIDEBAR_X + 140 - level_text.get_width() // 2, 330))
    
    draw_glass_frame(screen, SIDEBAR_X + 10, 410, 260, 100, "ĐIỂM CAO NHẤT")
    high_text = font_big.render(str(highscore), True, NEON_BLUE)
    screen.blit(high_text, (SIDEBAR_X + 140 - high_text.get_width() // 2, 460))
    
    draw_glass_frame(screen, SIDEBAR_X + 10, 530, 260, 100, "ĐIỂM HIỆN TẠI")
    score_text = font_big.render(str(score), True, NEON_YELLOW)
    screen.blit(score_text, (SIDEBAR_X + 140 - score_text.get_width() // 2, 580))

def draw_control_buttons(screen, sound_on):
    btn_size = 40          
    btn_y = 25             
    
    volume_rect = pygame.Rect(SCREEN_WIDTH - 170, btn_y, btn_size, btn_size)
    pygame.draw.rect(screen, NEON_BLUE, volume_rect, border_radius=10)
    pygame.draw.rect(screen, GLASS_BLUE, (volume_rect.x + 3, volume_rect.y + 3, btn_size - 6, btn_size - 6), border_radius=8)
    if sound_on:
        pygame.draw.circle(screen, NEON_YELLOW, (volume_rect.centerx - 6, volume_rect.centery), 6)
        pygame.draw.circle(screen, NEON_YELLOW, (volume_rect.centerx + 5, volume_rect.centery - 5), 4)
        pygame.draw.circle(screen, NEON_YELLOW, (volume_rect.centerx + 5, volume_rect.centery + 5), 4)
        pygame.draw.line(screen, NEON_YELLOW, (volume_rect.centerx + 14, volume_rect.centery - 8), (volume_rect.centerx + 14, volume_rect.centery + 8), 2)
    else:
        pygame.draw.line(screen, NEON_YELLOW, (volume_rect.centerx - 12, volume_rect.centery - 12), (volume_rect.centerx + 12, volume_rect.centery + 12), 3)
    
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

def draw_start_screen(screen, font_title_big):
    screen.fill(DARK_BLUE)
    title1 = font_title_big.render("XẾP HÌNH", True, ORANGE)
    screen.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 200))
    
    play_x = SCREEN_WIDTH // 2 - 50
    play_y = 400
    pygame.draw.rect(screen, NEON_BLUE, (play_x, play_y, 100, 100), border_radius=20)
    pygame.draw.rect(screen, GLASS_BLUE, (play_x + 5, play_y + 5, 90, 90), border_radius=15)
    pygame.draw.polygon(screen, NEON_YELLOW, [(play_x + 30, play_y + 20), (play_x + 30, play_y + 80), (play_x + 80, play_y + 50)])

def draw_pause_screen(screen, font_title_big):
    screen.fill(DARK_BLUE)
    title = font_title_big.render("TẠM DỪNG", True, ORANGE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
    continue_x = SCREEN_WIDTH // 2 - 50
    continue_y = 400
    pygame.draw.rect(screen, NEON_BLUE, (continue_x, continue_y, 100, 100), border_radius=20)
    pygame.draw.rect(screen, GLASS_BLUE, (continue_x + 5, continue_y + 5, 90, 90), border_radius=15)
    pygame.draw.polygon(screen, NEON_YELLOW, [(continue_x + 25, continue_y + 20), (continue_x + 25, continue_y + 80), (continue_x + 55, continue_y + 50)])
    pygame.draw.polygon(screen, NEON_YELLOW, [(continue_x + 55, continue_y + 20), (continue_x + 55, continue_y + 80), (continue_x + 85, continue_y + 50)])

def draw_new_game_over(screen, level, score, highscore, font_title_big, font_medium, font_big):
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

def draw_confirm_quit(screen, font_big):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    box_w = 400
    box_h = 200
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = SCREEN_HEIGHT // 2 - box_h // 2
    
    draw_glass_frame(screen, box_x, box_y, box_w, box_h)
    
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