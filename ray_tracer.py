# ray_tracer.py

import pygame
import math
import config

def mix_colors(c1, c2, ratio=0.5):
    """Простая функция смешения (R,G,B)."""
    r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
    g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
    b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
    return (r, g, b)

def reflect_angle(angle):
    """Разворот луча на config.REFLECTION_ANGLE_DEG градусов (по умолчанию 180)."""
    return angle + math.radians(config.REFLECTION_ANGLE_DEG)

def draw_soft_rays(surface, grid):
    """
    Рисуем «мягкие» лучи из всех источников:
    - Шаг луча = RAY_STEP_SIZE
    - Цвет луча = (255,255,255) в начале (можно менять).
    - При встрече с клеткой меняем поведение:
      pass    -> смешиваем цвет луча с цветом клетки
      reflect -> разворачиваем луч, продолжаем
      absorb  -> прерываем луч
    - alpha уменьшается с расстоянием, формируя "прозрачный шлейф".
    """
    rays_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)

    for source in config.LIGHT_SOURCES:
        sx, sy = source
        for angle_deg in range(0, 360, config.RAY_ANGLE_STEP):
            angle = math.radians(angle_deg)
            ray_color = (255, 255, 255)  # начальный цвет луча
            distance = 0.0
            alpha = config.RAY_ALPHA_START

            # Копируем угол, чтобы можно было несколько раз отразиться (по желанию)
            current_angle = angle

            while True:
                distance += config.RAY_STEP_SIZE
                x = sx + math.cos(current_angle) * distance
                y = sy + math.sin(current_angle) * distance

                # Выходим, если за границей
                if not (0 <= x < config.SCREEN_WIDTH and 0 <= y < config.SCREEN_HEIGHT):
                    break

                # Коэффициент затухания
                alpha = config.RAY_ALPHA_START - distance * config.RAY_ALPHA_FADE
                if alpha <= 0:
                    break

                # Рисуем круг с текущим цветом и альфой
                draw_color = (ray_color[0], ray_color[1], ray_color[2], int(alpha))
                pygame.draw.circle(rays_surface, draw_color, (int(x), int(y)), config.RAY_THICKNESS)

                # Проверяем клетку
                gx = int(y // config.CELL_SIZE)
                gy = int(x // config.CELL_SIZE)
                cell = grid[gx][gy]

                if cell is not None:
                    bh = cell["behavior"]
                    c = cell["color"]

                    if bh == "pass":
                        # Подмешиваем цвет клетки в луч
                        ray_color = mix_colors(ray_color, c, 0.3)
                        # Луч продолжает движение
                    elif bh == "reflect":
                        # Подмешиваем цвет клетки
                        ray_color = mix_colors(ray_color, c, 0.3)
                        # Разворачиваем угол
                        current_angle = reflect_angle(current_angle)
                    elif bh == "absorb":
                        # Луч гаснет
                        break

                # Проверка дистанции
                if distance >= config.RAY_MAX_DISTANCE:
                    break

    surface.blit(rays_surface, (0, 0))
