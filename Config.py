import pygame

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

COLORS = [NEON_CYAN, NEON_YELLOW, NEON_PINK, NEON_GREEN, RED, NEON_BLUE, ORANGE]

# Kích thước
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = 100
GRID_Y = 80

SIDEBAR_X = GRID_X + GRID_WIDTH * BLOCK_SIZE + 50
SCREEN_WIDTH = SIDEBAR_X + 280
SCREEN_HEIGHT = GRID_Y + GRID_HEIGHT * BLOCK_SIZE + 120

# Hình dạng khối
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]
