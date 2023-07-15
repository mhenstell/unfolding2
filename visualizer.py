# Example file showing a basic pygame "game loop"
import pygame
import json
import math
from stupidArtnet import StupidArtnetServer
import itertools

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


# led_data = [ (0, 0, 0) for _ in range(CHANNELS_PER_10_FACES)]

DMX_UNIVERSES = range(0, 80)

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return list(itertools.zip_longest(fillvalue=fillvalue, *args))

def get_led_pos_inv(center):
    output = []
    for strip in range(0, 16):

        if strip in range(0, 8):
            xpos =  center[0] - ((7 - strip) * WINDOW_STEP_X) - WINDOW_CENTER_OFFSET_X
        else:
            xpos =  center[0] + ((15 - strip) * WINDOW_STEP_X) + WINDOW_CENTER_OFFSET_X

        for led in range(strip_lens[strip]):
            if strip == 0:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y
            elif strip == 1:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 3)
            elif strip == 2:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 7)
            elif strip < 8:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 8)
            elif strip == 8:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y
            elif strip == 9:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 3)
            elif strip == 10:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 7)
            elif strip >= 11:
                window_ypos = center[1] + WINDOW_CENTER_OFFSET_Y + (WINDOW_STEP_Y * 8)

            start_ypos = window_ypos + (LED_SPACING * 2)
            ypos = start_ypos - (LED_SPACING * led)
            output .append((xpos, ypos))
  
    return output

def get_led_pos(center):
    output = []
    for strip in range(0, 16):
        if strip in range(0, 8):
            xpos = center[0] + ((8 - strip) * WINDOW_STEP_X) - WINDOW_CENTER_OFFSET_X
        else:
            xpos = center[0] - ((15 - strip) * WINDOW_STEP_X) - WINDOW_CENTER_OFFSET_X

        for led in range(strip_lens[strip]):
            if strip == 0:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y
            elif strip == 1:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 3)
            elif strip == 2:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 7)
            elif strip < 8:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 8)
            elif strip == 8:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y
            elif strip == 9:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 3)
            elif strip == 10:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 7)
            elif strip >= 11:
                window_ypos = center[1] - WINDOW_CENTER_OFFSET_Y - (WINDOW_STEP_Y * 8)

            start_ypos = window_ypos - (LED_SPACING * 2)
            ypos = start_ypos + (LED_SPACING * led)
            output.append((xpos, ypos))
    return output

def draw_pentagon(surface, radius, center, inv=False):

    c1 = 0.25 * (math.sqrt(5) - 1)
    c2 = 0.25 * (math.sqrt(5) + 1)
    s1 = 0.25 * (math.sqrt(10 + 2 * (math.sqrt(5))))
    s2 = 0.25 * (math.sqrt(10 - 2 * (math.sqrt(5))))

    inv_mult = -1 if inv is True else 1
    verticies = [ (0, 1), (s1, c1), (s2, -c2), (-s2, -c2), (-s1, c1) ]
    verticies = [ ( x, y * inv_mult ) for x, y in verticies ]
    verticies = [ ( ( x * radius ) + center[0], ( y * radius ) + center[1] ) for x, y in verticies]

    pygame.draw.lines(surface, "white", True, verticies)
    
    pygame.draw.circle(surface, COLOR_LOWLIGHT, center, 2)
    pygame.draw.line(surface, COLOR_LOWLIGHT, (center[0] - radius/2, center[1]), (center[0] + radius/2, center[1]), 1)

def draw_leds(surface, center, colors, inv=False):
    if inv:
        led_positions = get_led_pos_inv(center)
    else:
        led_positions = get_led_pos(center)

    for idx, led in enumerate(led_positions):
        color = colors[idx]
        if color[2] == None:
            continue
        pygame.draw.circle(surface, color, led, 1)
    # return led_positions

def pattern_test():
    output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]
    target = int(pygame.time.get_ticks() / 10)
    output[target] = (255, 255, 255)

    return output

# @receiver.listen_on()  # listens on universe 1
def callback(data, universe):  # packet type: sacn.DataPacket
    # print(f"Received: {packet.dmxData}")  # print the received DMX data
    # universe = packet.universe
    # print(f"Universe: {universe}")
    # slice_start = (universe - 1) * LEDS_PER_HALF
    # slice_end = slice_start + LEDS_PER_HALF
    # print(f"Slice: {slice_start}:{slice_end}")
    # print(f"Total slice: {slice_end - slice_start}")
    # print(f"Received total: {len(packet.dmxData)}")
    # led_data[slice_start:slice_end] = packet.dmxData

    # print(f"Received {len(data)} bytes")
    pass

def check_dmx(server):
    output = [ COLOR_LOWLIGHT for _ in range(LEDS_PER_PANEL * 10)]
    for universe in DMX_UNIVERSES:
        buf = server.get_buffer(universe)

        if len(buf) > 0:
            buf = grouper(buf, 3)
            start = universe * 170
            end = start + 170
            output[ start : end ] = buf

    return output

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

artnet = StupidArtnetServer()
artnet_listeners = [ artnet.register_listener(x, callback_function=callback) for x in DMX_UNIVERSES ]
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

    led_data = check_dmx(artnet)

    led_positions = []

    for p in range(0, 10, 2):
        center = (radius + (xstep * p), y_lower)
        draw_pentagon(screen, radius, center, True)

        colors = led_data[ (p * LEDS_PER_PANEL) : (p * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
        pos = draw_leds(screen, center, colors, True)
        # led_positions.extend(pos)

        center = (radius + (xstep * (p + 1)), y_upper)
        draw_pentagon(screen, radius, center, False)
        
        colors = led_data[ ((p + 1) * LEDS_PER_PANEL) : ((p + 1) * LEDS_PER_PANEL) + LEDS_PER_PANEL ]
        pos = draw_leds(screen, center, colors, False)
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
for listener in artnet_listeners:
    del listener

pygame.quit()