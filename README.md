# 🛋️ Bulánci: Školní řežba (Classroom Edition)

> **Projekt pro seminář z informatiky**  
> 2D akční střílečka inspirovaná legendární českou hrou *Bulánci*, přenesená do školního prostředí.

---

## 🎯 O projektu
Hra demonstruje klíčové koncepty vývoje počítačových her a programování v Pythonu s využitím knihovny `pygame`:
- **Herní smyčka (Game Loop)** a počítání fyziky nezávisle na snímkové frekvenci pomocí `Delta Time (dt)`.
- **2D Vektorová matematika** (`pygame.math.Vector2`) pro plynulý pohyb, směrové vektory, úhly a rozptyl střel.
- **Detekce kolizí**:
  - Kolize těla Bulánků s překážkami (školní lavice, katedra, zdi) s odděleným klouzáním v osách X a Y.
  - Paprsková detekce (**Raycasting**) pro ověření přímé viditelnosti (Line-of-Sight).
  - Kruhové a obdélníkové kolize střel a plošné poškození (**Area of Effect - AOE**).
- **Umělá inteligence (AI)** botů řízená **konečným stavovým automatem (FSM)**:
  - *Wander* (hlídkování / průzkum třídy)
  - *Chase* (přiblížení se k cíli)
  - *Engage* (zaměření a střelba v dávkách)
  - *Retreat* (ústup za lavici do krytu při přebíjení nebo nízkém zdraví)
  - *Pickup* (běh pro silnější školní zbraň)
- **Částicový systém (Particle System)** pro dynamické efekty peříček z roztržených polštářků, křídového prachu a mokrých louží.
- **Procedurální syntéza zvuku**: Hra nepotřebuje žádné externí WAV/MP3 soubory – všechny zvuky výstřelů, zásahů, exploze houby i školního zvonku jsou generovány v reálném čase matematickou syntézou zvukových vzorků (PCM).

---

## 🎮 Herní režimy
1. **Hra pro 1 hráče (Singleplayer):** Hrajete za červeného polštářka (*Šprt*) proti 3 botům (*Třídní šašek*, *Svačinář*, *Biflovač*).
2. **2 hráči na 1 klávesnici (Multiplayer):** Hrajete s kamarádem na jednom počítači + 2 boti ve třídě.
3. **Duel 2 hráčů (1v1):** Čistý souboj dvou hráčů na jedné klávesnici.

---

## ⌨️ Ovládání

### Hráč 1 (Červený Šprt):
* **Pohyb:** `W`, `S`, `A`, `D`
* **Střelba:** `Mezerník` (Space)

### Hráč 2 (Modrý Záškolák):
* **Pohyb:** Šipky `Nahoru`, `Dolů`, `Doleva`, `Doprava`
* **Střelba:** Pravý `Ctrl`, `Enter` nebo `Numpad 0`

### Společné ovládání:
* `ESC`: Návrat do hlavního menu
* `Mezerník` / `Enter` po konci zápasu: Spuštění dalšího kola

---

## 🎒 Školní výzbroj a zbraně
Zbraně se objevují jako bonusové krabičky na lavicích ve třídě:
* **[K] Křídomet:** Základní zbraň. Zásobník na 5 křídových nábojů, po vystřílení automaticky přebíjí.
* **[X] Kružítko / Rozbitá křída:** Brokovnice vystřelující kužel 4 křídových broků naráz.
* **[R] Pravítkový rychlopal:** Samopal s vysokou kadencí střelby a velkým zásobníkem (24 nábojů).
* **[H] Mokrá houba na tabuli:** Těžký projektil, který při nárazu vybuchne s plošným zásahem a zanechá louži na podlaze.

---

## 🚀 Jak hru spustit

### 1. Požadavky
* Python 3.10 nebo novější (testováno na Python 3.12)
* Knihovna `pygame`

### 2. Instalace závislostí
Otevřete terminál (PowerShell / Příkazový řádek) ve složce projektu a spusťte:
```bash
pip install -r requirements.txt
```

### 3. Spuštění hry
```bash
python main.py
```

---

## 📁 Struktura projektu
```
Bulanci2026/
├── main.py              # Hlavní smyčka, scény Menu, Controls a herní přepínač
├── settings.py          # Globální konfigurace (rozlišení, barvy, zbraně, klávesy)
├── game.py              # Manažer zápasu, kolizí, skóre a vyhodnocení vítěze
├── entities/
│   ├── pillow.py        # Základní třída Bulánka (autentický vzhled, kolize, HUD)
│   ├── player.py        # Třída lidského hráče (zpracování kláves)
│   ├── bot.py           # AI bot s FSM a raycastingem
│   ├── weapon.py        # Logika zbraní, přebíjení a kadence
│   ├── bullet.py        # Projektily (křídy, houba, AOE exploze)
│   └── pickup.py        # Spawnování bonusů na lavicích
├── world/
│   ├── map.py           # Mapa třídy (lavice, katedra, tabule, skříňky)
│   └── particles.py     # Částice peří, prachu a louží
├── audio/
│   └── sound_gen.py     # Procedurální PCM generátor zvukových efektů
├── requirements.txt
└── README.md
```

---

## 🌐 Jak nahrát projekt na GitHub
Pokud na školním počítači není nainstalován program `git`:
1. Vytvořte si nový prázdný repozitář na svém profilu [GitHub.com](https://github.com/new) (např. `bulanci-skolni-rezba`).
2. **Možnost A (přes webové rozhraní GitHubu):**
   - V novém repozitáři klikněte na **"uploading an existing file"**.
   - Označte soubory a složky z této složky a přetáhněte je myší na GitHub.
   - Klikněte na **Commit changes**.
3. **Možnost B (pokud nainstalujete Git for Windows nebo GitHub Desktop):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Bulanci Skolni rezba"
   git branch -M main
   git remote add origin https://github.com/VASI_UZIVATEL/bulanci-skolni-rezba.git
   git push -u origin main
   ```
