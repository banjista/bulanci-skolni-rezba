"""
Globální nastavení hry Bulánci: Školní řežba (Classroom Bulánci)
Vhodné pro demonstraci na semináři z informatiky.
"""

import pygame

# --- Okno a zobrazení ---
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
FPS = 60
WINDOW_TITLE = "Bulánci: Školní řežba (Seminární projekt)"

# --- Barvy (RGB) ---
COLOR_BG_FLOOR = (215, 195, 160)       # Školní parkety / linoleum
COLOR_FLOOR_LINES = (195, 175, 140)    # Spáry parket
COLOR_WALL = (60, 64, 72)              # Zdi učebny
COLOR_WALL_BORDER = (35, 38, 44)       # Rám zdí
COLOR_DESK = (180, 125, 75)            # Dřevěné školní lavice
COLOR_DESK_BORDER = (120, 75, 35)      # Hrana lavic
COLOR_CHAIR = (150, 100, 60)           # Židle
COLOR_BLACKBOARD = (34, 75, 48)        # Školní zelená tabule
COLOR_BLACKBOARD_FRAME = (120, 80, 45) # Dřevěný rám tabule
COLOR_KATEDRA = (140, 90, 50)          # Učitelská katedra
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_GRAY = (120, 120, 120)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_YELLOW = (245, 215, 60)
COLOR_CHALK_WHITE = (250, 250, 250)
COLOR_CHALK_RED = (240, 80, 80)
COLOR_CHALK_BLUE = (80, 140, 240)
COLOR_CHALK_GREEN = (90, 210, 110)
COLOR_CHALK_YELLOW = (250, 225, 75)
COLOR_INK_SPONGE = (50, 120, 200)

# --- Barvy polštářků (Bulánků) ---
COLOR_PLAYER_1 = (235, 75, 75)         # Červený polštářek (Šprt)
COLOR_PLAYER_2 = (60, 130, 245)        # Modrý polštářek (Záškolák)
COLOR_BOT_1 = (55, 185, 90)            # Zelený polštářek (Třídní šašek)
COLOR_BOT_2 = (245, 180, 45)           # Žlutý polštářek (Svačinář)
COLOR_BOT_3 = (165, 85, 225)           # Fialový polštářek (Biflovač)

# --- Fyzika a Bulánci ---
PILLOW_RADIUS = 24                     # Velikost polštářku
PILLOW_SPEED = 220                     # Rychlost pohybu v pixelech za sekundu
PILLOW_ROTATION_SPEED = 400            # Rychlost otáčení (stupně za sekundu)
MAX_HEALTH = 100                       # Maximální životy
RESPAWN_TIME = 2.0                     # Čas oživení v sekundách
SCORE_TO_WIN = 7                       # Výchozí počet sestřelů na vítězství

# --- Zbraně ---
WEAPON_PISTOL = "kridomet"             # Základní křídomet
WEAPON_SHOTGUN = "kruzitko"            # Brokovnice / Rozbitá křída
WEAPON_SMG = "pravitko"                # Rychlopalné pravítko
WEAPON_ROCKET = "houba"                # Mokrá houba na tabuli

WEAPON_CONFIG = {
    WEAPON_PISTOL: {
        "name": "Křídomet",
        "description": "Základní školní křídový revolver na 5 nábojů.",
        "max_ammo": 5,
        "fire_rate": 0.28,             # sekundy mezi výstřely
        "reload_time": 1.25,           # sekundy přebíjení
        "bullet_speed": 560,
        "damage": 35,
        "spread": 0,
        "pellets": 1,
        "color": COLOR_CHALK_WHITE,
        "icon_char": "K",
    },
    WEAPON_SHOTGUN: {
        "name": "Kružítko / Kousky křídy",
        "description": "Rozptyl 4 ostrých křídových projektilů najednou.",
        "max_ammo": 4,
        "fire_rate": 0.65,
        "reload_time": 1.7,
        "bullet_speed": 510,
        "damage": 26,
        "spread": 16,                  # rozptyl ve stupních
        "pellets": 4,
        "color": COLOR_CHALK_YELLOW,
        "icon_char": "X",
    },
    WEAPON_SMG: {
        "name": "Pravítkový rychlopal",
        "description": "Vysoká kadence vystřelující dávku drobných křídových střel.",
        "max_ammo": 24,
        "fire_rate": 0.09,
        "reload_time": 1.8,
        "bullet_speed": 640,
        "damage": 15,
        "spread": 7,
        "pellets": 1,
        "color": (255, 140, 50),
        "icon_char": "R",
    },
    WEAPON_ROCKET: {
        "name": "Mokrá houba",
        "description": "Vystřelí těžkou houbu na tabuli, která při nárazu vybuchne louží vody a peří.",
        "max_ammo": 2,
        "fire_rate": 0.9,
        "reload_time": 2.1,
        "bullet_speed": 400,
        "damage": 90,
        "spread": 0,
        "pellets": 1,
        "color": COLOR_INK_SPONGE,
        "is_explosive": True,
        "explosion_radius": 80,
        "icon_char": "H",
    }
}

# --- Léčivé bonusy (Svačina) ---
PICKUP_HEALTH_AMOUNT = 35              # Počet doplněných životů
COLOR_SNACK = (230, 60, 60)            # Červené jablíčko se svačinou

# --- Ovládání ---
PLAYER_1_KEYS = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "shoot": pygame.K_SPACE,
}

PLAYER_2_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "shoot": pygame.K_RCTRL,
    "shoot_alt": pygame.K_RETURN,
    "shoot_alt2": pygame.K_KP0,
}
