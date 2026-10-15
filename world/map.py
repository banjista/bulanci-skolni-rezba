"""
Reprezentace školní mapy (učebna) s překážkami, lavicemi a tabulí.
Obsahuje kolizní geometrii pro pohyb polštářků i střel.
"""

import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG_FLOOR, COLOR_FLOOR_LINES,
    COLOR_WALL, COLOR_WALL_BORDER,
    COLOR_DESK, COLOR_DESK_BORDER,
    COLOR_CHAIR, COLOR_BLACKBOARD, COLOR_BLACKBOARD_FRAME,
    COLOR_KATEDRA, COLOR_DARK_GRAY, COLOR_WHITE, COLOR_YELLOW
)

class Obstacle:
    def __init__(self, rect, obs_type="desk", color=COLOR_DESK, border_color=COLOR_DESK_BORDER, label=None):
        self.rect = rect
        self.obs_type = obs_type
        self.color = color
        self.border_color = border_color
        self.label = label

    def draw(self, surface):
        if self.obs_type == "wall":
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, self.border_color, self.rect, width=3)
        
        elif self.obs_type == "blackboard":
            # Rám tabule
            pygame.draw.rect(surface, self.border_color, self.rect, border_radius=4)
            # Vnitřek tabule
            inner_rect = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, self.color, inner_rect, border_radius=3)
            # Křídová polička dole
            shelf_rect = pygame.Rect(self.rect.left + 15, self.rect.bottom - 4, self.rect.width - 30, 4)
            pygame.draw.rect(surface, (200, 200, 200), shelf_rect)
            # Kousky křídy na poličce
            pygame.draw.rect(surface, COLOR_WHITE, (self.rect.left + 25, self.rect.bottom - 6, 12, 3))
            pygame.draw.rect(surface, COLOR_YELLOW, (self.rect.left + 45, self.rect.bottom - 6, 10, 3))
            
            # Nápis na tabuli (např. 1 + 1 = 2 nebo IT Seminář)
            font = pygame.font.SysFont("comicsansms", 15, bold=True)
            text_surf = font.render("IT Seminář: Bulánci 2026", True, (200, 240, 210))
            text_rect = text_surf.get_rect(center=inner_rect.center)
            surface.blit(text_surf, text_rect)

        elif self.obs_type == "katedra":
            # Učitelský stůl
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=6)
            # Židle za katedrou
            chair_rect = pygame.Rect(self.rect.centerx - 22, self.rect.top - 16, 44, 14)
            pygame.draw.rect(surface, COLOR_CHAIR, chair_rect, border_radius=3)
            # Notebook učitele
            laptop_rect = pygame.Rect(self.rect.centerx - 16, self.rect.centery - 10, 32, 20)
            pygame.draw.rect(surface, (40, 45, 55), laptop_rect, border_radius=2)
            pygame.draw.rect(surface, (120, 190, 255), laptop_rect.inflate(-6, -6), border_radius=1)

        elif self.obs_type == "desk":
            # Školní lavice (dvojlavice)
            pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
            pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=5)
            # Dělící rýha mezi místy v lavici
            pygame.draw.line(surface, self.border_color, 
                             (self.rect.centerx, self.rect.top + 4), 
                             (self.rect.centerx, self.rect.bottom - 4), 2)
            # Židličky za lavicí
            w_chair = (self.rect.width - 24) // 2
            chair1 = pygame.Rect(self.rect.left + 6, self.rect.bottom + 2, w_chair, 10)
            chair2 = pygame.Rect(self.rect.right - 6 - w_chair, self.rect.bottom + 2, w_chair, 10)
            pygame.draw.rect(surface, COLOR_CHAIR, chair1, border_radius=2)
            pygame.draw.rect(surface, COLOR_CHAIR, chair2, border_radius=2)
            # Pero / sešit na lavici
            notebook_rect = pygame.Rect(self.rect.left + 14, self.rect.top + 8, 18, 14)
            pygame.draw.rect(surface, COLOR_WHITE, notebook_rect)
            pygame.draw.line(surface, (50, 100, 220), (notebook_rect.left, notebook_rect.top), (notebook_rect.left, notebook_rect.bottom), 2)

        elif self.obs_type == "locker":
            # Skříňka na chodbě / boku třídy
            pygame.draw.rect(surface, (100, 110, 125), self.rect, border_radius=3)
            pygame.draw.rect(surface, (60, 70, 85), self.rect, width=2, border_radius=3)
            # Větrací mřížky skříňky
            for y_off in (8, 14, 20):
                pygame.draw.line(surface, (40, 45, 55), 
                                 (self.rect.left + 6, self.rect.top + y_off),
                                 (self.rect.right - 6, self.rect.top + y_off), 2)

        elif self.obs_type == "bin":
            # Odpadkový koš
            pygame.draw.rect(surface, (70, 140, 80), self.rect, border_radius=4)
            pygame.draw.rect(surface, (40, 90, 50), self.rect, width=2, border_radius=4)


class ClassroomMap:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.obstacles = []
        self.spawn_points = []
        self.pickup_spots = []
        self._build_classroom()

    def _build_classroom(self):
        wall_thick = 26

        # 1. Obvodové zdi
        top_wall = Obstacle(pygame.Rect(0, 0, self.width, wall_thick), obs_type="wall", color=COLOR_WALL, border_color=COLOR_WALL_BORDER)
        bottom_wall = Obstacle(pygame.Rect(0, self.height - wall_thick, self.width, wall_thick), obs_type="wall", color=COLOR_WALL, border_color=COLOR_WALL_BORDER)
        left_wall = Obstacle(pygame.Rect(0, 0, wall_thick, self.height), obs_type="wall", color=COLOR_WALL, border_color=COLOR_WALL_BORDER)
        right_wall = Obstacle(pygame.Rect(self.width - wall_thick, 0, wall_thick, self.height), obs_type="wall", color=COLOR_WALL, border_color=COLOR_WALL_BORDER)
        
        self.obstacles.extend([top_wall, bottom_wall, left_wall, right_wall])

        # 2. Školní tabule (uprostřed horní zdi)
        board_w, board_h = 320, 36
        board_x = (self.width - board_w) // 2
        board_y = wall_thick + 4
        blackboard = Obstacle(pygame.Rect(board_x, board_y, board_w, board_h), obs_type="blackboard",
                              color=COLOR_BLACKBOARD, border_color=COLOR_BLACKBOARD_FRAME)
        self.obstacles.append(blackboard)

        # 3. Katedra učitele (před tabulí)
        katedra_w, katedra_h = 130, 48
        katedra_x = (self.width - katedra_w) // 2
        katedra_y = board_y + board_h + 38
        katedra = Obstacle(pygame.Rect(katedra_x, katedra_y, katedra_w, katedra_h), obs_type="katedra",
                           color=COLOR_KATEDRA, border_color=COLOR_DESK_BORDER)
        self.obstacles.append(katedra)

        # 4. Školní lavice (uspořádání 3 sloupce x 3 řady lavic)
        desk_w = 150
        desk_h = 44
        col_xs = [120, 475, 830]
        row_ys = [240, 400, 560]

        for r_idx, ry in enumerate(row_ys):
            for c_idx, rx in enumerate(col_xs):
                # Vytvoření lavice
                desk = Obstacle(pygame.Rect(rx, ry, desk_w, desk_h), obs_type="desk",
                                color=COLOR_DESK, border_color=COLOR_DESK_BORDER)
                self.obstacles.append(desk)

                # Místa mezi lavicemi jsou skvělá pro spawnování bonusových zbraní
                self.pickup_spots.append((rx + desk_w // 2, ry - 38))

        # 5. Skříňky podél levé zdi
        for sy in [120, 180, 460, 520]:
            locker = Obstacle(pygame.Rect(wall_thick + 4, sy, 34, 46), obs_type="locker")
            self.obstacles.append(locker)

        # 6. Odpadkový koš v rohu
        bin_obs = Obstacle(pygame.Rect(self.width - wall_thick - 38, self.height - wall_thick - 38, 28, 28), obs_type="bin")
        self.obstacles.append(bin_obs)

        # 7. Příprava bezpečných Spawn pozic pro hráče a boty
        # Pozice v uličkách a rozích, kde není žádná kolize
        self.spawn_points = [
            (90, 80),                        # Levý horní roh (u skříněk)
            (self.width - 100, 80),          # Pravý horní roh (u okna)
            (90, self.height - 90),          # Levý dolní roh (u zadních dveří)
            (self.width - 100, self.height - 90), # Pravý dolní roh (u koše)
            (self.width // 2, self.height - 80),  # Střed vzadu
            (330, 320),                      # Ulička 1
            (730, 320),                      # Ulička 2
            (330, 480),                      # Ulička 1 dole
            (730, 480),                      # Ulička 2 dole
        ]

    def get_collision_rects(self):
        """Vrátí seznam obdélníků pro detekci kolizí s hráči a střelami."""
        return [obs.rect for obs in self.obstacles]

    def draw(self, surface):
        """Vykreslí podlahu učebny a všechny školní překážky."""
        # 1. Podlaha - parkety
        surface.fill(COLOR_BG_FLOOR)
        # Parketový rastr
        tile_size = 50
        for x in range(0, self.width, tile_size):
            pygame.draw.line(surface, COLOR_FLOOR_LINES, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, tile_size):
            pygame.draw.line(surface, COLOR_FLOOR_LINES, (0, y), (self.width, y), 1)

        # 2. Překážky
        for obs in self.obstacles:
            obs.draw(surface)
