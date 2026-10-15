"""
Entita ovládaná lidským hráčem z klávesnice.
"""

import pygame
from .pillow import Pillow

def _is_key_pressed(keys, key_code):
    if key_code is None:
        return False
    try:
        return bool(keys[key_code])
    except (IndexError, KeyError, TypeError):
        return False

class Player(Pillow):
    def __init__(self, x, y, color, name, role="Student", key_mapping=None):
        super().__init__(x, y, color, name, role, is_bot=False)
        self.key_mapping = key_mapping or {}

    def handle_input(self, keys, dt, obstacles):
        """Zpracuje stisk kláves z klávesnice a pohne hráčem."""
        if not self.alive:
            return []

        move_vec = pygame.math.Vector2(0, 0)
        km = self.key_mapping

        if _is_key_pressed(keys, km.get("up")):
            move_vec.y -= 1
        if _is_key_pressed(keys, km.get("down")):
            move_vec.y += 1
        if _is_key_pressed(keys, km.get("left")):
            move_vec.x -= 1
        if _is_key_pressed(keys, km.get("right")):
            move_vec.x += 1

        self.move_and_collide(move_vec, dt, obstacles)

        # Střelba při držení / stisku střelby
        is_shooting = (
            _is_key_pressed(keys, km.get("shoot")) or
            _is_key_pressed(keys, km.get("shoot_alt")) or
            _is_key_pressed(keys, km.get("shoot_alt2"))
        )

        if is_shooting:
            return self.shoot()

        return []
