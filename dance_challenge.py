from arduino import *
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()

def setup():
  alvik.begin()
  delay(1000)

def loop():
  # Step forward and back twice (like bouncing)
  alvik.set_wheels_speed(15,15)
  delay(800)
  alvik.set_wheels_speed(-15,-15)
  delay(800)

  alvik.set_wheels_speed(15,15)
  delay(800)
  alvik.set_wheels_speed(-15,-15)
  delay(800)

  # Spin left then right
  alvik.set_wheels_speed(-20,20)
  delay(1000)
  alvik.set_wheels_speed(20,-20)
  delay(1000)

  # Do a wiggle (left curve then right curve)
  alvik.set_wheels_speed(15,8)
  delay(800)
  alvik.set_wheels_speed(8,15)
  delay(800)

  # Finish with a small forward circle
  alvik.set_wheels_speed(18,10)
  delay(1200)
  alvik.stop()
  delay(500)

def cleanup():
  alvik.stop()

start(setup, loop, cleanup)
