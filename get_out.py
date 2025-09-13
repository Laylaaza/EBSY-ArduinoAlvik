from arduino_alvik import ArduinoAlvik
from time import sleep_ms
import sys

# Drives straight. If front < FRONT_STOP_CM:
#   rotate left, read front_cm
#   rotate right, read front_cm
#   compare distances from the SAME sensor used for FRONT_STOP_CM
#   face the clearer side and go

BASE_SPEED    = 30
FRONT_STOP_CM = 7
TURN_SPEED    = 25
TURN_90_MS    = 1400     # calibrate for a true 90°
SENSE_SETTLE  = 120
CLEAR_MS      = 600

# Flip if turns are inverted on your wiring.
SWAP_TURNS = False

DEBUG = True
def dbg(*args):
    if DEBUG:
        try:
            print(*args)
        except Exception:
            pass

# Use the SAME element as the front stop check. Do not change its index.
def front_cm(bot):
    return float(bot.get_distance()[0])

def turn_left_90(bot):
    if SWAP_TURNS:
        l, r = TURN_SPEED, -TURN_SPEED   # CW
        dbg(f"[TURN] left_90 (SWAP) speeds=({l},{r}) t={TURN_90_MS}ms")
    else:
        l, r = -TURN_SPEED, TURN_SPEED   # CCW
        dbg(f"[TURN] left_90 speeds=({l},{r}) t={TURN_90_MS}ms")
    bot.set_wheels_speed(l, r)
    sleep_ms(TURN_90_MS)
    bot.brake()

def turn_right_90(bot):
    if SWAP_TURNS:
        l, r = -TURN_SPEED, TURN_SPEED   # CCW
        dbg(f"[TURN] right_90 (SWAP) speeds=({l},{r}) t={TURN_90_MS}ms")
    else:
        l, r = TURN_SPEED, -TURN_SPEED   # CW
        dbg(f"[TURN] right_90 speeds=({l},{r}) t={TURN_90_MS}ms")
    bot.set_wheels_speed(l, r)
    sleep_ms(TURN_90_MS)
    bot.brake()

def drive_straight(bot):
    dbg(f"[MOVE] straight @{BASE_SPEED}")
    bot.set_wheels_speed(BASE_SPEED, BASE_SPEED)

alvik = ArduinoAlvik()
alvik.begin()
dbg(f"[BOOT] SWAP_TURNS={SWAP_TURNS} TURN_90_MS={TURN_90_MS} SENSE_SETTLE={SENSE_SETTLE}")

# wait for OK
while alvik.get_touch_ok():   sleep_ms(40)
while not alvik.get_touch_ok(): sleep_ms(40)
dbg("[STATE] OK pressed, starting")

try:
    while True:
        while not alvik.get_touch_cancel():
            f = front_cm(alvik)
            dbg(f"[SENSE] front={f:.1f}cm")
            if f < FRONT_STOP_CM:
                dbg(f"[STATE] front {f:.1f} < {FRONT_STOP_CM}, scanning")
                alvik.brake()

                # look left, sample SAME front sensor, return to centre
                turn_left_90(alvik)
                sleep_ms(SENSE_SETTLE)
                left_val = front_cm(alvik)
                dbg(f"[SCAN] left-look front_cm={left_val:.1f}cm")
                turn_right_90(alvik)  # back to centre

                # look right, sample SAME front sensor, return to centre
                turn_right_90(alvik)
                sleep_ms(SENSE_SETTLE)
                right_val = front_cm(alvik)
                dbg(f"[SCAN] right-look front_cm={right_val:.1f}cm")
                turn_left_90(alvik)   # back to centre

                # decide which way to face using SAME sensor values
                if left_val > right_val:
                    dbg(f"[DECIDE] LEFT {left_val:.1f} > RIGHT {right_val:.1f} -> face LEFT")
                    turn_left_90(alvik)
                elif right_val > left_val:
                    dbg(f"[DECIDE] RIGHT {right_val:.1f} > LEFT {left_val:.1f} -> face RIGHT")
                    turn_right_90(alvik)
                else:
                    dbg(f"[DECIDE] equal {left_val:.1f} == {right_val:.1f} -> keep forward")

                # move straight a bit
                drive_straight(alvik)
                sleep_ms(CLEAR_MS)
                alvik.brake()
                dbg("[MOVE] brake after clearing")
            else:
                drive_straight(alvik)
                sleep_ms(40)

        alvik.brake()
        dbg("[STATE] Cancel pressed, waiting for OK")
        while not alvik.get_touch_ok():
            sleep_ms(80)
        dbg("[STATE] OK pressed, resuming")

except KeyboardInterrupt:
    dbg("[EXIT] KeyboardInterrupt, stopping")
    alvik.stop()
    sys.exit(0)
