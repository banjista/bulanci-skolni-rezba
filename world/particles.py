"""
Částicový systém pro vizuální efekty:
- Létající peříčka (peří z roztržených polštářků)
- Křídový prach (při nárazu křídy do zdi či lavice)
- Kapky vody a louže (z mokré houby)
- Zářivé částice (při sebrání zbraně)
"""

import math
import random
import pygame

class Particle:
    def __init__(self, x, y, vx, vy, color, radius, lifetime, p_type="feather"):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vx, vy)
        self.color = color
        self.radius = radius
        self.initial_radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.p_type = p_type
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        # Pohyb a tření vzduchu
        self.pos += self.vel * dt
        if self.p_type == "feather":
            self.vel *= (0.92 ** (dt * 60))  # peříčka plachtí a brzdí
            self.rotation += self.rot_speed * dt
        elif self.p_type == "dust":
            self.vel *= (0.85 ** (dt * 60))
        elif self.p_type == "splash":
            self.vel *= (0.80 ** (dt * 60))

        # Zmenšování s ubývajícím časem
        t = max(0.0, self.lifetime / self.max_lifetime)
        self.radius = max(1.0, self.initial_radius * t)
        return True

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha <= 5:
            return

        if self.p_type == "feather":
            # Kreslení oválného peříčka s rotací
            w = int(self.radius * 2.8)
            h = int(self.radius * 1.4)
            if w <= 1 or h <= 1:
                return
            surf = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
            feather_color = (*self.color[:3], alpha)
            rect = pygame.Rect(w - w // 2, h - h // 2, w, h)
            pygame.draw.ellipse(surf, feather_color, rect)
            rotated_surf = pygame.transform.rotate(surf, self.rotation)
            draw_pos = rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(rotated_surf, draw_pos)

        elif self.p_type == "dust":
            # Křídový obláček
            surf = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
            dust_color = (*self.color[:3], int(alpha * 0.75))
            pygame.draw.circle(surf, dust_color, (int(self.radius + 1), int(self.radius + 1)), int(self.radius))
            surface.blit(surf, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))

        elif self.p_type == "splash":
            # Kapka vody
            surf = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
            splash_color = (*self.color[:3], alpha)
            pygame.draw.circle(surf, splash_color, (int(self.radius + 1), int(self.radius + 1)), int(self.radius))
            surface.blit(surf, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))

        else:
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.decals = []  # Trvalejší stopy na podlaze (louže, křídové skvrny)
        self.max_decals = 40

    def add_feather_burst(self, x, y, color, count=16):
        """Vytvoří výbuch peříček v barvě polštářku při zásahu."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 260)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            # Směs bílých a zabarvených peříček
            p_color = (255, 255, 255) if random.random() < 0.45 else color
            radius = random.uniform(3.5, 7.0)
            lifetime = random.uniform(0.7, 1.4)
            self.particles.append(Particle(x, y, vx, vy, p_color, radius, lifetime, p_type="feather"))

    def add_chalk_impact(self, x, y, color, count=8):
        """Křídový prach při nárazu střely do zdi či překážky."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 140)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            radius = random.uniform(2.0, 4.5)
            lifetime = random.uniform(0.3, 0.6)
            self.particles.append(Particle(x, y, vx, vy, color, radius, lifetime, p_type="dust"))

    def add_sponge_explosion(self, x, y, count=35):
        """Mokrá exploze houby (kapky vody a peří)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 320)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            radius = random.uniform(4.0, 9.0)
            lifetime = random.uniform(0.5, 1.1)
            water_color = (60, 140, 230)
            self.particles.append(Particle(x, y, vx, vy, water_color, radius, lifetime, p_type="splash"))

        # Záchytná louže na podlaze
        if len(self.decals) >= self.max_decals:
            self.decals.pop(0)
        self.decals.append({
            "pos": (int(x), int(y)),
            "radius": random.randint(28, 42),
            "color": (60, 130, 210, 85)
        })

    def update(self, dt):
        # Aktualizace všech částic, mrtvé se odstraní
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw_decals(self, surface):
        """Vykreslení stop na podlaze pod objekty."""
        for d in self.decals:
            r = d["radius"]
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, d["color"], (r, r), r)
            surface.blit(surf, (d["pos"][0] - r, d["pos"][1] - r))

    def draw(self, surface):
        """Vykreslení aktivních částic."""
        for p in self.particles:
            p.draw(surface)
