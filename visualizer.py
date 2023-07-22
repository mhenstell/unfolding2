# Example file showing a basic pygame "game loop"
import pygame
import json
import math
from stupidArtnet import StupidArtnetServer
from util import draw_pentagon, draw_leds, draw_edge_strips, grouper

panels = []

# def import_json():
#     with open("data.json", "r") as infile:
#         panels = json.load(infile)["panels"]
#     print(panels)

# import_json()


# edge to center first window 63.5mm
# spacing X 76.15mm 
# spacing Y 100.1mm

# +12.7mm (downward) first window from zero
#radius = 1191.844mm

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
strip_lens = [29, 53, 77, 89, 95, 101, 107, 113, 29, 53, 77, 89, 95, 101, 107, 113]

LEDS_PER_EDGE_STRIP = 42 * 5 # 42 LEDs per edge, five edges per strip

# led_data = [ (0, 0, 0) for _ in range(CHANNELS_PER_10_FACES)]

DMX_UNIVERSES_PENTAGONS = range(0, 90) # Using DMX universes 0 - 79 for the pentagons
# DMX_UNIVERSES_EDGES = range(100, 110) # Using DMX universes 100 - 109 for the edges (two universes for each edge strip)

def check_dmx(server):
    pentagon_output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]
    edge_output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]

    for universe in range(0, 80):
        buf = server.get_buffer(universe)

        if len(buf) > 0:
            buf = grouper(buf, 3)
            start = universe * 170
            end = start + 170
            
            if universe < 80:
                pentagon_output[ start : end ] = buf
            else:
                edge_output[ start : end ] = buf

    return pentagon_output, edge_output 

# def check_dmx_edges(server):

#     output = [ (255, 0, 0) for _ in range(LEDS_PER_EDGE_STRIP * 5)]

#     for universe in DMX_UNIVERSES_EDGES:
#         print(f"getting universe {universe}")
#         buf = server.get_buffer(universe)

#         if len(buf) > 0:
#             buf = grouper(buf, 3)
#             start = universe * 170
#             end = start + 170
#             output[ start : end ] = buf

#     return output

# Set initial values
radius = 1191.844 / DIVISOR
xstep = radius * 0.95
y_upper = radius
y_lower = y_upper + radius * 1.3

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
artnet_listeners = [ artnet.register_listener(x) for x in DMX_UNIVERSES_PENTAGONS ]
print(f"Registered {len(artnet_listeners)} listeners")

# artnet_edge_listeners = [ artnet.register_listener(x) for x in DMX_UNIVERSES_EDGES ]
# print(f"Registered {len(artnet_edge_listeners)} listeners for the edge strips")

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
    
    # edge_colors = check_dmx_edges(artnet)

    led_positions = []

    for p in range(0, 10, 2):
        center_lower = (radius + (xstep * p), y_lower)
        draw_pentagon(screen, radius, center_lower, True)

        colors = led_data[ (p * LEDS_PER_PANEL) : (p * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
        pos = draw_leds(screen, center_lower, colors, strip_lens, WINDOW_STEP_X, WINDOW_STEP_Y, WINDOW_CENTER_OFFSET_X, WINDOW_CENTER_OFFSET_Y, LED_SPACING, True)
        # led_positions.extend(pos)

        center_upper = (radius + (xstep * (p + 1)), y_upper)
        draw_pentagon(screen, radius, center_upper, False)
        
        colors = led_data[ ((p + 1) * LEDS_PER_PANEL) : ((p + 1) * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
        pos = draw_leds(screen, center_upper, colors, strip_lens, WINDOW_STEP_X, WINDOW_STEP_Y, WINDOW_CENTER_OFFSET_X, WINDOW_CENTER_OFFSET_Y, LED_SPACING, False)

        # print("color range:")
        # print(f"{((p//2) * LEDS_PER_EDGE_STRIP)} : {((p//2) * LEDS_PER_EDGE_STRIP) + LEDS_PER_EDGE_STRIP} out of maximum {len(edge_colors)}")
        colors = edge_colors[ ((p//2) * LEDS_PER_EDGE_STRIP) : ((p//2) * LEDS_PER_EDGE_STRIP) + LEDS_PER_EDGE_STRIP ]
        edge_pos = draw_edge_strips(screen, radius, center_lower, center_upper, colors)

        # led_positions.extend(pos)

    # Write out the normalized positions of each LED
    # max_x = max(p[0] for p in led_positions)
    # max_y = max(p[1] for p in led_positions)
    # min_x = min(p[0] for p in led_positions)
    # min_y = min(p[1] for p in led_positions)

    # normalized = [ ( led[0] / max_x, led[1] / max_y ) for led in led_positions ]
    # import json
    # if not done:
    #     with open("leds_normalied.json", "w") as outfile:
    #         json.dump(normalized, outfile, indent=2)
    #         done = True
    #         print("writing")

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