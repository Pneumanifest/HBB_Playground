import time
import board
import digitalio
import neopixel
import usb_hid
import microcontroller
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Configuration of keys and keycodes
keys = [
    {"pin": board.GP25, "keycode": Keycode.ONE},
    {"pin": board.GP26, "keycode": Keycode.TWO},
    {"pin": board.GP27, "keycode": Keycode.THREE},
    {"pin": board.GP19, "keycode": Keycode.FOUR},
    {"pin": board.GP18, "keycode": Keycode.FIVE},
    {"pin": board.GP13, "keycode": Keycode.SIX},
    {"pin": board.GP12, "keycode": Keycode.SEVEN},
]

# Set colors for LEDs
colors = [
    (255, 255, 255),  # White
    (255, 165, 0),    # Orange
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 255, 0),      # Green
    (255, 255, 0),    # yellow
    (128, 0, 128)     # pink
]

# Initialize keys
key_pins = []
for key in keys:
    pin = digitalio.DigitalInOut(key["pin"])
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    key_pins.append(pin)

# Initialize HID-Keyboard
keyboard = Keyboard(usb_hid.devices)

# Initialize NeoPixel
pixel_pin = board.GP20
num_pixels = 8  # Anzahl der NeoPixel anpassen
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=True)

# Storage for colors in NVM
flash = microcontroller.nvm

def save_colors():
    for i in range(len(keys)):
        color = colors[color_indices[i]]
        flash[i*3:i*3+3] = bytes(color)

def load_colors():
    for i in range(len(keys)):
        color = tuple(flash[i*3:i*3+3])
        if color in colors:
            pixels[i] = color
            color_indices[i] = colors.index(color)
        else:
            # Default color if none found
            pixels[i] = colors[0]
            color_indices[i] = 0

# Load saved colors on startup
color_indices = [0] * len(keys)
load_colors()

# Array to store the state of the keys (pressed or not)
key_states = [False] * len(keys)
# Array to store the times of the last key presses
key_press_times = [[] for _ in range(len(keys))]

# Time interval for triple key presses
triple_press_interval = 1.0  # In seconds

while True:
    current_time = time.monotonic()
    for i, key_pin in enumerate(key_pins):
        key = keys[i]

        if not key_pin.value:  # Button pressed
            if not key_states[i]:  # Button was not pressed before
                keyboard.press(Keycode.SHIFT, Keycode.CONTROL, key["keycode"])
                key_states[i] = True
                key_press_times[i].append(current_time)
                
                # Remove old entries that are outside the interval
                key_press_times[i] = [t for t in key_press_times[i] if current_time - t <= triple_press_interval]
                
                # Check if the button has been pressed three times within the interval
                if len(key_press_times[i]) >= 3:
                    color_indices[i] = (color_indices[i] + 1) % len(colors)
                    pixels[i] = colors[color_indices[i]]
                    key_press_times[i] = []  # Reset the list after color change
                    save_colors()  # Save the colors after the color change
                    print(f"Button {i+1} pressed three times quickly. Color changed to {colors[color_indices[i]]}")
            else:
                keyboard.release(Keycode.SHIFT, Keycode.CONTROL, key["keycode"])
        else:  # Button not pressed
            if key_states[i]:  # Button was previously pressed
                keyboard.release(Keycode.SHIFT, Keycode.CONTROL, key["keycode"])
                key_states[i] = False

    time.sleep(0.01)  # Short break to reduce CPU load
