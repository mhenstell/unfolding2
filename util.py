import math
import pygame
import itertools

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
    for universe in dmx_universes:
        # print(f"Sending universe {universe}")
        packet = led_to_packet(led_data, universe)

        # Pad out the last packet
        if len(packet) != PACKET_SIZE:
            packet += [ 0 for _ in range(PACKET_SIZE - len(packet))]

        senders[universe - dmx_universes[0]].set(packet)

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
    return output

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

    pygame.draw.lines(surface, COLOR_LOWLIGHT, True, verticies)
    
    pygame.draw.circle(surface, COLOR_LOWLIGHT, center, 2)
    pygame.draw.line(surface, COLOR_LOWLIGHT, (center[0] - radius/2, center[1]), (center[0] + radius/2, center[1]), 1)

    # pygame.draw.lines(surface, "red", False, edgestrip_verticies, width=5)

def draw_edge_strips(surface, radius, center_lower, center_upper, colors):
    c1 = 0.25 * (math.sqrt(5) - 1)
    c2 = 0.25 * (math.sqrt(5) + 1)
    s1 = 0.25 * (math.sqrt(10 + 2 * (math.sqrt(5))))
    s2 = 0.25 * (math.sqrt(10 - 2 * (math.sqrt(5))))

    edgestrip_verticies_lower = [ (s2, -c2), (s1, c1), (0, 1) ]
    edgestrip_verticies_lower = [ ( x, y * -1 ) for x, y in edgestrip_verticies_lower ]
    edgestrip_verticies_lower = [ ( ( x * radius ) + center_lower[0], ( y * radius ) + center_lower[1] ) for x, y in edgestrip_verticies_lower]
    # pygame.draw.circle(surface, "red", edgestrip_verticies[0], 3)

    led_positions = [get_interpolated_points(edgestrip_verticies_lower[0], edgestrip_verticies_lower[1], 42)]
    led_positions.append(get_interpolated_points(edgestrip_verticies_lower[1], edgestrip_verticies_lower[2], 42))
    
    edgestrip_verticies_upper_0 = [ (-s1, c1), (-s2, -c2), (s2, -c2) ]
    edgestrip_verticies_upper_0 = [ ( ( x * radius ) + center_upper[0], ( y * radius ) + center_upper[1] ) for x, y in edgestrip_verticies_upper_0]
    # pygame.draw.circle(surface, "red", edgestrip_verticies_upper_0[2], 3)

    led_positions.append(get_interpolated_points(edgestrip_verticies_upper_0[0], edgestrip_verticies_upper_0[1], 42))
    led_positions.append(get_interpolated_points(edgestrip_verticies_upper_0[1], edgestrip_verticies_upper_0[2], 42))

    edgestrip_verticies_upper_1 = [ (0, 1), (s1, c1) ]
    edgestrip_verticies_upper_1 = [ ( ( x * radius ) + center_upper[0], ( y * radius ) + center_upper[1] ) for x, y in edgestrip_verticies_upper_1]
    # pygame.draw.circle(surface, "red", edgestrip_verticies_upper_1[1], 3)

    led_positions.append(get_interpolated_points(edgestrip_verticies_upper_1[0], edgestrip_verticies_upper_1[1], 42))

    # pygame.draw.lines(surface, "red", False, edgestrip_verticies_lower + edgestrip_verticies_upper_0)
    # pygame.draw.lines(surface, "red", False, edgestrip_verticies_upper_1)

    for edge_idx, edge in enumerate(led_positions):

        # print(f"displaying edge {edge_idx} with {len(edge)} LEDs")

        for idx, led in enumerate(edge):
            
            # print(edge_idx)
            # print(idx)
            # print((edge_idx * 42) + idx)
            color = colors[ (edge_idx * 42) + idx ]

            pygame.draw.circle(surface, color, led, 1)

    return led_positions

def get_interpolated_points(start_point, end_point, num_points):
    # Calculate the step size for each dimension
    step_size = [(end - start) / (num_points + 1) for start, end in zip(start_point, end_point)]

    # Initialize the list to store the interpolated points
    interpolated_points = [start_point]

    # Calculate the intermediate points
    for i in range(num_points - 1):
        interpolated_point = [start + step * i for start, step in zip(start_point, step_size)]
        interpolated_points.append(interpolated_point)

    return interpolated_points

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return list(itertools.zip_longest(fillvalue=fillvalue, *args))
