"""
Umělá inteligence bota (AI Bulánek) pro hru Bulánci.
Využívá stavový automat (FSM), detekci přímé viditelnosti (Raycasting) a taktický ústup za lavice.
Skvělá ukázka herní AI pro seminář z informatiky.
"""

import math
import random
import pygame
from .pillow import Pillow

class Bot(Pillow):
    def __init__(self, x, y, color, name, role="AI Šašek"):
        super().__init__(x, y, color, name, role, is_bot=True)
        
        # Stavy bota: 'WANDER', 'CHASE', 'ENGAGE', 'RETREAT'
        self.state = "WANDER"
        self.target = None
        self.waypoint = pygame.math.Vector2(x, y)
        self.change_dir_timer = random.uniform(1.0, 3.0)
        
        # Časovač kadence střelby bota (aby nestřílel strojově každý možný snímek)
        self.shoot_cooldown = random.uniform(0.2, 0.5)

    def _has_line_of_sight(self, target_pos, obstacles):
        """Ověří přímou viditelnost mezi botem a cílem bez překážejících lavic."""
        p1 = (self.pos.x, self.pos.y)
        p2 = (target_pos.x, target_pos.y)
        for obs in obstacles:
            if obs.clipline(p1, p2):
                return False
        return True

    def _find_closest_enemy(self, all_pillows):
        """Vyhledá nejbližšího živého protivníka."""
        closest = None
        min_dist = float("inf")
        for p in all_pillows:
            if p == self or not p.alive:
                continue
            dist = self.pos.distance_to(p.pos)
            if dist < min_dist:
                min_dist = dist
                closest = p
        return closest

    def _find_closest_pickup(self, pickups):
        """Vyhledá nejbližší aktivní bonusovou zbraň."""
        best = None
        min_dist = 400.0  # Jen pokud je rozumně blízko
        for item in pickups:
            if not item.active:
                continue
            dist = self.pos.distance_to(item.pos)
            if dist < min_dist:
                min_dist = dist
                best = item
        return best

    def update_ai(self, dt, all_pillows, obstacles, pickups, spawn_points):
        """Hlavní rozhodovací cyklus umělé inteligence bota."""
        if not self.alive:
            self.update(dt, spawn_points)
            return []

        self.update(dt)
        self.shoot_cooldown -= dt
        self.change_dir_timer -= dt

        # 1. Vyhledání protivníka
        self.target = self._find_closest_enemy(all_pillows)
        pickup = self._find_closest_pickup(pickups)

        # 2. Určení stavu bota
        has_los = False
        target_dist = 9999.0
        if self.target:
            target_dist = self.pos.distance_to(self.target.pos)
            has_los = self._has_line_of_sight(self.target.pos, obstacles)

        # Pokud bot přebíjí nebo má málo životů, ustupuje do krytu
        if self.weapon.is_reloading or (self.health < 30 and target_dist < 250):
            self.state = "RETREAT"
        elif has_los and target_dist < 480:
            self.state = "ENGAGE"
        elif pickup and self.weapon.weapon_type == "kridomet":
            self.state = "PICKUP"
        elif self.target:
            self.state = "CHASE"
        else:
            self.state = "WANDER"

        # 3. Vykonání chování podle stavu
        move_dir = pygame.math.Vector2(0, 0)
        spawned_bullets = []

        if self.state == "ENGAGE":
            # Přímý boj: otočit se na cíl a pálit
            to_target = self.target.pos - self.pos
            self.target_angle = math.degrees(math.atan2(to_target.y, to_target.x))
            self._smooth_rotate(dt)

            # Mírný pohyb / kličkování při boji
            if target_dist > 220:
                move_dir = to_target.normalize()
            elif target_dist < 120:
                move_dir = -to_target.normalize()  # udržování bezpečné vzdálenosti

            # Střelba v dávkách
            angle_diff = abs((self.target_angle - self.angle + 180) % 360 - 180)
            if angle_diff < 20 and self.shoot_cooldown <= 0:
                bullets = self.shoot()
                if bullets:
                    spawned_bullets.extend(bullets)
                    self.shoot_cooldown = random.uniform(0.18, 0.45)

        elif self.state == "RETREAT":
            # Ústup od cíle směrem k náhodnému volnému místu
            if self.target:
                away_vec = self.pos - self.target.pos
                if away_vec.length_squared() > 0:
                    move_dir = away_vec.normalize()

        elif self.state == "PICKUP" and pickup:
            # Běh pro novou zbraň
            to_pickup = pickup.pos - self.pos
            if to_pickup.length_squared() > 0:
                move_dir = to_pickup.normalize()

        elif self.state == "CHASE" and self.target:
            # Pronásledování cíle
            to_target = self.target.pos - self.pos
            if to_target.length_squared() > 0:
                move_dir = to_target.normalize()

        else: # WANDER
            if self.change_dir_timer <= 0 or self.pos.distance_to(self.waypoint) < 30:
                # Výběr nového náhodného cílového bodu
                self.waypoint = pygame.math.Vector2(random.choice(spawn_points))
                self.change_dir_timer = random.uniform(2.5, 5.0)

            to_wp = self.waypoint - self.pos
            if to_wp.length_squared() > 0:
                move_dir = to_wp.normalize()

        # Fyzický pohyb s kolizemi
        self.move_and_collide(move_dir, dt, obstacles)

        return spawned_bullets
