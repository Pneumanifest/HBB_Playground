import board
import digitalio
import neopixel
import random
import time

# Define button pins
button_pins = [
    board.GP12,  # Button 1
    board.GP13,  # Button 2
    board.GP27,  # Button 3
    board.GP19,  # Button 4 (center button)
    board.GP18,  # Button 5
    board.GP26,  # Button 6
    board.GP25   # Button 7
]

# Define NeoPixel pin and number of pixels
pixel_pin = board.GP20
num_pixels = 7

# Setup buttons
buttons = []
for pin in button_pins:
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP  # Use pull-up
    buttons.append(button)

# Setup NeoPixels
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

# LED Mapping
led_mapping = [6, 5, 2, 3, 4, 1, 0]  # Button to LED mapping

# Helper function to turn off all pixels
def clear_pixels():
    pixels.fill((0, 0, 0))
    pixels.show()

# Helper function to light up a specific pixel with a color
def light_pixel(index, color):
    pixels[led_mapping[index]] = color  # Map button index to LED
    pixels.show()

# Countdown effect
def countdown():
    for color in [(255, 0, 0), (255, 255, 0), (0, 255, 0)]:
        for i in [2, 3, 4]:  # Middle buttons
            light_pixel(i, color)
        time.sleep(0.5)
        clear_pixels()

# Oscillating red effect on wrong guess
def oscillate_red():
    for _ in range(3):  # Repeat 3 times
        for i in [0, 1, 2, 4, 5, 6]:  # All except center
            light_pixel(i, (255, 0, 0))
        light_pixel(3, (0, 0, 0))  # Center off
        time.sleep(0.2)

        for i in [0, 1, 2, 4, 5, 6]:
            light_pixel(i, (0, 0, 0))
        light_pixel(3, (255, 0, 0))  # Center red
        time.sleep(0.2)

# Function to play the pattern
def play_pattern(pattern):
    for index in pattern:
        light_pixel(index, (0, 0, 255))  # Blue color
        time.sleep(0.5)
        clear_pixels()
        time.sleep(0.2)

# Function to get user input
def get_user_input(pattern):
    user_pattern = []
    start_time = time.time()
    
    while len(user_pattern) < len(pattern):
        for i, button in enumerate(buttons):
            if not button.value:  # Button pressed (active LOW)
                time.sleep(0.1)  # Debounce
                if not button.value:  # Confirm button is still pressed
                    light_pixel(i, (0, 255, 0))  # Green color
                    user_pattern.append(i)
                    time.sleep(0.5)
                    clear_pixels()
                    print(f"Button {i + 1} pressed")  # Debugging
                    while not button.value:  # Wait for button release
                        time.sleep(0.01)
                    break
        
        # Check if user pressed wrong button
        if len(user_pattern) > 0 and user_pattern[-1] != pattern[len(user_pattern) - 1]:
            print("Wrong guess!")  # Debugging
            oscillate_red()  # Oscillate red effect
            clear_pixels()  # Clear LEDs after a wrong guess
            return user_pattern
            
        if time.time() - start_time > 15:  # 15 seconds to input
            print("Time up!")  # Debugging
            return user_pattern
            
    return user_pattern

# Function to wait for a double press
def wait_for_double_press():
    press_count = 0
    last_state = False
    start_time = time.time()
    
    while True:
        current_state = buttons[3].value  # Center button
        if not current_state and last_state:  # Button was just pressed
            press_count += 1
            print(f"Press count: {press_count}")  # Debugging
            time.sleep(0.3)  # Debounce
        last_state = current_state
        
        if press_count == 2:
            print("Double press detected!")  # Debugging
            return True
        
        if time.time() - start_time > 5:  # 5 seconds window
            press_count = 0
            start_time = time.time()

# Main game loop
while True:
    # Clear LEDs before starting
    clear_pixels()

    # Wait for double press to start
    if wait_for_double_press():
        # Start countdown
        countdown()

        pattern = []
        while True:
            pattern.append(random.randint(0, num_pixels - 1))  # Add a new step
            print(f"New pattern: {pattern}")  # Debugging
            play_pattern(pattern)  # Show the pattern
            user_pattern = get_user_input(pattern)  # Get user input

            # End game if user input does not match pattern
            if user_pattern != pattern:
                print("Wrong guess!")  # Debugging
                oscillate_red()  # Oscillate red effect
                clear_pixels()  # Clear LEDs after a wrong guess
                break

            # User guessed correctly
            print("Correct guess!")  # Debugging
            for i in range(num_pixels):
                light_pixel(i, (0, 255, 0))  # Flash green
                time.sleep(0.1)
            clear_pixels()

