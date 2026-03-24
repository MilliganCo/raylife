import pygame
import sys
import math
import random

# ---------- ПАРАМЕТРЫ ----------

# Размер сетки
GRID_WIDTH = 80
GRID_HEIGHT = 60

# Размер клетки (в пикселях)
CELL_SIZE = 10

# Размер окна
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Частота кадров
FPS = 30

# Список доступных цветов (кроме None = "мёртвой" клетки).
# Можно расширять. Здесь некоторые яркие, некоторые более приглушённые.
PALETTE = [
    (80, 80, 80),
    (128, 128, 255),
    (255, 128, 128),
    (128, 255, 128),
    (200, 100, 100),
    (100, 200, 200),
    (255, 255, 128),
    (128, 255, 255),
    (255, 128, 255),
    (180, 180, 220),
    (220, 180, 180),
    (180, 220, 180),
    (255, 200, 80),
    (200, 255, 80),
    (80, 200, 255),
]

# Индексы палитры, которые будем выбирать клавишами 1..9 (ограничимся 9-ю).
# Можно назначить любые индексы. Например, первые 9 цветов.
PALETTE_KEYS = [i for i in range(9)]  # индексы 0..8

# Цвет сетки и фона
COLOR_GRID = (40, 40, 40)
COLOR_BG = (10, 10, 10)

# Параметры лучей
LIGHT_SOURCES = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]  # один источник в центре
RAY_STEP_SIZE = 4  # Шаг, с которым луч «пробегает» пиксели
RAY_MAX_DISTANCE = max(SCREEN_WIDTH, SCREEN_HEIGHT)  # Длина до края экрана
RAY_ANGLE_STEP = 3  # Чем меньше, тем больше лучей
RAY_THICKNESS = 3  # Толщина луча
RAY_ALPHA_START = 180  # Начальная непрозрачность (0..255)
RAY_ALPHA_FADE = 0.7  # Скорость затухания прозрачности с расстоянием


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def mix_colors(c1, c2, ratio=0.5):
    """
    Простейшее смешение двух цветов c1 и c2 (кортежи (R,G,B)).
    ratio определяет долю второго цвета.
    """
    if c1 is None:
        return c2
    if c2 is None:
        return c1
    r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
    g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
    b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
    return (r, g, b)


def average_colors(colors):
    """Среднее (по каналам) из списка цветов (без None)."""
    if not colors:
        return None
    r = sum(c[0] for c in colors) // len(colors)
    g = sum(c[1] for c in colors) // len(colors)
    b = sum(c[2] for c in colors) // len(colors)
    return (r, g, b)


# ---------- ЛОГИКА КЛЕТОЧНОГО АВТОМАТА С ЦВЕТОМ ----------

class GameOfLifeColored:
    """
    В grid храним либо None (мертвая клетка), либо (R,G,B).
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def randomize_grid(self):
        """Случайная инициализация."""
        for i in range(self.height):
            for j in range(self.width):
                if random.random() < 0.2:  # 20% шанс
                    self.grid[i][j] = random.choice(PALETTE)
                else:
                    self.grid[i][j] = None

    def count_live_neighbors(self, x, y):
        """Считает живых соседей (возвращает список их цветов, без None)."""
        neighbors = []
        for nx in range(max(0, x - 1), min(self.height, x + 2)):
            for ny in range(max(0, y - 1), min(self.width, y + 2)):
                if (nx, ny) != (x, y):
                    c = self.grid[nx][ny]
                    if c is not None:
                        neighbors.append(c)
        return neighbors

    def update(self):
        """
        Правила Game of Life:
        - Клетка (x,y) жива, если grid[x][y] != None.
        - Подсчёт соседей: количество клеток != None вокруг.
        - Выживает, если 2 или 3 соседа, иначе умирает (None).
        - Рождается, если ровно 3 соседа, цвет = среднее от соседей.
        - (Дополнительно) Если клетка выживает, можно «подмешать» цвета соседей.
        """
        new_grid = [[None for _ in range(self.width)] for _ in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                neighbors_colors = self.count_live_neighbors(i, j)
                live_neighbors = len(neighbors_colors)
                current_color = self.grid[i][j]

                if current_color is not None:
                    # Клетка жива
                    if live_neighbors in (2, 3):
                        # Выживает
                        # Подмешаем цвета соседей + свой собственный
                        all_colors = [current_color] + neighbors_colors
                        new_grid[i][j] = average_colors(all_colors)
                    else:
                        # Умирает
                        new_grid[i][j] = None
                else:
                    # Клетка мертва
                    if live_neighbors == 3:
                        # Рождается
                        # Цвет = среднее от соседей
                        new_grid[i][j] = average_colors(neighbors_colors)
                    else:
                        new_grid[i][j] = None

        self.grid = new_grid

    def set_cell_color(self, x, y, color):
        """Устанавливает цвет клетки (x, y) в (R,G,B)."""
        if 0 <= x < self.height and 0 <= y < self.width:
            self.grid[x][y] = color


# ---------- ЛУЧИ (МЯГКАЯ ОТРИСОВКА) ----------

def draw_soft_rays(surface, grid):
    """
    Рисуем «мягкие» лучи из всех LIGHT_SOURCES до края экрана.
    - Шаг луча: RAY_STEP_SIZE
    - Цвет луча: изначально белый (255,255,255)
    - При прохождении через цветную клетку луч постепенно "подкрашивается"
      (для простоты берём среднее между текущим цветом луча и цветом клетки).
    - Интенсивность луча уменьшается с расстоянием (alpha).
    """
    rays_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for source in LIGHT_SOURCES:
        sx, sy = source
        for angle_deg in range(0, 360, RAY_ANGLE_STEP):
            angle = math.radians(angle_deg)
            # Луч изначально белый
            ray_color = (255, 255, 255)
            distance = 0
            while True:
                distance += RAY_STEP_SIZE
                x = sx + math.cos(angle) * distance
                y = sy + math.sin(angle) * distance

                # Если вышли за границы - остановиться
                if not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                    break

                # Проверка клетки
                gx = int(y // CELL_SIZE)
                gy = int(x // CELL_SIZE)
                cell_color = grid[gx][gy]

                if cell_color is not None:
                    # Подкрашиваем луч
                    ray_color = mix_colors(ray_color, cell_color, ratio=0.3)

                # Рассчитываем прозрачность по расстоянию
                alpha = int(RAY_ALPHA_START - distance * RAY_ALPHA_FADE)
                if alpha <= 0:
                    break

                # Рисуем маленькую «точку» (или можно линию)
                # Цвет в формате RGBA
                draw_color = (ray_color[0], ray_color[1], ray_color[2], alpha)
                pygame.draw.circle(rays_surface, draw_color, (int(x), int(y)), RAY_THICKNESS)

                if distance >= RAY_MAX_DISTANCE:
                    break

    # Наложим слой с лучами поверх экрана
    surface.blit(rays_surface, (0, 0))


# ---------- ОСНОВНОЙ ЦИКЛ ИГРЫ ----------

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Colored Game of Life with Soft Rays")
    clock = pygame.time.Clock()

    game = GameOfLifeColored(GRID_WIDTH, GRID_HEIGHT)
    # Если нужно случайно заполнить сетку:
    # game.randomize_grid()

    paused = True  # Изначально на паузе
    current_color_index = 0  # Индекс в PALETTE

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Клавиши 1..9 меняют цвет рисования
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if 0 <= idx < len(PALETTE_KEYS):
                        current_color_index = PALETTE_KEYS[idx]
                # F - переключение паузы
                if event.key == pygame.K_f:
                    paused = not paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # При нажатии ЛКМ тоже ставим клетку (но рисовать будем в MOUSEMOTION)
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    gx = my // CELL_SIZE
                    gy = mx // CELL_SIZE
                    game.set_cell_color(gx, gy, PALETTE[current_color_index])
            elif event.type == pygame.MOUSEMOTION:
                # Если зажата ЛКМ, «рисуем» по сетке
                if event.buttons[0]:  # левая кнопка
                    mx, my = event.pos
                    gx = my // CELL_SIZE
                    gy = mx // CELL_SIZE
                    if 0 <= gx < GRID_HEIGHT and 0 <= gy < GRID_WIDTH:
                        game.set_cell_color(gx, gy, PALETTE[current_color_index])

        # Обновление автомата, если не на паузе
        if not paused:
            game.update()

        # Отрисовка
        screen.fill(COLOR_BG)

        # Рисуем клетки
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                c = game.grid[i][j]
                if c is not None:
                    pygame.draw.rect(screen, c, rect)
                pygame.draw.rect(screen, COLOR_GRID, rect, 1)

        # Рисуем «мягкие» лучи
        draw_soft_rays(screen, game.grid)

        # Отрисуем источник(и) света жёлтым кружком (для наглядности)
        for (sx, sy) in LIGHT_SOURCES:
            pygame.draw.circle(screen, (255, 255, 0), (sx, sy), 5)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
