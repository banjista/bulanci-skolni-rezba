"""
Základní entita Bulánka (polštářku).
Řeší pohyb, kolize se školními lavicemi, střelbu, životy a autentické vykreslení polštářku.
"""

import math
import random
import pygame
from settings import (
    PILLOW_RADIUS, PILLOW_SPEED, PILLOW_ROTATION_SPEED,
    MAX_HEALTH, RESPAWN_TIME, WEAPON_PISTOL,
    COLOR_WHITE, COLOR_BLACK, COLOR_DARK_GRAY, COLOR_YELLOW
)
from .weapon import Weapon
from .bullet import Bullet
from audio.sound_gen import SoundManager

class Pillow:
    def __init__(self, x, y, color, name, role="Student", is_bot=False):
        self.pos = pygame.math.Vector2(x, y)
        self.prev_pos = pygame.math.Vector2(x, y)
        self.color = color
        self.name = name
        self.role = role
        self.is_bot = is_bot
        
        self.radius = PILLOW_RADIUS
        self.speed = PILLOW_SPEED
        self.angle = 0.0           # Úhel natočení ve stupních (0 = vpravo, 90 = dolů)
        self.target_angle = 0.0
        
        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.alive = True
        self.respawn_timer = 0.0
        
        self.weapon = Weapon(WEAPON_PISTOL)
        self.score = 0             # Počet sestřelů (fragy)
        self.deaths = 0            # Počet úmrtí
        
        # Animace chůze (kolébání)
        self.walk_anim = 0.0
        self.is_moving = False

    def reset_for_match(self, spawn_pos):
        """Reset stavu před novou hrou."""
        self.pos = pygame.math.Vector2(spawn_pos)
        self.health = self.max_health
        self.alive = True
        self.weapon.reset_to(WEAPON_PISTOL)
        self.score = 0
        self.deaths = 0
        self.respawn_timer = 0.0

    def respawn(self, spawn_pos):
        """Oživení po sestřelení."""
        self.pos = pygame.math.Vector2(spawn_pos)
        self.health = self.max_health
        self.alive = True
        self.weapon.reset_to(WEAPON_PISTOL)
        self.respawn_timer = 0.0

    def take_damage(self, amount, attacker, particle_system):
        """Udělení poškození polštářku."""
        if not self.alive:
            return

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.deaths += 1
            self.respawn_timer = RESPAWN_TIME
            SoundManager.get_instance().play("death")
            particle_system.add_feather_burst(self.pos.x, self.pos.y, self.color, count=28)
            
            # Započtení bodu střelci
            if attacker and attacker != self:
                attacker.score += 1

    def move_and_collide(self, move_vec, dt, obstacles):
        """Plynulý pohyb s odděleným klouzáním podél zdí a lavic (X a Y osa zvlášť)."""
        if not self.alive or move_vec.length_squared() == 0:
            self.is_moving = False
            return

        self.is_moving = True
        self.walk_anim += dt * 14.0
        norm_dir = move_vec.normalize()

        # Otáčení ve směru pohybu
        self.target_angle = math.degrees(math.atan2(norm_dir.y, norm_dir.x))
        self._smooth_rotate(dt)

        # 1. Pohyb v ose X
        new_x = self.pos.x + norm_dir.x * self.speed * dt
        test_rect_x = pygame.Rect(new_x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        collided_x = False
        for obs_rect in obstacles:
            if obs_rect.colliderect(test_rect_x):
                collided_x = True
                break
        if not collided_x:
            self.pos.x = new_x

        # 2. Pohyb v ose Y
        new_y = self.pos.y + norm_dir.y * self.speed * dt
        test_rect_y = pygame.Rect(self.pos.x - self.radius, new_y - self.radius, self.radius * 2, self.radius * 2)
        collided_y = False
        for obs_rect in obstacles:
            if obs_rect.colliderect(test_rect_y):
                collided_y = True
                break
        if not collided_y:
            self.pos.y = new_y

    def _smooth_rotate(self, dt):
        """Plynulé dotočení k cílovému úhlu."""
        diff = (self.target_angle - self.angle + 180) % 360 - 180
        max_turn = PILLOW_ROTATION_SPEED * dt
        if abs(diff) <= max_turn:
            self.angle = self.target_angle
        else:
            self.angle += math.copysign(max_turn, diff)
        self.angle %= 360

    def shoot(self):
        """Vystřelí ze zbraně a vrátí vygenerované střely."""
        if not self.alive:
            return []

        w = self.weapon
        if not w.shoot():
            return []

        bullets = []
        cfg = w.config
        pellets = cfg.get("pellets", 1)
        spread = cfg.get("spread", 0)

        # Přehrání příslušného zvuku výstřelu
        snd = SoundManager.get_instance()
        if w.weapon_type == WEAPON_PISTOL:
            snd.play("shoot_pistol")
        elif w.weapon_type == "kruzitko":
            snd.play("shoot_shotgun")
        elif w.weapon_type == "pravitko":
            snd.play("shoot_smg")
        elif w.weapon_type == "houba":
            snd.play("shoot_sponge")

        # Pozice hlavně (mírně před polštářkem)
        rad = math.radians(self.angle)
        barrel_dist = self.radius + 12
        muzzle_x = self.pos.x + math.cos(rad) * barrel_dist
        muzzle_y = self.pos.y + math.sin(rad) * barrel_dist

        if pellets == 1:
            # Jedna střela s případným malým rozptylem (např. samopal)
            ang = self.angle + random.uniform(-spread, spread) if spread > 0 else self.angle
            bullets.append(Bullet(muzzle_x, muzzle_y, ang, cfg, self))
        else:
            # Více střel (brokovnice / rozbitá křída)
            step = (spread * 2) / (pellets - 1)
            for i in range(pellets):
                ang = self.angle - spread + i * step
                bullets.append(Bullet(muzzle_x, muzzle_y, ang, cfg, self))

        return bullets

    def update(self, dt, spawn_points=None):
        self.weapon.update(dt)

        if not self.alive:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0 and spawn_points:
                # Vybereme náhodný bezpečný spawn
                new_spawn = random.choice(spawn_points)
                self.respawn(new_spawn)

    def draw(self, surface):
        if not self.alive:
            return

        # Vytvoření dočasného povrchu pro rotaci polštářku
        size = int(self.radius * 3.4)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Jemné kolébání při chůzi
        wobble = math.sin(self.walk_anim) * 2.0 if self.is_moving else 0.0

        # 1. Cípy polštářku (4 rohy polštáře)
        tuft_r = int(self.radius * 0.42)
        diag = int(self.radius * 0.82)
        corners = [
            (center - diag, center - diag),
            (center + diag, center - diag),
            (center + diag, center + diag),
            (center - diag, center + diag),
        ]
        tuft_color = tuple(max(0, c - 25) for c in self.color)
        for cx, cy in corners:
            pygame.draw.circle(surf, tuft_color, (cx, cy), tuft_r)

        # 2. Tělo polštářku (nadýchaný čtverec se zaoblenými rohy)
        body_rect = pygame.Rect(center - self.radius, center - self.radius, self.radius * 2, self.radius * 2)
        pygame.draw.rect(surf, self.color, body_rect, border_radius=int(self.radius * 0.65))
        # Obvodová lemovka polštáře
        pygame.draw.rect(surf, tuft_color, body_rect, width=2, border_radius=int(self.radius * 0.65))

        # 3. Zbraň v rukou (držená před polštářkem směrem doprava - rotace povrchu ji pak natočí)
        w_cfg = self.weapon.config
        w_color = w_cfg["color"]
        gun_start_x = center + int(self.radius * 0.6)
        gun_y = center + 5
        gun_len = 16
        pygame.draw.line(surf, (50, 50, 50), (gun_start_x, gun_y), (gun_start_x + gun_len, gun_y), 5)
        pygame.draw.line(surf, w_color, (gun_start_x + 4, gun_y), (gun_start_x + gun_len, gun_y), 3)

        # 4. Očička Bulánka (velké černé zornice s bílým odleskem hledící dopředu)
        eye_offset_x = center + int(self.radius * 0.35)
        eye_y1 = center - 6
        eye_y2 = center + 6
        # Bílá bělma
        pygame.draw.circle(surf, COLOR_WHITE, (eye_offset_x, eye_y1), 5)
        pygame.draw.circle(surf, COLOR_WHITE, (eye_offset_x, eye_y2), 5)
        # Zornice dívající se dopředu
        pygame.draw.circle(surf, COLOR_BLACK, (eye_offset_x + 2, eye_y1), 3)
        pygame.draw.circle(surf, COLOR_BLACK, (eye_offset_x + 2, eye_y2), 3)

        # Školní prvek: Šprt má kulaté brýle!
        if "Šprt" in self.role or "Hráč 1" in self.name:
            pygame.draw.circle(surf, (20, 20, 20), (eye_offset_x, eye_y1), 6, width=1)
            pygame.draw.circle(surf, (20, 20, 20), (eye_offset_x, eye_y2), 6, width=1)
            pygame.draw.line(surf, (20, 20, 20), (eye_offset_x, eye_y1 + 4), (eye_offset_x, eye_y2 - 4), 1)

        # Otočení celého polštářku
        rot_surf = pygame.transform.rotate(surf, -self.angle)
        rot_rect = rot_surf.get_rect(center=(int(self.pos.x), int(self.pos.y + wobble)))
        surface.blit(rot_surf, rot_rect)

        # 5. Ukazatele nad hlavou (Jméno, životy, přebíjení)
        self._draw_hud_indicators(surface)

    def _draw_hud_indicators(self, surface):
        hud_y = int(self.pos.y - self.radius - 16)
        hud_x = int(self.pos.x)

        # Jméno polštářku
        font = pygame.font.SysFont("arial", 12, bold=True)
        name_surf = font.render(self.name, True, COLOR_DARK_GRAY)
        surface.blit(name_surf, name_surf.get_rect(center=(hud_x, hud_y - 8)))

        # Proužek zdraví
        bar_w = 34
        bar_h = 4
        bar_x = hud_x - bar_w // 2
        pygame.draw.rect(surface, (60, 60, 60), (bar_x - 1, hud_y - 1, bar_w + 2, bar_h + 2), border_radius=2)
        hp_ratio = max(0.0, self.health / self.max_health)
        hp_color = (60, 220, 80) if hp_ratio > 0.5 else ((240, 210, 50) if hp_ratio > 0.25 else (230, 60, 60))
        pygame.draw.rect(surface, hp_color, (bar_x, hud_y, int(bar_w * hp_ratio), bar_h), border_radius=1)

        # Stav munice nebo přebíjení
        if self.weapon.is_reloading:
            # Přebíjecí lišta (žlutá)
            reload_ratio = self.weapon.get_reload_progress()
            r_y = hud_y + bar_h + 3
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, r_y, bar_w, 3), border_radius=1)
            pygame.draw.rect(surface, COLOR_YELLOW, (bar_x, r_y, int(bar_w * reload_ratio), 3), border_radius=1)
        else:
            # Puntíky nábojů křídy
            ammo_cnt = self.weapon.current_ammo
            max_ammo = self.weapon.max_ammo
            if max_ammo <= 10:
                dot_space = bar_w / max_ammo
                for i in range(max_ammo):
                    dot_x = bar_x + i * dot_space + dot_space / 2
                    color = self.weapon.config["color"] if i < ammo_cnt else (110, 110, 110)
                    pygame.draw.circle(surface, color, (int(dot_x), hud_y + bar_h + 4), 2)
