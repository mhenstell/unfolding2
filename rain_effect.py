import random
import pygame
import colorsys
import time
import argparse

from util import create_artnet_pentagon_senders, send_dmx
from util import STRIP_LENS

# Output setup
# Uncomment to use local Simulator
target_ips = ['127.0.0.1', '127.0.0.1']

# Uncomment to send data to two Advateks
# may throw errors if both are not connected
# target_ips = ['192.168.0.50', '192.168.0.51']

# Defines
DMX_UNIVERSES = range(0, 90)
EDGE_START_UNIVERSE = 80

# Preview window
height = 620
width = 2000

# Strip constants
NUM_PANEL_STRIPS = 16 * 20
LEDS_PER_PANEL_STRIP = 120
PIXELS_PER_CHAR = 6
CHARS_PER_PANEL_STRIP = LEDS_PER_PANEL_STRIP // PIXELS_PER_CHAR
STRIPS_PER_PANEL = 16
NUM_PANELS = 10

# Color constants
HUE_GREEN = 120
LEAD_SAT = 190 # saturations that still look green to me range from 160-255
LEAD_VAL = 255
TRAIL_SAT = 255
MAX_TRAIL_GREEN_VAL = 128

# animation constants
MIN_DECAY = 2 #// 13/256 is about 5%
MAX_DECAY = 30 #// 77/256 is about 30%
DECAY_RANGE = 10

MAX_RESPAWN_DELAY = -10
MIN_RESPAWN_DELAY = 0


def hsv2rgb(h,s,v):
    if v > 255: v = 255
    elif v < 0: v = 0
    t = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/255,s/255,v/255))
    return t

class MatrixAnimation:
    def __init__(self):
        self.led_data = [[(0, 0, 0) for _ in range(LEDS_PER_PANEL_STRIP)] for _ in range(NUM_PANEL_STRIPS)]
        self.strand_avg_decay = [random.randrange(MIN_DECAY, MAX_DECAY + 1) for _ in range(NUM_PANEL_STRIPS)]
        self.lit_char = [random.randrange(0, CHARS_PER_PANEL_STRIP) for _ in range(NUM_PANEL_STRIPS)]

    def _set_pixel(self, strand, pixel, color):
        self.led_data[strand][pixel] = color

    def _set_char_color(self, strand, char, color):
        if char < 0: return
        if char >= CHARS_PER_PANEL_STRIP: return
        for pixel in range(PIXELS_PER_CHAR - 1):
            self._set_pixel(strand, char * PIXELS_PER_CHAR + pixel, color)

    def _fade_pixel_by(self, strand, pixel, value):
        old = self.led_data[strand][pixel]
        r = max(0, old[0] - value)
        g = max(0, old[1] - value)
        b = max(0, old[2] - value)
        self.led_data[strand][pixel] = (r, g, b)

    def _fade_char_by(self, strand, char, value):
        for pixel in range(PIXELS_PER_CHAR - 1):
            self._fade_pixel_by(strand, char * PIXELS_PER_CHAR + pixel, value)

    def _crop_leds(self, led_data):
        # This is a total hack to crop the crop the pixels because
        # we don't have as many output pixels as we do in the pattern here
        # also I needed to flip some of them upside down because I'm bad at math
        # please don't look at this
        output = []

        for panel in range(NUM_PANELS):
            for strip in range(STRIPS_PER_PANEL):
                for led in range(STRIP_LENS[strip]):
                    if panel % 2 == 0:
                        led = STRIP_LENS[strip] - led
                    pix = led_data[(STRIPS_PER_PANEL * panel) + strip][led]
                    output.append(pix)
        return output

    def get_frame(self, ticks=None):

        # Set the LED states for each panel strip
        for strand in range(NUM_PANEL_STRIPS):
            # Set lead char color
            char = self.lit_char[strand]
            color = hsv2rgb(HUE_GREEN, LEAD_SAT, LEAD_VAL)
            self._set_char_color(strand, char, color)

            # Set trails
            char = self.lit_char[strand] - 1
            color = hsv2rgb(HUE_GREEN, TRAIL_SAT, MAX_TRAIL_GREEN_VAL)
            self._set_char_color(strand, char, color)

            # Set decay for rest of chars
            for char in range(CHARS_PER_PANEL_STRIP):
                char_decay = random.randrange(max(0, self.strand_avg_decay[strand] - DECAY_RANGE), self.strand_avg_decay[strand] + DECAY_RANGE + 1)
                self._fade_char_by(strand, char, char_decay)

            self.lit_char[strand] += 1
            if self.lit_char[strand] == CHARS_PER_PANEL_STRIP + 5:
                self.lit_char[strand] = random.randrange(MAX_RESPAWN_DELAY, MIN_RESPAWN_DELAY) 

        # Crop the output and invert the bottom panels
        output = self._crop_leds(self.led_data)
        return output

    def get_raw_led_data(self):
        return self.led_data


def draw_leds(surface, led_data):
    """ Draw the LEDs for the pygame preview window"""
    for strip_idx, strip in enumerate(led_data):
      x = (strip_idx * 15) + 5

      for led_idx, led in enumerate(strip):
            y = (led_idx * 5) + 5

            color = led_data[strip_idx][led_idx]
            pygame.draw.circle(surface, color, (x, y), 1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Unfolding Humanity Video Player',
        description='This program reverse-projects a video file onto the LEDs on Unfolding Humanity')
    parser.add_argument('-p', '--preview', action='store_true', help="Show a 2D preview of the movie")
    parser.add_argument('--fps', default=15, help="Frames Per Second for the DMX output")
    args = parser.parse_args()

    pentagon_senders = create_artnet_pentagon_senders(DMX_UNIVERSES[:EDGE_START_UNIVERSE], target_ips, int(args.fps))
    # edge_senders = create_artnet_edge_senders(DMX_UNIVERSES[EDGE_START_UNIVERSE:], target_ips, int(args.fps))

    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    animation = MatrixAnimation()

    if args.preview:
        screen = pygame.display.set_mode((width, height))

    while True:

        pygame.event.get()

        led_data = animation.get_frame()
        
         # Send the DMX data
        if len(led_data):
            send_dmx(led_data, pentagon_senders, DMX_UNIVERSES[:EDGE_START_UNIVERSE])

        if args.preview:
            screen.fill("black")
            draw_leds(screen, animation.get_raw_led_data())
            pygame.display.flip()

        clock.tick(args.fps)
