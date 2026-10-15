"""
Hlavní spouštěcí modul hry Bulánci: Školní řežba.
Spouští hlavní herní smyčku, menu a přepínání herních režimů.
"""

import sys
import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE,
    COLOR_BLACKBOARD, COLOR_BLACKBOARD_FRAME, COLOR_WHITE, COLOR_YELLOW,
    COLOR_PLAYER_1, COLOR_PLAYER_2, COLOR_BOT_1, COLOR_BOT_2
)
from game import Game
from audio.sound_gen import SoundManager

def draw_chalkboard_background(screen):
    """Vykreslí stylovou školní tabuli jako pozadí menu."""
    screen.fill(COLOR_BLACKBOARD)
    # Dřevěný rám tabule
    frame_w = 20
    pygame.draw.rect(screen, COLOR_BLACKBOARD_FRAME, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), width=frame_w)
    # Polička na křídy dole
    pygame.draw.rect(screen, (160, 110, 60), (frame_w, WINDOW_HEIGHT - frame_w - 10, WINDOW_WIDTH - frame_w * 2, 10))
    # Kousky křídy
    pygame.draw.rect(screen, COLOR_WHITE, (100, WINDOW_HEIGHT - frame_w - 14, 25, 6))
    pygame.draw.rect(screen, COLOR_YELLOW, (140, WINDOW_HEIGHT - frame_w - 14, 22, 6))
    pygame.draw.rect(screen, (80, 160, 240), (175, WINDOW_HEIGHT - frame_w - 14, 20, 6))

def render_pillow_preview(screen, x, y, color, angle=0):
    """Vykreslí malého dekorativního Bulánka v menu."""
    r = 20
    surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    center = r * 2

    # Rohy
    diag = int(r * 0.8)
    for cx, cy in [(center - diag, center - diag), (center + diag, center - diag),
                   (center + diag, center + diag), (center - diag, center + diag)]:
        pygame.draw.circle(surf, tuple(max(0, c - 30) for c in color), (cx, cy), int(r * 0.4))

    # Tělo
    rect = pygame.Rect(center - r, center - r, r * 2, r * 2)
    pygame.draw.rect(surf, color, rect, border_radius=int(r * 0.6))
    # Oči
    pygame.draw.circle(surf, COLOR_WHITE, (center + 6, center - 5), 5)
    pygame.draw.circle(surf, COLOR_WHITE, (center + 6, center + 5), 5)
    pygame.draw.circle(surf, (0, 0, 0), (center + 8, center - 5), 3)
    pygame.draw.circle(surf, (0, 0, 0), (center + 8, center + 5), 3)

    rot_surf = pygame.transform.rotate(surf, -angle)
    screen.blit(rot_surf, rot_surf.get_rect(center=(x, y)))

def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Inicializace zvuku
    sound_mgr = SoundManager.get_instance()

    state = "MENU"  # "MENU", "GAME", "CONTROLS"
    game_instance = None
    selected_option = 0

    menu_options = [
        {"title": "1. Hra proti botům (Singleplayer)", "mode": "singleplayer"},
        {"title": "2. Dva hráči + boti na jedné klávesnici", "mode": "multiplayer"},
        {"title": "3. Duel 2 hráčů (1v1 na klávesnici)", "mode": "duel"},
        {"title": "4. Ovládání a zbraně (Nápověda)", "mode": "controls"},
        {"title": "5. Ukončit hru", "mode": "quit"},
    ]

    title_font = pygame.font.SysFont("arial", 46, bold=True)
    menu_font = pygame.font.SysFont("arial", 24, bold=True)
    info_font = pygame.font.SysFont("arial", 17)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time v sekundách
        dt = min(dt, 0.1)  # Ochrana před skokem při lagu

        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break

            if state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_option = (selected_option - 1) % len(menu_options)
                        sound_mgr.play("shoot_smg")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_option = (selected_option + 1) % len(menu_options)
                        sound_mgr.play("shoot_smg")
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        chosen = menu_options[selected_option]
                        if chosen["mode"] == "quit":
                            running = False
                        elif chosen["mode"] == "controls":
                            state = "CONTROLS"
                        else:
                            game_instance = Game(mode=chosen["mode"])
                            state = "GAME"
                        sound_mgr.play("pickup")

            elif state == "CONTROLS":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        state = "MENU"
                        sound_mgr.play("shoot_smg")

            elif state == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "MENU"
                        sound_mgr.play("shoot_smg")
                    elif game_instance and game_instance.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        # Restart nového kola
                        game_instance = Game(mode=game_instance.mode)

        # Vykreslování podle stavu
        if state == "MENU":
            draw_chalkboard_background(screen)

            # Titulek
            t_surf = title_font.render("BULÁNCI: ŠKOLNÍ ŘEŽBA", True, COLOR_WHITE)
            t_rect = t_surf.get_rect(center=(WINDOW_WIDTH // 2, 110))
            screen.blit(t_surf, t_rect)

            sub_surf = info_font.render("Demonstrace 2D herních principů pro seminář z informatiky", True, (180, 230, 200))
            sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 155))
            screen.blit(sub_surf, sub_rect)

            # Dekorativní polštářci po stranách
            render_pillow_preview(screen, 180, 240, COLOR_PLAYER_1, angle=15)
            render_pillow_preview(screen, WINDOW_WIDTH - 180, 240, COLOR_PLAYER_2, angle=-25)
            render_pillow_preview(screen, 180, 420, COLOR_BOT_1, angle=45)
            render_pillow_preview(screen, WINDOW_WIDTH - 180, 420, COLOR_BOT_2, angle=-40)

            # Seznam položek menu
            start_y = 230
            for i, opt in enumerate(menu_options):
                is_sel = (i == selected_option)
                item_y = start_y + i * 58
                item_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, item_y - 8, 500, 44)

                if is_sel:
                    pygame.draw.rect(screen, (40, 110, 70), item_rect, border_radius=8)
                    pygame.draw.rect(screen, COLOR_YELLOW, item_rect, width=2, border_radius=8)
                    color = COLOR_YELLOW
                    prefix = "►  "
                else:
                    color = (220, 225, 230)
                    prefix = "   "

                m_surf = menu_font.render(prefix + opt["title"], True, color)
                screen.blit(m_surf, (WINDOW_WIDTH // 2 - 230, item_y))

            # Spodní nápověda ovládání menu
            hint_surf = info_font.render("Pohyb v menu: [ŠIPKY] / [W/S] | Potvrdit: [ENTER] / [MEZERNÍK]", True, (160, 210, 180))
            hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
            screen.blit(hint_surf, hint_rect)

        elif state == "CONTROLS":
            draw_chalkboard_background(screen)

            # Nadpis
            t_surf = title_font.render("OVLÁDÁNÍ A ŠKOLNÍ VÝZBROJ", True, COLOR_YELLOW)
            screen.blit(t_surf, t_surf.get_rect(center=(WINDOW_WIDTH // 2, 85)))

            # Dvě tabulky: Hráči a Zbraně
            col1_x = 90
            col2_x = WINDOW_WIDTH // 2 + 30
            y = 150

            # 1. Hráč 1
            h1_title = menu_font.render("Hráč 1 (Červený Šprt):", True, COLOR_PLAYER_1)
            screen.blit(h1_title, (col1_x, y))
            screen.blit(info_font.render("• Pohyb: [W] [S] [A] [D]", True, COLOR_WHITE), (col1_x, y + 34))
            screen.blit(info_font.render("• Střelba: [MEZERNÍK] (Space)", True, COLOR_WHITE), (col1_x, y + 62))

            # 2. Hráč 2
            h2_title = menu_font.render("Hráč 2 (Modrý Záškolák):", True, COLOR_PLAYER_2)
            screen.blit(h2_title, (col1_x, y + 115))
            screen.blit(info_font.render("• Pohyb: [ŠIPKY] (Nahoru, Dolů, Vlevo, Vpravo)", True, COLOR_WHITE), (col1_x, y + 149))
            screen.blit(info_font.render("• Střelba: [PRAVÝ CTRL] / [ENTER] / [NUMPAD 0]", True, COLOR_WHITE), (col1_x, y + 177))

            # 3. Zbraně a pravidla
            w_title = menu_font.render("Školní zbraně (Bonusy na lavicích):", True, COLOR_YELLOW)
            screen.blit(w_title, (col2_x, y))
            screen.blit(info_font.render("• [K] Křídomet: 5 nábojů, přesný, přebíjí", True, COLOR_WHITE), (col2_x, y + 34))
            screen.blit(info_font.render("• [X] Kružítko: 4 broky křídy najednou", True, COLOR_WHITE), (col2_x, y + 62))
            screen.blit(info_font.render("• [R] Pravítko: Rychlopalný křídový samopal", True, COLOR_WHITE), (col2_x, y + 90))
            screen.blit(info_font.render("• [H] Mokrá houba: Exploduje s plošným poškozením!", True, (100, 200, 255)), (col2_x, y + 118))
            screen.blit(info_font.render("• Cíl hry: Získej 7 sestřelů v učebně dříve než ostatní!", True, (240, 220, 110)), (col2_x, y + 160))

            # Návrat
            back_surf = menu_font.render("Stiskni [ESC] nebo [ENTER] pro návrat do menu", True, COLOR_YELLOW)
            screen.blit(back_surf, back_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 75)))

        elif state == "GAME":
            if game_instance:
                game_instance.update(dt, keys)
                game_instance.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
