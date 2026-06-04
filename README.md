<div align="center">

# 🏎️ Forza Horizon 6 — Event Lab Skill Point Farmer

**Automated screen-reading bot that farms skill points on any Event Lab race loop.**  
Detects game screens via colour analysis (OpenCV) — no image templates, no memory hacking.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 📸 Demo

| Start Race Screen | Result Screen | Restart Confirmation |
|:-----------------:|:-------------:|:--------------------:|
| ![start](screenshots/start_race.png) | ![result](screenshots/result.png) | ![restart](screenshots/restart.png) |

> The bot detects each of these screens automatically and acts accordingly.

---

## ⚙️ How It Works

```
┌─────────────────────┐
│  Start Race screen  │ ◄─────────────────────────────────┐
│  detected → Enter   │                                   │
└────────┬────────────┘                                   │
         │                                                │
         ▼                                                │
┌─────────────────────┐                                   │
│  Hold W key for     │                                   │
│  race duration      │                                   │
└────────┬────────────┘                                   │
         │                                                │
         ▼                                                │
┌─────────────────────┐     ┌──────────────────────────┐  │
│  Result screen      │────►│  Press Restart (X key)   │  │
│  detected           │     └────────────┬─────────────┘  │
└─────────────────────┘                  │                 │
                                         ▼                 │
                              ┌──────────────────────┐     │
                              │  Confirm popup (Yes) │─────┘
                              │  detected → Enter    │
                              └──────────────────────┘
```

The bot uses **HSV colour range detection** on specific screen regions, so it's fast and doesn't require any game memory access or image templates.

---

## 🗂️ Recommended Event

The bot was built and tested on the **"Skillpoint Meta — 10x Under 25 sec"** Event Lab shared by **KennWirUns** using a **1998 Subaru Impreza 22B-STi (S2 805)**.
Event Code 692 410 869

> You can use it with any short looped Event Lab race — just adjust `RACE_DURATION_SECONDS`.

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 / 11
- Python 3.11+ → [python.org/downloads](https://www.python.org/downloads/)  
  ✅ Check **"Add Python to PATH"** during installation
- Forza Horizon running in **English**
- Monitor resolution: **1920 × 1080** (other resolutions require calibration)

### 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/forza-skillpoint-farmer.git
cd forza-skillpoint-farmer
```

### 2 — Install dependencies

> ⚠️ Open your terminal **as Administrator** (required by the `keyboard` library)

```bash
pip install -r requirements.txt
```

### 3 — Configure the bot

Open `farmer.py` and adjust the settings at the top of the file:

```python
RACE_DURATION_SECONDS = 35   # Set to your race length + ~5s buffer
ACCELERATOR_KEY       = "w"  # Change to "up" for arrow keys
SCREEN_W              = 1920 # Your monitor width
SCREEN_H              = 1080 # Your monitor height
```

### 4 — Run

```bash
python farmer.py
```

In-game: navigate to the Event Lab race and leave the **"Start Race Event"** menu on screen.  
The bot does the rest. Press **CTRL+C** to stop at any time.

---

## 🏗️ Build a Standalone EXE

If you want a single `.exe` to share or use without Python:

1. Place `BUILD_EXE.bat` in the same folder as `farmer.py`
2. Right-click → **Run as Administrator**
3. Wait ~2 minutes (installs deps + compiles)
4. `ForzaSkillFarmer.exe` appears in the folder

> The generated `.exe` is fully self-contained — no Python installation needed on the target PC.

---

## 🔧 Calibration (fix detection issues)

If the bot doesn't detect your screens correctly (different resolution, HDR, brightness):

```bash
python farmer.py
# Select option 2 — Calibration Mode
```

Follow the on-screen instructions. The tool captures each game screen and prints the HSV values of the most vibrant pixels, which you can then paste into the detector functions in `farmer.py`.

---

## 📁 Project Structure

```
forza-skillpoint-farmer/
├── farmer.py          # Main bot script
├── requirements.txt   # Python dependencies
├── BUILD_EXE.bat      # One-click EXE compiler (Windows)
├── .gitignore
├── LICENSE
└── screenshots/       # Demo images for this README
```

---

## ⚠️ Disclaimer

This project is intended for **educational and personal use only**.  
Using automation tools may violate the Terms of Service of Forza Horizon.  
**Use at your own risk.** The author is not responsible for any account actions taken by the game publisher.

---

## 📄 License

Released under the [MIT License](LICENSE).  
Feel free to fork, modify, and share.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/douglasreckz">swEd</a>
</div>
