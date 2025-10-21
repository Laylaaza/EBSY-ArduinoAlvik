from arduino_alvik import ArduinoAlvik
from time import ticks_ms, ticks_diff, sleep_ms
import sys

# ==============================
# Full path logic
# Drive forward, log colours
# Stop when obstacle < FRONT_STOP_CM
# Find unique colour, reverse to it + centre, then exit tile
# ==============================

BASE_SPEED    = 30
FRONT_STOP_CM = 5
LOG_INTERVAL  = 3000      # ms between colour logs (~10 cm)
EXTRA_CM      = 5         # extra distance to centre on tile (~half tile)
TURN_SPEED    = 25
TURN_TIME_MS  = 900       # adjust for 90° turn
EXIT_TIME_MS  = 2000      # how long to drive forward off the tile (~20 cm)
SAMPLE_MS     = 80

def front_cm(bot):
    try:
        return float(bot.get_distance()[0])
    except Exception:
        return 999.0

def read_colour(bot):
    try:
        return bot.get_color_label()
    except Exception:
        return None

def drive_straight(bot):
    bot.set_wheels_speed(BASE_SPEED, BASE_SPEED)

def drive_reverse(bot):
    bot.set_wheels_speed(-BASE_SPEED, -BASE_SPEED)

def stop(bot):
    bot.brake()

def turn_left(bot):
    bot.set_wheels_speed(-TURN_SPEED, TURN_SPEED)
    sleep_ms(TURN_TIME_MS)
    stop(bot)

def turn_right(bot):
    bot.set_wheels_speed(TURN_SPEED, -TURN_SPEED)
    sleep_ms(TURN_TIME_MS)
    stop(bot)

def find_unique_index(colours):
    """Return (unique_colour, index_position) where index starts at 0."""
    for i, c in enumerate(colours):
        if colours.count(c) == 1:
            return c, i
    return None, None

# =====================================
# MAIN
# =====================================
alvik = ArduinoAlvik()
alvik.begin()

# Wait for OK button
while alvik.get_touch_ok():    sleep_ms(40)
while not alvik.get_touch_ok(): sleep_ms(40)

colour_log = []
last_log_time = ticks_ms()

try:
    drive_straight(alvik)

    # --- FORWARD DRIVE LOOP ---
    while True:
        f = front_cm(alvik)

        # Log colour every LOG_INTERVAL
        if ticks_diff(ticks_ms(), last_log_time) >= LOG_INTERVAL:
            colour = read_colour(alvik)
            if colour:
                colour_log.append(colour)
                print(f"Saved colour: {colour}")
            last_log_time = ticks_ms()

        if f < FRONT_STOP_CM:
            stop(alvik)
            break

        sleep_ms(SAMPLE_MS)

    print("[FINAL COLOURS] " + ", ".join(colour_log))

    # --- FIND UNIQUE COLOUR AND ITS INDEX ---
    unique, index = find_unique_index(colour_log)
    if unique is None:
        print("No unique colour found.")
        sys.exit(0)

    print(f"Unique colour: {unique} (position {index + 1} in list)")

    # How many colours were scanned AFTER the unique one
    colours_after = len(colour_log) - (index + 1)
    print(f"Colours after unique: {colours_after}")

    if colours_after < 0:
        print("Already at or before the unique colour.")
        sys.exit(0)

    # --- REVERSE BACKWARDS FOR THE SAME NUMBER OF STEPS + HALF STEP EXTRA ---
    print("Reversing the same distance (plus extra 5 cm to centre on tile)...")
    drive_reverse(alvik)

    # Each logged colour ≈ LOG_INTERVAL milliseconds (~10 cm)
    reverse_time = (colours_after * LOG_INTERVAL) + (LOG_INTERVAL // 2)
    start_time = ticks_ms()

    while ticks_diff(ticks_ms(), start_time) < reverse_time:
        sleep_ms(SAMPLE_MS)

    stop(alvik)
    print(f"Stopped after reversing ~{(colours_after * 10) + EXTRA_CM} cm")
    print(f"Now positioned approximately in the middle of the unique colour: {unique}")

    # --- EXIT TILE ---
    print("Turning and exiting the tile...")

    # choose one direction – change to turn_right(alvik) if you prefer
    turn_left(alvik)
    drive_straight(alvik)
    sleep_ms(EXIT_TIME_MS)
    stop(alvik)

    print("Exited the unique colour tile. Task complete!")

except KeyboardInterrupt:
    stop(alvik)
    sys.exit(0)
