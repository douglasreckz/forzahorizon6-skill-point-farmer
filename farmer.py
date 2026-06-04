"""
Forza Horizon - Event Lab Skill Point Farmer
=============================================
Author : swEd9984
Usage  : python farmer.py

How it works:
  1. Detects the "Start Race Event" screen and presses Enter
  2. Holds the accelerator key (W) for the configured race duration
  3. Detects the result screen and presses Restart
  4. Detects the "Restart Event" confirmation popup and confirms Yes
  5. Loops forever

Requirements:
  pip install -r requirements.txt

NOTE: Keep Forza Horizon as the active window.
      Press CTRL+C at any time to stop the bot.
"""

import time
import sys
import pyautogui
import keyboard
import numpy as np
import cv2
from PIL import ImageGrab

# ============================================================
#  SETTINGS  —  edit these to match your setup
# ============================================================

# Monitor resolution
SCREEN_W = 1920
SCREEN_H = 1080

# Race duration in seconds — add a few extra seconds as safety margin.
# The "10x Under 25 sec" event takes ~25 s, so 35 s is a safe value.
RACE_DURATION_SECONDS = 35

# Keyboard key mapped to the accelerator in-game (default: W)
# Change to "up" if you use the arrow keys.
ACCELERATOR_KEY = "w"

# Seconds between screen-state checks
SCAN_INTERVAL = 0.5

# Seconds to wait after pressing a button
ACTION_DELAY = 1.0

# ============================================================
#  BOT STATE
# ============================================================

running      = True
paused       = False
cycle_count  = 0
start_time   = time.time()

# ============================================================
#  HELPERS
# ============================================================

def log(msg: str, level: str = "INFO") -> None:
    elapsed = int(time.time() - start_time)
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
    icons = {"INFO": "✅", "WARN": "⚠️ ", "ERR": "❌", "ACT": "🎮", "SCAN": "🔍"}
    icon = icons.get(level, "   ")
    print(f"[{h:02d}:{m:02d}:{s:02d}] {icon} {msg}")


def take_screenshot() -> np.ndarray:
    """Capture the full screen and return a BGR numpy array."""
    img = ImageGrab.grab()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def color_region_present(
    bgr_image: np.ndarray,
    hsv_lower: np.ndarray,
    hsv_upper: np.ndarray,
    min_pixels: int = 50,
) -> bool:
    """
    Return True if at least *min_pixels* pixels inside *bgr_image* fall
    within the HSV range [hsv_lower, hsv_upper].
    """
    hsv   = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
    mask  = cv2.inRange(hsv, hsv_lower, hsv_upper)
    return int(cv2.countNonZero(mask)) >= min_pixels


def press_key(key: str, hold: float = 0.1) -> None:
    """Press and release a key."""
    keyboard.press(key)
    time.sleep(hold)
    keyboard.release(key)


def hold_key_for(key: str, duration: float) -> None:
    """Hold a key down for *duration* seconds, logging progress every 5 s."""
    log(f"Holding '{key}' for {duration}s  (race in progress)", "ACT")
    keyboard.press(key)

    elapsed  = 0.0
    interval = 1.0
    while elapsed < duration:
        if not running:
            break
        time.sleep(interval)
        elapsed   += interval
        remaining  = duration - elapsed
        if remaining > 0 and int(elapsed) % 5 == 0:
            log(f"Race in progress... {remaining:.0f}s remaining", "SCAN")

    keyboard.release(key)
    log("Accelerator released — waiting for result screen...", "ACT")

# ============================================================
#  SCREEN DETECTORS
# ============================================================

def detect_start_race_screen(screenshot: np.ndarray) -> bool:
    """
    Detect the 'Start Race Event' menu screen.

    The selected menu item is outlined with a bright lime-green border.
    We look for that colour in the lower-left quadrant of the screen
    (where the menu always appears).
    """
    lower = np.array([35, 180, 180])  # HSV
    upper = np.array([75, 255, 255])

    h, w  = screenshot.shape[:2]
    roi   = screenshot[int(h * 0.50) : int(h * 0.90), 0 : int(w * 0.40)]
    return color_region_present(roi, lower, upper, min_pixels=30)


def detect_result_screen(screenshot: np.ndarray) -> bool:
    """
    Detect the post-race results / leaderboard screen.

    The leaderboard header row is filled with a bright yellow-lime colour
    that is unique to this screen.
    """
    lower = np.array([25, 200, 200])  # HSV
    upper = np.array([40, 255, 255])

    h, w  = screenshot.shape[:2]
    roi   = screenshot[int(h * 0.05) : int(h * 0.60), int(w * 0.10) : int(w * 0.90)]
    return color_region_present(roi, lower, upper, min_pixels=100)


def detect_restart_confirm_screen(screenshot: np.ndarray) -> bool:
    """
    Detect the 'Restart Event — Are you sure?' confirmation popup.

    The 'Yes' button has a solid bright lime-yellow background that
    distinguishes it from the rest of the UI.
    """
    lower = np.array([28, 220, 220])  # HSV
    upper = np.array([38, 255, 255])

    h, w  = screenshot.shape[:2]
    roi   = screenshot[int(h * 0.30) : int(h * 0.70), int(w * 0.25) : int(w * 0.75)]
    return color_region_present(roi, lower, upper, min_pixels=200)

# ============================================================
#  STATE MACHINE
# ============================================================

STATE_WAITING_START   = "WAITING_FOR_START"
STATE_RACING          = "RACING"
STATE_WAITING_RESULT  = "WAITING_FOR_RESULT"
STATE_WAITING_CONFIRM = "WAITING_FOR_CONFIRM"


def bot_loop() -> None:
    global running, paused, cycle_count

    state = STATE_WAITING_START

    log("Bot started! Navigate to the Event Lab race in-game.", "INFO")
    log(f"Screen resolution : {SCREEN_W}x{SCREEN_H}", "INFO")
    log(f"Race duration     : {RACE_DURATION_SECONDS}s", "INFO")
    log("Press CTRL+C to stop at any time.\n", "INFO")

    # 5-second countdown so you can alt-tab back into the game
    for i in range(5, 0, -1):
        log(f"Starting in {i}s… (focus Forza Horizon now!)", "WARN")
        time.sleep(1)

    log("Bot active — scanning for start screen…\n", "INFO")

    while running:
        if paused:
            time.sleep(0.5)
            continue

        try:
            screenshot = take_screenshot()

            # ── STATE 1: Wait for "Start Race Event" ──────────────────────
            if state == STATE_WAITING_START:
                log("Scanning for 'Start Race Event' screen…", "SCAN")

                if detect_start_race_screen(screenshot):
                    log("Start screen detected — pressing Enter!", "ACT")
                    time.sleep(0.3)
                    press_key("enter")
                    time.sleep(ACTION_DELAY * 2)   # wait for loading screen

                    log("Race started — accelerating…", "ACT")
                    state = STATE_RACING
                else:
                    time.sleep(SCAN_INTERVAL)

            # ── STATE 2: Race in progress ──────────────────────────────────
            elif state == STATE_RACING:
                hold_key_for(ACCELERATOR_KEY, RACE_DURATION_SECONDS)
                state = STATE_WAITING_RESULT

            # ── STATE 3: Wait for result screen ───────────────────────────
            elif state == STATE_WAITING_RESULT:
                log("Waiting for result screen…", "SCAN")

                if detect_result_screen(screenshot):
                    log("Result screen detected — pressing Restart (X)…", "ACT")
                    time.sleep(0.5)
                    press_key("x")
                    time.sleep(ACTION_DELAY)
                    state = STATE_WAITING_CONFIRM
                else:
                    time.sleep(SCAN_INTERVAL)

            # ── STATE 4: Wait for "Restart Event" confirmation ────────────
            elif state == STATE_WAITING_CONFIRM:
                log("Waiting for restart confirmation popup…", "SCAN")

                if detect_restart_confirm_screen(screenshot):
                    log("Confirmation popup detected — selecting Yes…", "ACT")
                    time.sleep(0.3)
                    press_key("enter")
                    time.sleep(ACTION_DELAY * 3)   # wait for loading screen

                    cycle_count += 1
                    elapsed_total = int(time.time() - start_time)
                    avg = elapsed_total // max(cycle_count, 1)
                    log(f"✨ Cycle #{cycle_count} done!  "
                        f"Total: {elapsed_total}s  |  Avg: ~{avg}s/cycle\n", "INFO")

                    state = STATE_WAITING_START

                elif detect_start_race_screen(screenshot):
                    # Some builds skip the popup and go straight back to the menu
                    log("Skipped confirmation — back at start screen.", "INFO")
                    cycle_count += 1
                    state = STATE_WAITING_START

                else:
                    time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            break
        except Exception as exc:
            log(f"Unexpected error: {exc}", "ERR")
            time.sleep(1)

    log(f"\nBot stopped. Completed cycles: {cycle_count}", "INFO")

# ============================================================
#  CALIBRATION MODE
# ============================================================

def calibration_mode() -> None:
    """
    Capture screenshots of each game screen and report the HSV values of the
    most vibrant pixels.  Use these values to fine-tune the detector constants
    above if the bot fails to detect your particular resolution or HDR setting.
    """
    print("\n=== CALIBRATION MODE ===")
    print("Navigate to each screen in-game, then press ENTER here to capture it.\n")

    screens = [
        ("Start Race Event menu",       "debug_start_race.png"),
        ("Post-race result screen",     "debug_result.png"),
        ("Restart confirmation popup",  "debug_restart_confirm.png"),
    ]

    for name, filename in screens:
        input(f"Go to '{name}' and press ENTER…")
        time.sleep(0.5)

        shot = take_screenshot()
        cv2.imwrite(filename, shot)

        hsv          = cv2.cvtColor(shot, cv2.COLOR_BGR2HSV)
        bright_mask  = cv2.inRange(hsv, np.array([0, 150, 150]), np.array([180, 255, 255]))
        ys, xs       = np.where(bright_mask > 0)

        print(f"\n  Screen : {name}")
        print(f"  Saved  : {filename}")

        if len(ys) > 0:
            indices = np.random.choice(len(ys), min(10, len(ys)), replace=False)
            print("  Sample vibrant pixels (H, S, V):")
            for idx in indices:
                y, x = ys[idx], xs[idx]
                h_v, s_v, v_v = hsv[y, x]
                print(f"    ({x:4d}, {y:4d})  →  H={h_v:3d}  S={s_v:3d}  V={v_v:3d}")
        else:
            print("  No vibrant pixels found — check your game brightness/HDR settings.")

    print("\nCalibration complete!  Adjust the HSV ranges in the detector functions above.")

# ============================================================
#  ENTRY POINT
# ============================================================

def main() -> None:
    print("=" * 60)
    print("  FORZA HORIZON — EVENT LAB SKILL POINT FARMER")
    print("  github.com/swEd9984/forza-skillpoint-farmer")
    print("=" * 60)
    print()
    print("  [1]  Start farming")
    print("  [2]  Calibration mode  (fix detection issues)")
    print()

    choice = input("Select (1/2)  [default: 1]: ").strip() or "1"

    if choice == "2":
        calibration_mode()
    else:
        try:
            bot_loop()
        except KeyboardInterrupt:
            global running
            running = False
            log("Interrupted by user.", "WARN")


if __name__ == "__main__":
    main()
