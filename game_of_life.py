# game_of_life.py

import random
import config

def color_brightness(color):
    """Простейшая оценка яркости цвета (R,G,B)."""
    if color is None:
        return 0
    r, g, b = color
    return (r + g + b) / 3.0

def mix_colors(c1, c2, ratio=0.5):
    """Смешивание двух цветов (R,G,B) с заданной долей второго цвета."""
    if c1 is None:
        return c2
    if c2 is None:
        return c1
    r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
    g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
    b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
    return (r, g, b)

class GameOfLifeColored:
    """
    grid[x][y] = None или словарь {"color": (R,G,B), "behavior": str}
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def randomize(self, probability=0.2):
        """Случайная инициализация: с вероятностью probability клетка заполняется одним из CELL_TYPES."""
        keys = list(config.CELL_TYPES.keys())
        for i in range(self.height):
            for j in range(self.width):
                if random.random() < probability:
                    k = random.choice(keys)
                    # Создаём копию словаря, чтобы цвет мог меняться
                    cell_info = {
                        "color": config.CELL_TYPES[k]["color"],
                        "behavior": config.CELL_TYPES[k]["behavior"]
                    }
                    self.grid[i][j] = cell_info
                else:
                    self.grid[i][j] = None

    def count_live_neighbors(self, x, y):
        """Возвращает список словарей-соседей (без None)."""
        neighbors = []
        for nx in range(max(0, x-1), min(self.height, x+2)):
            for ny in range(max(0, y-1), min(self.width, y+2)):
                if (nx, ny) != (x, y):
                    if self.grid[nx][ny] is not None:
                        neighbors.append(self.grid[nx][ny])
        return neighbors

    def update(self):
        """
        Упрощённые правила Game of Life:
        - Клетка жива, если не None.
        - Подсчёт соседей = количество соседей != None.
        - 2 или 3 соседа -> клетка выживает, иначе умирает.
        - Ровно 3 соседа -> рождается новая клетка, цвет = среднее от соседей.
        - "Умное" смешение: при выживании цвет клетки подмешивается с цветами соседей.
        """
        new_grid = [[None for _ in range(self.width)] for _ in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                neighbors = self.count_live_neighbors(i, j)
                live_neighbors = len(neighbors)
                current_cell = self.grid[i][j]

                if current_cell is not None:
                    # Клетка жива
                    if live_neighbors in (2, 3):
                        # Выживает. Смешаем цвета всех соседей + свой
                        mixed_color = current_cell["color"]
                        for neigh in neighbors:
                            mixed_color = mix_colors(mixed_color, neigh["color"], config.COLOR_MIX_RATIO / live_neighbors)
                        new_grid[i][j] = {
                            "color": mixed_color,
                            "behavior": current_cell["behavior"]
                        }
                    else:
                        # Умирает
                        new_grid[i][j] = None
                else:
                    # Пустая клетка
                    if live_neighbors == 3:
                        # Рождается. Цвет = среднее всех соседей
                        # Поведение берём у случайного соседа (или можно другое правило)
                        neighbor_colors = [n["color"] for n in neighbors]
                        neighbor_behaviors = [n["behavior"] for n in neighbors]

                        c = neighbor_colors[0]
                        for nc in neighbor_colors[1:]:
                            c = mix_colors(c, nc, config.COLOR_MIX_RATIO)

                        b = random.choice(neighbor_behaviors)
                        new_grid[i][j] = {
                            "color": c,
                            "behavior": b
                        }
                    else:
                        new_grid[i][j] = None

        self.grid = new_grid

    def set_cell(self, gx, gy, cell_type):
        """
        Устанавливает клетку по типу из config.CELL_TYPES,
        если cell_type == 0, то стираем (None).
        """
        if 0 <= gx < self.height and 0 <= gy < self.width:
            if cell_type == 0:
                self.grid[gx][gy] = None
            else:
                # Создаём копию
                base = config.CELL_TYPES[cell_type]
                self.grid[gx][gy] = {
                    "color": base["color"],
                    "behavior": base["behavior"]
                }
