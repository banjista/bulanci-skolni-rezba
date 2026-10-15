"""
Systém zbraní a munice pro hru Bulánci.
"""

from settings import WEAPON_CONFIG, WEAPON_PISTOL
from audio.sound_gen import SoundManager

class Weapon:
    def __init__(self, weapon_type=WEAPON_PISTOL):
        self.weapon_type = weapon_type
        self.config = WEAPON_CONFIG[weapon_type]
        self.name = self.config["name"]
        self.max_ammo = self.config["max_ammo"]
        self.current_ammo = self.max_ammo
        self.fire_rate = self.config["fire_rate"]
        self.reload_time = self.config["reload_time"]
        
        self.fire_timer = 0.0
        self.is_reloading = False
        self.reload_timer = 0.0

    def reset_to(self, weapon_type):
        """Přenastaví zbraň (např. při sebrání nového bonusu)."""
        self.weapon_type = weapon_type
        self.config = WEAPON_CONFIG[weapon_type]
        self.name = self.config["name"]
        self.max_ammo = self.config["max_ammo"]
        self.current_ammo = self.max_ammo
        self.fire_rate = self.config["fire_rate"]
        self.reload_time = self.config["reload_time"]
        self.fire_timer = 0.0
        self.is_reloading = False
        self.reload_timer = 0.0

    def update(self, dt):
        """Aktualizace časovačů střelby a přebíjení."""
        if self.fire_timer > 0:
            self.fire_timer -= dt

        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.max_ammo
                self.fire_timer = 0.0

    def can_shoot(self):
        """Vrátí True, pokud je možné ze zbraně vystřelit."""
        return not self.is_reloading and self.fire_timer <= 0 and self.current_ammo > 0

    def shoot(self):
        """Provede výstřel, sníží munici a v případě vyprázdnění zahájí přebíjení."""
        if not self.can_shoot():
            return False

        self.current_ammo -= 1
        self.fire_timer = self.fire_rate

        # Automatické přebíjení při prázdném zásobníku
        if self.current_ammo <= 0:
            self.start_reload()

        return True

    def start_reload(self):
        """Zahájí proces přebíjení zbraně."""
        if not self.is_reloading and self.current_ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_timer = self.reload_time
            SoundManager.get_instance().play("reload")

    def get_reload_progress(self):
        """Vrátí postup přebíjení v rozmezí 0.0 až 1.0."""
        if not self.is_reloading:
            return 1.0
        return max(0.0, 1.0 - (self.reload_timer / self.reload_time))
