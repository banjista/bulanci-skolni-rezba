"""
Projektily vystřelené zbraněmi (křídy, broky, houby).
"""

import math
import pygame
from audio.sound_gen import SoundManager

class Bullet:
    def __init__(self, x, y, angle_deg, weapon_config, owner):
        self.pos = pygame.math.Vector2(x, y)
        self.owner = owner
        self.config = weapon_config
        self.speed = weapon_config["bullet_speed"]
        self.damage = weapon_config["damage"]
        self.color = weapon_config["color"]
        self.is_explosive = weapon_config.get("is_explosive", False)
        self.explosion_radius = weapon_config.get("explosion_radius", 75)
        
        self.angle_deg = angle_deg
        rad = math.radians(angle_deg)
        self.vel = pygame.math.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)
        
        self.radius = 7 if self.is_explosive else 3.5
        self.alive = True
        self.lifetime = 3.0  # Maximální doba letu (sekundy)

    def update(self, dt, obstacles, pillows, particle_system):
        if not self.alive:
            return

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return

        # Pohyb střely
        prev_pos = pygame.math.Vector2(self.pos)
        self.pos += self.vel * dt

        # 1. Kontrola kolize se zdmi a lavicemi
        # Vytvoříme úsečku pohybu střely pro přesnou detekci
        bullet_rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        
        for obs_rect in obstacles:
            if obs_rect.colliderect(bullet_rect) or obs_rect.clipline(prev_pos, self.pos):
                self._handle_impact(obs_rect.centerx, obs_rect.centery, pillows, particle_system, hit_pillow=None)
                return

        # 2. Kontrola kolize s polštářky
        for pillow in pillows:
            if not pillow.alive or pillow == self.owner:
                continue

            dist = self.pos.distance_to(pillow.pos)
            if dist <= pillow.radius + self.radius:
                self._handle_impact(self.pos.x, self.pos.y, pillows, particle_system, hit_pillow=pillow)
                return

    def _handle_impact(self, hit_x, hit_y, pillows, particle_system, hit_pillow=None):
        """Vyřešení dopadu střely (přímý zásah i plošná exploze houby)."""
        self.alive = False

        if self.is_explosive:
            # Mokrá houba vybuchne s plošným poškozením (AOE)
            SoundManager.get_instance().play("explode_sponge")
            particle_system.add_sponge_explosion(self.pos.x, self.pos.y)

            for target in pillows:
                if not target.alive:
                    continue
                d = self.pos.distance_to(target.pos)
                if d <= self.explosion_radius:
                    # Poškození klesá se vzdáleností od středu exploze
                    falloff = max(0.2, 1.0 - (d / self.explosion_radius))
                    actual_dmg = self.damage * falloff
                    target.take_damage(actual_dmg, self.owner, particle_system)
        else:
            # Klasická křída
            if hit_pillow:
                SoundManager.get_instance().play("hit")
                hit_pillow.take_damage(self.damage, self.owner, particle_system)
                particle_system.add_feather_burst(self.pos.x, self.pos.y, hit_pillow.color, count=12)
            else:
                SoundManager.get_instance().play("hit")
                particle_system.add_chalk_impact(self.pos.x, self.pos.y, self.color, count=8)

    def draw(self, surface):
        if not self.alive:
            return

        if self.is_explosive:
            # Houba: oválný modrozelený tvar s pěnou
            surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            sponge_rect = pygame.Rect(2, 2, int(self.radius * 2.2), int(self.radius * 1.6))
            pygame.draw.rect(surf, self.color, sponge_rect, border_radius=4)
            pygame.draw.circle(surf, (200, 240, 255), (int(self.radius * 1.5), int(self.radius)), 3)
            rot_surf = pygame.transform.rotate(surf, -self.angle_deg)
            rect = rot_surf.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(rot_surf, rect)
        else:
            # Kousíček letící křídy (váleček)
            rad = math.radians(self.angle_deg)
            length = 7
            end_x = self.pos.x - math.cos(rad) * length
            end_y = self.pos.y - math.sin(rad) * length
            pygame.draw.line(surface, self.color, (int(self.pos.x), int(self.pos.y)), (int(end_x), int(end_y)), 4)
