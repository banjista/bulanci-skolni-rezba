"""
Testovaci skript pro overeni integrity vsech komponent hry Bulanci.
Vhodne pro automatizovane testovani (CI/CD i lokalni verifikaci).
"""

import os
import sys

# Nastaveni headless rezimu pro Pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

def test_imports():
    print("[1/5] Testovani importu modulu...")
    import settings
    import audio.sound_gen
    import world.map
    import world.particles
    import entities.weapon
    import entities.bullet
    import entities.pickup
    import entities.pillow
    import entities.player
    import entities.bot
    import game
    print("      [OK] Vsechny moduly se uspesne nacetly.")

def test_sound_system():
    print("[2/5] Testovani zvukoveho subsystemu...")
    from audio.sound_gen import SoundManager
    mgr = SoundManager.get_instance()
    for name in ["shoot_pistol", "shoot_shotgun", "shoot_smg", "shoot_sponge", "hit", "death", "pickup", "bell"]:
        mgr.play(name)
    print("      [OK] Zvukove vzorky byly syntetizovany bez chyb.")

def test_map_and_particles():
    print("[3/5] Testovani mapy a casticoveho systemu...")
    from world.map import ClassroomMap
    from world.particles import ParticleSystem
    
    m = ClassroomMap()
    assert len(m.obstacles) > 0, "Chyba: Mapa nema zadne prekazky!"
    assert len(m.spawn_points) >= 4, "Chyba: Nedostatek spawn bodu na mape!"
    
    ps = ParticleSystem()
    ps.add_feather_burst(100, 100, (255, 0, 0), count=10)
    ps.add_chalk_impact(150, 150, (255, 255, 255), count=5)
    ps.add_sponge_explosion(200, 200, count=15)
    assert len(ps.particles) > 0
    ps.update(0.016)
    print("      [OK] Mapa a casticovy system funguji spravne.")

def test_game_simulation():
    print("[4/5] Testovani herni smycky a simulace (Singleplayer, Multiplayer, Duel)...")
    from game import Game
    
    # Test Singleplayer
    g_sp = Game(mode="singleplayer")
    assert len(g_sp.pillows) == 4, f"Ocekavani 4 polstarki, nalezeno {len(g_sp.pillows)}"
    
    dummy_keys = {k: False for k in range(512)}
    dummy_keys[pygame.K_w] = True
    dummy_keys[pygame.K_SPACE] = True
    
    for _ in range(60):
        g_sp.update(0.016, dummy_keys)
    print("      [OK] Singleplayer simulace probehla bez padu.")
    
    # Test Multiplayer
    g_mp = Game(mode="multiplayer")
    assert len(g_mp.pillows) == 4, f"Ocekavani 4 polstarki, nalezeno {len(g_mp.pillows)}"
    for _ in range(30):
        g_mp.update(0.016, dummy_keys)
    print("      [OK] Multiplayer simulace probehla bez padu.")

    # Test Duel
    g_duel = Game(mode="duel")
    assert len(g_duel.pillows) == 2, f"Ocekavani 2 polstarki pro duel, nalezeno {len(g_duel.pillows)}"
    for _ in range(30):
        g_duel.update(0.016, dummy_keys)
    print("      [OK] Duel simulace probehla bez padu.")

def test_rendering():
    print("[5/5] Testovani vykreslovani hernich scen...")
    from game import Game
    from settings import WINDOW_WIDTH, WINDOW_HEIGHT
    
    surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    g = Game(mode="singleplayer")
    g.draw(surf)
    print("      [OK] Herni scena a HUD se uspesne vykreslily na povrch.")

if __name__ == "__main__":
    print("=== SPUSTENI AUTOMATIZOVANYCH TESTU BULANCI ===")
    test_imports()
    test_sound_system()
    test_map_and_particles()
    test_game_simulation()
    test_rendering()
    print("=== VSECHNY TESTY USPESNE PROBEHLY (5/5) ===")
