"""
Hlavní herní manažer: správa zápasu, hráčů, botů, střel, skóre a vyhodnocení vítěze.
"""

import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, SCORE_TO_WIN,
    COLOR_PLAYER_1, COLOR_PLAYER_2, COLOR_BOT_1, COLOR_BOT_2, COLOR_BOT_3,
    PLAYER_1_KEYS, PLAYER_2_KEYS, COLOR_WHITE, COLOR_BLACK, COLOR_YELLOW
)
from world.map import ClassroomMap
from world.particles import ParticleSystem
from entities.player import Player
from entities.bot import Bot
from entities.pickup import WeaponPickup, HealthPickup
from audio.sound_gen import SoundManager

class Game:
    def __init__(self, mode="singleplayer"):
        self.mode = mode  # "singleplayer", "multiplayer", "duel"
        self.map = ClassroomMap()
        self.particles = ParticleSystem()
        
        self.pillows = []
        self.bullets = []
        self.pickups = []
        
        self.score_limit = SCORE_TO_WIN
        self.game_over = False
        self.winner = None
        self.match_time = 0.0

        self._setup_match()

    def _setup_match(self):
        """Inicializace účastníků a zbraní na základě zvoleného módu."""
        sp = self.map.spawn_points
        self.pillows.clear()
        self.bullets.clear()
        self.pickups.clear()
        self.game_over = False
        self.winner = None
        self.match_time = 0.0

        # 1. Hráč 1 (vždy přítomen - Červený Šprt)
        p1 = Player(sp[0][0], sp[0][1], COLOR_PLAYER_1, "Hráč 1", role="Šprt", key_mapping=PLAYER_1_KEYS)
        self.pillows.append(p1)

        if self.mode == "singleplayer":
            # 3 AI boti proti hráči 1
            bot1 = Bot(sp[1][0], sp[1][1], COLOR_BOT_1, "Třídní šašek", role="Rebel")
            bot2 = Bot(sp[2][0], sp[2][1], COLOR_BOT_2, "Svačinář", role="Otesánek")
            bot3 = Bot(sp[3][0], sp[3][1], COLOR_BOT_3, "Biflovač", role="Učeň")
            self.pillows.extend([bot1, bot2, bot3])

        elif self.mode == "multiplayer":
            # 2 hráči na 1 klávesnici + 2 boti
            p2 = Player(sp[1][0], sp[1][1], COLOR_PLAYER_2, "Hráč 2", role="Záškolák", key_mapping=PLAYER_2_KEYS)
            self.pillows.append(p2)
            bot1 = Bot(sp[2][0], sp[2][1], COLOR_BOT_1, "Třídní šašek", role="Rebel")
            bot2 = Bot(sp[3][0], sp[3][1], COLOR_BOT_2, "Svačinář", role="Otesánek")
            self.pillows.extend([bot1, bot2])

        elif self.mode == "duel":
            # Čistý 1v1 souboj na jedné klávesnici
            p2 = Player(sp[1][0], sp[1][1], COLOR_PLAYER_2, "Hráč 2", role="Záškolák", key_mapping=PLAYER_2_KEYS)
            self.pillows.append(p2)

        # 2. Spawnování bonusových zbraní na školních místech
        for spot in self.map.pickup_spots[:6]:
            self.pickups.append(WeaponPickup(spot[0], spot[1]))

        # 3. Spawnování školních svačin (jablíček) pro léčení na zbývajících lavicích
        for spot in self.map.pickup_spots[6:]:
            self.pickups.append(HealthPickup(spot[0], spot[1]))

        # Školní zvonění na začátku zápasu
        SoundManager.get_instance().play("bell")

    def update(self, dt, keys):
        """Aktualizace herní logiky každý snímek."""
        self.match_time += dt
        obs_rects = self.map.get_collision_rects()
        sp = self.map.spawn_points

        if not self.game_over:
            # 1. Hráči a boti
            for p in self.pillows:
                if not p.alive:
                    p.update(dt, sp)
                    continue

                if isinstance(p, Player):
                    bullets = p.handle_input(keys, dt, obs_rects)
                    self.bullets.extend(bullets)
                elif isinstance(p, Bot):
                    bullets = p.update_ai(dt, self.pillows, obs_rects, self.pickups, sp)
                    self.bullets.extend(bullets)

                # Kontrola sebrání zbraní
                for item in self.pickups:
                    item.check_pickup(p, self.particles)

                # Kontrola vítězství
                if p.score >= self.score_limit:
                    self.game_over = True
                    self.winner = p
                    SoundManager.get_instance().play("bell")

            # 2. Zbraně na mapě
            for item in self.pickups:
                item.update(dt)

            # 3. Projektily
            for b in self.bullets:
                b.update(dt, obs_rects, self.pillows, self.particles)
            self.bullets = [b for b in self.bullets if b.alive]

        # 4. Částice
        self.particles.update(dt)

    def draw(self, surface):
        """Vykreslení celého herního světa a uživatelského rozhraní."""
        # 1. Školní učebna
        self.map.draw(surface)

        # 2. Stopy na podlaze (louže vody, křída)
        self.particles.draw_decals(surface)

        # 3. Bonusové předměty
        for item in self.pickups:
            item.draw(surface)

        # 4. Polštářci (živí)
        for p in self.pillows:
            p.draw(surface)

        # 5. Střely křídy a houby
        for b in self.bullets:
            b.draw(surface)

        # 6. Částice peří a prachu
        self.particles.draw(surface)

        # 7. Herní panel se skóre (HUD)
        self._draw_scoreboard(surface)

        # 8. Obrazovka vítěze
        if self.game_over and self.winner:
            self._draw_victory_screen(surface)

    def _draw_scoreboard(self, surface):
        """Horní lišta s průběžným skóre a zbraněmi."""
        hud_bg = pygame.Rect(0, 0, WINDOW_WIDTH, 36)
        pygame.draw.rect(surface, (25, 28, 35, 230), hud_bg)
        pygame.draw.line(surface, (60, 65, 75), (0, 36), (WINDOW_WIDTH, 36), 2)

        font = pygame.font.SysFont("arial", 14, bold=True)
        small_font = pygame.font.SysFont("arial", 12)

        x_offset = 20
        spacing = WINDOW_WIDTH // max(1, len(self.pillows))

        for idx, p in enumerate(self.pillows):
            x = x_offset + idx * spacing
            # Barevný čtvereček polštářku
            pygame.draw.rect(surface, p.color, (x, 8, 20, 20), border_radius=4)
            pygame.draw.rect(surface, COLOR_WHITE, (x, 8, 20, 20), width=1, border_radius=4)

            # Jméno a skóre
            score_text = f"{p.name}: {p.score}/{self.score_limit}"
            s_surf = font.render(score_text, True, COLOR_WHITE)
            surface.blit(s_surf, (x + 26, 6))

            # Zbraň
            w_text = f"[{p.weapon.name}]"
            w_surf = small_font.render(w_text, True, p.weapon.config["color"])
            surface.blit(w_surf, (x + 26, 21))

    def _draw_victory_screen(self, surface):
        """Vítězná obrazovka po dosažení limitu sestřelů."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 18, 24, 195))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 560, 320
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = (WINDOW_HEIGHT - box_h) // 2
        banner_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        
        # Školní cedule
        pygame.draw.rect(surface, (40, 45, 55), banner_rect, border_radius=12)
        pygame.draw.rect(surface, self.winner.color, banner_rect, width=4, border_radius=12)

        title_font = pygame.font.SysFont("arial", 34, bold=True)
        sub_font = pygame.font.SysFont("arial", 20)
        hint_font = pygame.font.SysFont("arial", 16)

        title = f"Vítěz kola: {self.winner.name}!"
        t_surf = title_font.render(title, True, self.winner.color)
        t_rect = t_surf.get_rect(center=(WINDOW_WIDTH // 2, box_y + 60))
        surface.blit(t_surf, t_rect)

        sub = f"Dosáhl {self.winner.score} sestřelů a ovládl školní třídu!"
        s_surf = sub_font.render(sub, True, COLOR_WHITE)
        s_rect = s_surf.get_rect(center=(WINDOW_WIDTH // 2, box_y + 115))
        surface.blit(s_surf, s_rect)

        # Tabulka skóre
        y_score = box_y + 160
        for p in sorted(self.pillows, key=lambda x: x.score, reverse=True):
            entry = f"{p.name} ({p.role}): {p.score} sestřelů | {p.deaths} smrtí"
            e_surf = hint_font.render(entry, True, (210, 215, 225))
            surface.blit(e_surf, (box_x + 80, y_score))
            y_score += 24

        hint = "Stiskni [MEZERNÍK] nebo [ENTER] pro nové kolo | [ESC] do Menu"
        h_surf = hint_font.render(hint, True, COLOR_YELLOW)
        h_rect = h_surf.get_rect(center=(WINDOW_WIDTH // 2, box_y + box_h - 32))
        surface.blit(h_surf, h_rect)
