# main.py

import pygame
import sys

import config
from game_of_life import GameOfLifeColored
from ray_tracer import draw_soft_rays

def draw_grid(screen, game):
    """Отрисовка клеток и сетки."""
    for i in range(game.height):
        for j in range(game.width):
            rect = pygame.Rect(j*config.CELL_SIZE, i*config.CELL_SIZE,
                               config.CELL_SIZE, config.CELL_SIZE)
            cell = game.grid[i][j]
            if cell is not None:
                pygame.draw.rect(screen, cell["color"], rect)
            pygame.draw.rect(screen, config.COLOR_GRID, rect, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Colored Game of Life with Different Cell Behaviors & Soft Rays")
    clock = pygame.time.Clock()

    game = GameOfLifeColored(config.GRID_WIDTH, config.GRID_HEIGHT)
    # При желании — случайная инициализация
    # game.randomize(probability=0.3)

    paused = config.START_PAUSED
    current_cell_type = 1  # по умолчанию выберем первый тип из CELL_TYPES

    running = True
    while running:
        # --- ОБРАБОТКА СОБЫТИЙ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Клавиши 1..9 для выбора типа клетки
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1  # 0..8
                    if idx < len(config.CELL_KEYS):
                        current_cell_type = config.CELL_KEYS[idx]

                # Клавиша F - пауза
                if event.key == pygame.K_f:
                    paused = not paused

            elif event.type == pygame.MOUSEMOTION:
                # Зажатая ЛКМ -> рисуем текущим типом
                if event.buttons[0]:
                    mx, my = event.pos
                    gx = my // config.CELL_SIZE
                    gy = mx // config.CELL_SIZE
                    game.set_cell(gx, gy, current_cell_type)
                # Зажатая ПКМ -> стираем
                if event.buttons[2]:
                    mx, my = event.pos
                    gx = my // config.CELL_SIZE
                    gy = mx // config.CELL_SIZE
                    game.set_cell(gx, gy, 0)  # 0 = стереть (None)

        # --- ОБНОВЛЕНИЕ ---
        if not paused:
            game.update()

        # --- ОТРИСОВКА ---
        screen.fill(config.COLOR_BG)

        # Рисуем клетки
        draw_grid(screen, game)

        # Рисуем мягкие лучи
        draw_soft_rays(screen, game.grid)

        # Отрисовываем источники света (для наглядности)
        for (sx, sy) in config.LIGHT_SOURCES:
            pygame.draw.circle(screen, (255, 255, 0), (sx, sy), 5)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
