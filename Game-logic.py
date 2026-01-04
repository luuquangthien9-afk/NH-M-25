import os
from config import GRID_WIDTH, GRID_HEIGHT, BLACK

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

def get_fall_speed(score):
    level = 1 + (score // 500)  # Sửa từ //1000 thành //500 để khớp xephinh.py
    if level == 1:
        return 0.8
    else:
        return max(0.45 - 0.05 * (level - 2), 0.05)
