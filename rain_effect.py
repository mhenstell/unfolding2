import random
import pygame
import colorsys
import time
import math
from stupidArtnet import StupidArtnet, StupidArtnetServer
from util import led_to_packet, send_dmx

# Advatek setup
# Simulator
target_ip = '255.255.255.255'
# Actual advatek
# target_ip = '192.168.0.50'

packet_size = 510
DMX_UNIVERSES = range(0, 80)

# Pygame window
height = 620
width = 2000

# Strip constants
NUM_PANEL_STRIPS = 16 * 20
LEDS_PER_PANEL_STRIP = 120
PIXELS_PER_CHAR = 6
CHARS_PER_PANEL_STRIP = LEDS_PER_PANEL_STRIP // PIXELS_PER_CHAR
NUM_PANELS = 10
LEDS_PER_PANEL = 1328
STRIPS_PER_PANEL = 16

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

FPS = 10

led_data = [[(0, 0, 0) for _ in range(LEDS_PER_PANEL_STRIP)] for _ in range(NUM_PANEL_STRIPS)]
strand_avg_decay = [random.randrange(MIN_DECAY, MAX_DECAY + 1) for _ in range(NUM_PANEL_STRIPS)]
lit_char = [random.randrange(0, CHARS_PER_PANEL_STRIP) for _ in range(NUM_PANEL_STRIPS)]

# lit_char = [0] * CHARS_PER_PANEL_STRIP * NUM_PANEL_STRIPS

strip_lens = [29, 53, 77, 89, 95, 101, 107, 113, 29, 53, 77, 89, 95, 101, 107, 113]


def hsv2rgb(h,s,v):
    if v > 255: v = 255
    elif v < 0: v = 0
    t = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/255,s/255,v/255))
    return t

def fade_pixel_by(strand, pixel, value):
    old = led_data[strand][pixel]
    r = max(0, old[0] - value)
    g = max(0, old[1] - value)
    b = max(0, old[2] - value)
    led_data[strand][pixel] = (r, g, b)

def fade_char_by(strand, char, value):
    for pixel in range(PIXELS_PER_CHAR - 1):
        fade_pixel_by(strand, char * PIXELS_PER_CHAR + pixel, value)

def set_pixel(strand, pixel, color):
    led_data[strand][pixel] = color

def draw_leds(surface):
    for strip_idx, strip in enumerate(led_data):
      x = (strip_idx * 15) + 5

      for led_idx, led in enumerate(strip):
            y = (led_idx * 5) + 5

            color = led_data[strip_idx][led_idx]
            pygame.draw.circle(surface, color, (x, y), 1)

def set_char_color(strand, char, color):
    if char < 0: return
    if char >= CHARS_PER_PANEL_STRIP: return
    for pixel in range(PIXELS_PER_CHAR - 1):
        set_pixel(strand, char * PIXELS_PER_CHAR + pixel, color)

def make_it_rain(ticks):

    for strand in range(NUM_PANEL_STRIPS):

        # Set lead char color
        char = lit_char[strand]
        color = hsv2rgb(HUE_GREEN, LEAD_SAT, LEAD_VAL)
        set_char_color(strand, char, color)

        # Set trails
        char = lit_char[strand] - 1
        color = hsv2rgb(HUE_GREEN, TRAIL_SAT, MAX_TRAIL_GREEN_VAL)
        set_char_color(strand, char, color)

        # Set decay for rest of chars
        for char in range(CHARS_PER_PANEL_STRIP):
            char_decay = random.randrange(max(0, strand_avg_decay[strand] - DECAY_RANGE), strand_avg_decay[strand] + DECAY_RANGE + 1)
            fade_char_by(strand, char, char_decay)

        lit_char[strand] += 1
        if lit_char[strand] == CHARS_PER_PANEL_STRIP + 5:
            lit_char[strand] = random.randrange(MAX_RESPAWN_DELAY, MIN_RESPAWN_DELAY)

def crop_leds(data):
    # This is a total hack to crop the crop the pixels because
    # we don't have as many output pixels as we do in the pattern here
    # also I needed to flip some of them upside down because I'm bad at math
    # please don't look at this
    output = []

    for panel in range(NUM_PANELS):
        for strip in range(STRIPS_PER_PANEL):
            for led in range(strip_lens[strip]):
                if panel % 2 == 0:
                    led = strip_lens[strip] - led
                pix = data[(STRIPS_PER_PANEL * panel) + strip][led]
                output.append(pix)
    return output


if __name__ == "__main__":

    senders = []
    for universe in DMX_UNIVERSES:
        senders.append(StupidArtnet(target_ip, universe, packet_size, 30, True, True))
        senders[universe - DMX_UNIVERSES[0]].start()    
    print(f"Created {len(senders)} DMX senders")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True
    ticks = 0

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        make_it_rain(ticks)
        draw_leds(screen)

        # Send the DMX data
        send_dmx(crop_leds(led_data), senders, DMX_UNIVERSES)

        pygame.display.flip()

        clock.tick(FPS)

        ticks += 1

        # optional: if multicast was previously joined
    print("Leaving DMX universes")
    for listener in artnet_listeners:
        del listener

