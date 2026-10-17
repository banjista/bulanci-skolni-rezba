"""
Procedurální generátor zvukových efektů pro hru Bulánci.
Využívá přímou syntézu zvukových vzorků (PCM), takže hra nepotřebuje žádné externí WAV/MP3 soubory
a funguje spolehlivě na jakémkoliv počítači.
"""

import math
import struct
import pygame

class SoundManager:
    _instance = None

    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._generate_all_sounds()
        except Exception as e:
            print(f"[SoundManager] Zvukový subsystém nedostupný ({e}), hra poběží bez zvuku.")
            self.enabled = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _generate_tone(self, freq_start, freq_end, duration_sec, volume=0.5, wave_type="sine", noise=False):
        """Vygeneruje syntetický zvukový vzorek jako Pygame Sound objekt."""
        if not self.enabled:
            return None

        sample_rate = 22050
        num_samples = int(sample_rate * duration_sec)
        raw_data = bytearray()

        import random

        for i in range(num_samples):
            t = i / num_samples
            current_freq = freq_start + (freq_end - freq_start) * t
            
            # Obálka (envelope) pro měkký náběh a dozvuk
            fade_in = min(1.0, i / (0.01 * sample_rate + 1))
            fade_out = max(0.0, 1.0 - t)
            env = fade_in * (fade_out ** 1.5)

            if noise:
                sample_val = (random.random() * 2.0 - 1.0) * env
            elif wave_type == "sine":
                phase = 2.0 * math.pi * current_freq * (i / sample_rate)
                sample_val = math.sin(phase) * env
            elif wave_type == "square":
                phase = 2.0 * math.pi * current_freq * (i / sample_rate)
                sample_val = (1.0 if math.sin(phase) >= 0 else -1.0) * env * 0.7
            else: # saw
                phase = (current_freq * (i / sample_rate)) % 1.0
                sample_val = (2.0 * phase - 1.0) * env * 0.7

            # Převod na 16-bit podepsané celé číslo (-32768 až 32767)
            int_sample = int(sample_val * volume * 32767)
            int_sample = max(-32768, min(32767, int_sample))
            raw_data.extend(struct.pack("<h", int_sample))

        try:
            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception:
            return None

    def _generate_all_sounds(self):
        """Vytvoří všechny herní zvuky."""
        # 1. Výstřel křídometu (krátké cvaknutí a hvizd křídy)
        self.sounds["shoot_pistol"] = self._generate_tone(800, 200, 0.08, volume=0.4, wave_type="square")
        # 2. Brokovnice / kružítko (hlasitější rozptýlený výstřel)
        self.sounds["shoot_shotgun"] = self._generate_tone(400, 120, 0.16, volume=0.6, noise=True)
        # 3. Samopal (rychlé ostré lupnutí)
        self.sounds["shoot_smg"] = self._generate_tone(1100, 350, 0.05, volume=0.35, wave_type="saw")
        # 4. Houba / raketa (zahvízdání)
        self.sounds["shoot_sponge"] = self._generate_tone(300, 700, 0.25, volume=0.45, wave_type="sine")
        # 5. Exploze houby (plesknutí mokré houby o tabuli/zeď)
        self.sounds["explode_sponge"] = self._generate_tone(220, 60, 0.35, volume=0.7, noise=True)
        # 6. Zásah polštářku (tlumený úder s peřím)
        self.sounds["hit"] = self._generate_tone(350, 90, 0.12, volume=0.55, noise=True)
        # 7. Smrt polštářku (vyfouknutí)
        self.sounds["death"] = self._generate_tone(500, 80, 0.4, volume=0.6, wave_type="saw")
        # 8. Přebíjení (klik - klik)
        self.sounds["reload"] = self._generate_tone(600, 950, 0.1, volume=0.35, wave_type="square")
        # 9. Sebrání bonusu (veselé cinknutí)
        self.sounds["pickup"] = self._generate_tone(523, 1046, 0.18, volume=0.5, wave_type="sine")
        # 10. Školní zvonění na hodinu / konec kola
        self.sounds["bell"] = self._generate_tone(1200, 1150, 0.6, volume=0.5, wave_type="square")

    def toggle_mute(self):
        """Přepne stav ztlumení všech zvuků."""
        self.muted = not self.muted
        return self.muted

    def play(self, sound_name):
        """Přehraje daný zvuk pokud je k dispozici."""
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
