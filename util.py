import math
import pygame

PACKET_SIZE = 510

# Color defints
COLOR_LOWLIGHT = (50, 50, 50)
COLOR_BLACK = (0, 0, 0)

def led_to_packet(led_data, universe):
    start = universe * 170
    end = start + 170
    leds = led_data[start:end]
    return [i for sub in leds for i in sub]

def send_dmx(led_data, senders, dmx_universes):
    for universe in range(dmx_universes):
        # print(f"Sending universe {universe}")
        packet = led_to_packet(led_data, universe)

        # Pad out the last packet
        if len(packet) != PACKET_SIZE:
            packet += [ 0 for _ in range(PACKET_SIZE - len(packet))]

        senders[universe].set(packet)

def get_led_pos_inv(center, strip_lens, window_step_x, window_step_y, window_center_offset_x, window_center_offset_y, led_spacing):
    output = []
    for strip in range(0, 16):

        if strip in range(0, 8):
            xpos =  center[0] - ((7 - strip) * window_step_x) - window_center_offset_x
        else:
            xpos =  center[0] + ((15 - strip) * window_step_x) + window_center_offset_x

        for led in range(strip_lens[strip]):
            if strip == 0:
                window_ypos = center[1] + window_center_offset_y
            elif strip == 1:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 3)
            elif strip == 2:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 7)
            elif strip < 8:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 8)
            elif strip == 8:
                window_ypos = center[1] + window_center_offset_y
            elif strip == 9:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 3)
            elif strip == 10:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 7)
            elif strip >= 11:
                window_ypos = center[1] + window_center_offset_y + (window_step_y * 8)

            start_ypos = window_ypos + (led_spacing * 2)
            ypos = start_ypos - (led_spacing * led)
            output.append((xpos, ypos))
    return output

def get_led_pos(center, strip_lens, window_step_x, window_step_y, window_center_offset_x, window_center_offset_y, led_spacing):
    output = []
    for strip in range(0, 16):
        if strip in range(0, 8):
            xpos = center[0] + ((8 - strip) * window_step_x) - window_center_offset_x
        else:
            xpos = center[0] - ((15 - strip) * window_step_x) - window_center_offset_x

        for led in range(strip_lens[strip]):
            if strip == 0:
                window_ypos = center[1] - window_center_offset_y
            elif strip == 1:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 3)
            elif strip == 2:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 7)
            elif strip < 8:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 8)
            elif strip == 8:
                window_ypos = center[1] - window_center_offset_y
            elif strip == 9:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 3)
            elif strip == 10:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 7)
            elif strip >= 11:
                window_ypos = center[1] - window_center_offset_y - (window_step_y * 8)

            start_ypos = window_ypos - (led_spacing * 2)
            ypos = start_ypos + (led_spacing * led)
            output.append((xpos, ypos))
    return outpu

def draw_leds(surface, center, colors, strip_lens, window_step_x, window_step_y, window_center_offset_x, window_center_offset_y, led_spacing, inv=False):
    if inv:
        led_positions = get_led_pos_inv(center, strip_lens, window_step_x, window_step_y, window_center_offset_x, window_center_offset_y, led_spacing)
    else:
        led_positions = get_led_pos(center, strip_lens, window_step_x, window_step_y, window_center_offset_x, window_center_offset_y, led_spacing)

    for idx, led in enumerate(led_positions):
        color = colors[idx]
        if color[2] == None:
            continue
        pygame.draw.circle(surface, color, led, 1)

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