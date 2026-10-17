"""
Bonusové zbraně objevující se ve třídě na lavicích nebo na podlaze.
"""

import math
import random
import pygame
from settings import WEAPON_CONFIG, WEAPON_SHOTGUN, WEAPON_SMG, WEAPON_ROCKET
from audio.sound_gen import SoundManager

class WeaponPickup:
    def __init__(self, x, y, weapon_type=None):
        self.pos = pygame.math.Vector2(x, y)
        self.available_types = [WEAPON_SHOTGUN, WEAPON_SMG, WEAPON_ROCKET]
        self.weapon_type = weapon_type if weapon_type else random.choice(self.available_types)
        self.active = True
        self.respawn_timer = 0.0
        self.respawn_delay = 10.0  # Obnovení po 10 sekundách
        self.anim_timer = random.uniform(0, 10)
        self.radius = 18

    def update(self, dt):
        self.anim_timer += dt * 3.5

        if not self.active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.active = True
                self.weapon_type = random.choice(self.available_types)

    def check_pickup(self, pillow, particle_system):
        """Ověří, zda polštářek sebral zbraň."""
        if not self.active or not pillow.alive:
            return False

        dist = self.pos.distance_to(pillow.pos)
        if dist <= self.radius + pillow.radius:
            # Polštářek získává zbraň
            pillow.weapon.reset_to(self.weapon_type)
            SoundManager.get_instance().play("pickup")
            particle_system.add_chalk_impact(self.pos.x, self.pos.y, WEAPON_CONFIG[self.weapon_type]["color"], count=14)
            self.active = False
            self.respawn_timer = self.respawn_delay
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return

        cfg = WEAPON_CONFIG[self.weapon_type]
        # Plovoucí efekt (hover nahoru a dolů)
        float_y = self.pos.y + math.sin(self.anim_timer) * 4.0
        draw_pos = (int(self.pos.x), int(float_y))

        # 1. Zářivý podkres (glow)
        glow_surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        glow_color = (*cfg["color"][:3], 65)
        pygame.draw.circle(glow_surf, glow_color, (22, 22), 20)
        surface.blit(glow_surf, (draw_pos[0] - 22, draw_pos[1] - 22))

        # 2. Školní krabička / penál na zbraň
        box_rect = pygame.Rect(draw_pos[0] - 16, draw_pos[1] - 13, 32, 26)
        pygame.draw.rect(surface, (45, 50, 60), box_rect, border_radius=5)
        pygame.draw.rect(surface, cfg["color"], box_rect, width=2, border_radius=5)

        # 3. Znak zbraně (K, X, R, H)
        font = pygame.font.SysFont("arial", 14, bold=True)
        char = cfg.get("icon_char", "?")
        text_surf = font.render(char, True, cfg["color"])
        text_rect = text_surf.get_rect(center=draw_pos)
        surface.blit(text_surf, text_rect)


class HealthPickup:
    """Školní svačina (červené jablko), která doplní zraněnému polštářku životy."""
    def __init__(self, x, y, heal_amount=35):
        self.pos = pygame.math.Vector2(x, y)
        self.heal_amount = heal_amount
        self.active = True
        self.respawn_timer = 0.0
        self.respawn_delay = 12.0
        self.anim_timer = random.uniform(0, 10)
        self.radius = 16

    def update(self, dt):
        self.anim_timer += dt * 3.5
        if not self.active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.active = True

    def check_pickup(self, pillow, particle_system):
        """Ověří, zda zraněný polštářek sebral svačinu."""
        if not self.active or not pillow.alive:
            return False
        # Svačinu má smysl sebrat jen když má polštářek méně než maximum životů
        if pillow.health >= pillow.max_health:
            return False

        dist = self.pos.distance_to(pillow.pos)
        if dist <= self.radius + pillow.radius:
            pillow.health = min(pillow.max_health, pillow.health + self.heal_amount)
            SoundManager.get_instance().play("pickup")
            # Efekt zelených peříček radosti
            particle_system.add_feather_burst(self.pos.x, self.pos.y, (120, 240, 140), count=14)
            self.active = False
            self.respawn_timer = self.respawn_delay
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return

        float_y = self.pos.y + math.sin(self.anim_timer) * 4.0
        draw_pos = (int(self.pos.x), int(float_y))

        # 1. Zelená záře
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (80, 220, 110, 65), (20, 20), 18)
        surface.blit(glow_surf, (draw_pos[0] - 20, draw_pos[1] - 20))

        # 2. Jablíčko
        pygame.draw.circle(surface, (230, 60, 60), draw_pos, 12)
        pygame.draw.circle(surface, (160, 30, 30), draw_pos, 12, width=2)
        # Stopka jablíčka
        pygame.draw.line(surface, (100, 60, 20), (draw_pos[0], draw_pos[1] - 12), (draw_pos[0] + 3, draw_pos[1] - 16), 2)
        pygame.draw.circle(surface, (80, 200, 80), (draw_pos[0] + 4, draw_pos[1] - 14), 2)

        # 3. Křížek zdraví (+) uprostřed
        pygame.draw.line(surface, (255, 255, 255), (draw_pos[0] - 5, draw_pos[1]), (draw_pos[0] + 5, draw_pos[1]), 2)
        pygame.draw.line(surface, (255, 255, 255), (draw_pos[0], draw_pos[1] - 5), (draw_pos[0], draw_pos[1] + 5), 2)
