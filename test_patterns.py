import pygame
from stupidArtnet import StupidArtnet, StupidArtnetServer

from util import led_to_packet, send_dmx, get_led_pos, get_led_pos_inv, draw_leds, draw_pentagon, create_artnet_pentagon_senders, create_artnet_edge_senders
from util import COLOR_BLACK, COLOR_LOWLIGHT

FPS = 5

# Output setup
# Uncomment to use local Simulator
target_ips = ['127.0.0.1', '127.0.0.1']

# Uncomment to send data to two Advateks
# may throw errors if both are not connected
# target_ips = ['192.168.0.50', '192.168.0.51']

DMX_UNIVERSES = range(0, 100)

DIVISOR = 7

# Set initial values
radius = 1191.844 / DIVISOR
xstep = radius * 0.95
y_upper = 0
y_lower = radius

# LED defines
LEDS_PER_PANEL = 1328
MAX_HEIGHT = 113
strip_lens = [29, 53, 77, 89, 95, 101, 107, 113, 29, 53, 77, 89, 95, 101, 107, 113]

# Physial space defines
WINDOW_STEP_X = 120.65 / DIVISOR
WINDOW_STEP_Y = 100.1 / DIVISOR
WINDOW_CENTER_OFFSET_X = 63.5 / DIVISOR
WINDOW_CENTER_OFFSET_Y = 12.7 / DIVISOR
LEDS_PER_WINDOW = 5
LED_SPACING = ((1 / 60) * 1000) / DIVISOR
NUM_PANELS = 10

width = radius * 2
height = radius * 2

LEDS_PER_EDGE_STRIP = 42 * 5 # 42 LEDs per edge, five edges per strip

# @receiver.listen_on()  # listens on universe 1
def callback(data, universe):  # packet type: sacn.DataPacket
    pass

def pattern_vert(ticks):
    output = [ COLOR_BLACK for _ in range(LEDS_PER_PANEL * NUM_PANELS)]

    for panel in range(NUM_PANELS):
        for strip_idx in range(len(strip_lens)):

            y = ticks % strip_lens[strip_idx] 
            if panel % 2 == 0:
                y = strip_lens[strip_idx] - y

            led_idx = sum(strip_lens[:strip_idx]) + y + (panel * LEDS_PER_PANEL)
            output[led_idx] = (255, 255, 255)
            
    return output

def pattern_horiz(ticks):

    output = [ COLOR_BLACK for _ in range(LEDS_PER_PANEL * NUM_PANELS)]
    
    for panel in range(NUM_PANELS):
        
        # Pick our line number from the current time
        line_x = ticks % len(strip_lens) + 1

        # Die if we're at the edge to give a short pause between sweeps
        if line_x == len(strip_lens):
            return output
        
        # Invert even panels
        if panel % 2 == 0:
            line_x = 15 - line_x

        # Invert the backwards half of each pentagon face
        if line_x >= 8:
            line_x = (8 - line_x) + 15

        # for every strip going left to right
        for strip_idx in range(len(strip_lens)):

            # if we're on the active strip, light up every led
            if strip_idx == line_x:

                for led in range(strip_lens[strip_idx]):
                    led_idx = sum(strip_lens[:strip_idx]) + led + (panel * LEDS_PER_PANEL)
                    output[led_idx] = (255, 255, 255)
    return output

def pattern_color(ticks):
    output = [ COLOR_BLACK for _ in range(LEDS_PER_PANEL * NUM_PANELS)]

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]

    ticker = ticks // 5 % 4

    for panel in range(NUM_PANELS):

        for led in range(LEDS_PER_PANEL):
            color = colors[(panel + ticker) % 4]
            output[(panel * LEDS_PER_PANEL) + led] = color

    return output


def outer_edge_fill(ticks):

    y = ticks % LEDS_PER_EDGE_STRIP

    output = [ COLOR_BLACK for _ in range(LEDS_PER_EDGE_STRIP * 10)]

    for edge in range(80, 100, 4):
        # only get outer edge strips

        for led in range(LEDS_PER_EDGE_STRIP):
            if led < y:
                output[()]



if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    running = True

    senders = create_artnet_pentagon_senders(DMX_UNIVERSES, target_ips, FPS)

    done = False

    ticks = 0

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        
        led_data = pattern_vert(ticks)
        # led_data = pattern_horiz(ticks)
        # led_data = pattern_color(ticks)


        # Draw the pentagons
        center = (radius, y_lower)
        draw_pentagon(screen, radius, center, True)

        # Draw the LEDs
        colors = led_data[ : LEDS_PER_PANEL]
        pos = draw_leds(screen, center, colors, strip_lens, WINDOW_STEP_X, WINDOW_STEP_Y, WINDOW_CENTER_OFFSET_X, WINDOW_CENTER_OFFSET_Y, LED_SPACING, inv=True)

        # Display graphics
        pygame.display.flip()

        # Send the DMX data
        send_dmx(led_data, senders, DMX_UNIVERSES)

        clock.tick(FPS)

        ticks += 1

    # # optional: if multicast was previously joined
    # print("Leaving DMX universes")
    # for listener in artnet_listeners:
    #     del listener

    pygame.quit()