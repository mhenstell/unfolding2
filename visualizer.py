# Example file showing a basic pygame "game loop"
import pygame
import json
import math
from stupidArtnet import StupidArtnetServer
from util import draw_pentagon, draw_leds, draw_edge_strips, grouper
from util import normalize_leds

# Magic number derived from careful experimentation
# with integers between 5 and 10
DIVISOR = 7

FULLSCREEN = False

# Physial space defines
WINDOW_STEP_X = 120.65 / DIVISOR
WINDOW_STEP_Y = 100.1 / DIVISOR
WINDOW_CENTER_OFFSET_X = 63.5 / DIVISOR
WINDOW_CENTER_OFFSET_Y = 12.7 / DIVISOR
LEDS_PER_WINDOW = 5
LED_SPACING = ((1 / 60) * 1000) / DIVISOR

# Color defints
COLOR_LOWLIGHT = (50, 50, 50)

# LED defines
LEDS_PER_PANEL = 1328
LEDS_PER_HALF = LEDS_PER_PANEL // 2
CHANNELS_PER_HALF = LEDS_PER_HALF * 3
CHANNELS_PER_10_FACES = LEDS_PER_PANEL * 10 * 3
LEDS_PER_EDGE_STRIP = 42 * 5 # 42 LEDs per edge, five edges per strip

# Pentagon strip lengths 0-15 (8-15 are mirrored)
strip_lens = [29, 53, 77, 89, 95, 101, 107, 113, 29, 53, 77, 89, 95, 101, 107, 113]

DMX_UNIVERSES_ALL = range(0, 90) # Using DMX universes 0 - 79 for the pentagons and 80-89 for the edge strips

# Set initial values
radius = 1191.844 / DIVISOR
xstep = radius * 0.95
y_upper = radius
y_lower = y_upper + radius * 1.3

def check_dmx(server):
    pentagon_output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]
    edge_output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]

    for universe in range(0,90):
        buf = server.get_buffer(universe)

        if len(buf) > 0:
            buf = grouper(buf, 3)
            start = universe * 170
            end = start + 170
            
            # print(universe)
            if universe < 80:
                pentagon_output[ start : end ] = buf
            else:
                # print(f"Putting universe {universe} into edge")
                start -= (80 * 170)
                end -= (80 * 170)

                # print(start, end)

                edge_output[ start : end ] = buf

    return pentagon_output, edge_output 

if __name__ == "__main__":

    # Initialize pygame
    pygame.init()
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((radius * 10.75, y_lower + radius))

    clock = pygame.time.Clock()
    running = True

    # Start artnet listeners
    artnet = StupidArtnetServer()
    artnet_listeners = [ artnet.register_listener(x) for x in DMX_UNIVERSES_ALL ]
    print(f"Registered {len(artnet_listeners)} listeners")

    done = False    

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        led_data, edge_colors = check_dmx(artnet)
        
        edge_positions = []

        for p in range(0, 10, 2):

            # Draw the lower pentagon
            center_lower = (radius + (xstep * p), y_lower)
            draw_pentagon(screen, radius, center_lower, True)

            # Draw the LEDs on the lower pentagon
            colors = led_data[ (p * LEDS_PER_PANEL) : (p * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
            pos = draw_leds(screen, center_lower, colors, strip_lens, WINDOW_STEP_X, WINDOW_STEP_Y, WINDOW_CENTER_OFFSET_X, WINDOW_CENTER_OFFSET_Y, LED_SPACING, True)
            # led_positions.extend(pos)

            # Draw the upper pentagon
            center_upper = (radius + (xstep * (p + 1)), y_upper)
            draw_pentagon(screen, radius, center_upper, False)
            
            # Draw the LEDs on the upper pentagon
            colors = led_data[ ((p + 1) * LEDS_PER_PANEL) : ((p + 1) * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
            pos = draw_leds(screen, center_upper, colors, strip_lens, WINDOW_STEP_X, WINDOW_STEP_Y, WINDOW_CENTER_OFFSET_X, WINDOW_CENTER_OFFSET_Y, LED_SPACING, False)

            # Draw the LEDs for the edge strips
            colors = edge_colors[ ((p//2) * LEDS_PER_EDGE_STRIP) : ((p//2) * LEDS_PER_EDGE_STRIP) + LEDS_PER_EDGE_STRIP ]
            edge_pos = draw_edge_strips(screen, radius, center_lower, center_upper, colors)

            edge_positions += edge_pos

        # Write out normalized edge positions to json file
        # pos = []
        # print(len(edge_positions))
        # for strip in edge_positions:
        #     for x in strip:
        #         pos.append(x)
        # normalize_leds(pos, "edge_positions_normalized.json")
        # sys.exit()


        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    # optional: if multicast was previously joined
    print("Leaving DMX universes")
    for listener in artnet_pentagon_listeners:
        del listener
    for listener in artnet_edge_listeners:
        del listener
    pygame.quit()