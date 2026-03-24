import RPi.GPIO as GPIO
import time

# GPIO Modus (BCM = GPIO Nummern, nicht Pin-Nummern)
GPIO.setmode(GPIO.BCM)

# Liste aller nutzbaren GPIOs (angepasst für Raspberry Pi 4)
gpio_pins = [
#    2, 3, 
    4, 17, 27, 22,
    10,14,15,1,7,8,9,11,
    5, 6, 13, 19, 26,
    12, 16, 20, 21,
    18, 23, 24, 25
]

# Setup aller Pins als Input mit Pull-Up
for pin in gpio_pins:
    print("Setup GPIO " + str(pin))
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Starte GPIO Scan... (STRG+C zum Beenden)\n")

try:
    while True:
        for pin in gpio_pins:
            state = GPIO.input(pin)

            if state == GPIO.LOW:
                print(f"GPIO {pin} ist AKTIV (LOW)")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nBeendet")

finally:
    GPIO.cleanup()






