import cv2
import math
import pygame
import itertools
from stupidArtnet import StupidArtnet

PACKET_SIZE = 510

# Color defints
COLOR_LOWLIGHT = (50, 50, 50)
COLOR_BLACK = (0, 0, 0)

STRIP_LENS = [29, 53, 77, 89, 95, 101, 107, 113, 29, 53, 77, 89, 95, 101, 107, 113]

def create_artnet_pentagon_senders(universes, target_ips, fps):
    pentagon_senders = []

    # See StupidArtnet()
    EVEN_PACKET_SIZE = True
    BROADCAST = True
    
    for universe in universes:

        ip_address = target_ips[0] if universe < 64 else target_ips[1]

        pentagon_senders.append(StupidArtnet(ip_address, universe, PACKET_SIZE, fps, EVEN_PACKET_SIZE, BROADCAST))
        pentagon_senders[universe].start()

    return pentagon_senders

def create_artnet_edge_senders(universes, target_ips, fps):
    edge_senders = []
   
    # See StupidArtnet()
    EVEN_PACKET_SIZE = True
    BROADCAST = True
    ip_address = target_ips[1]

    for universe in universes:
        sender = StupidArtnet(ip_address, universe, PACKET_SIZE, fps, EVEN_PACKET_SIZE, BROADCAST)
        edge_senders.append(sender)
        sender.start()
    return edge_senders

def load_video_file(filename):
    # Open video file
    cap = cv2.VideoCapture(filename)

    # video_fps = cap.get(cv2.CAP_PROP_FPS),
    # total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # print(f"Frames Per second: {video_fps } \nTotal Frames: {total_frames} \n Height: {height} \nWidth: {width}")

    return cap

def led_to_packet(led_data, universe, start_universe=0):
    start = (universe * 170) - (start_universe * 170)
    end = start + 170
    leds = led_data[start:end]
    return [i for sub in leds for i in sub]

def send_dmx(led_data, senders, dmx_universes):
    for universe in dmx_universes:
        # print(f"Sending universe {universe}")
        start_universe = dmx_universes[0]
        packet = led_to_packet(led_data, universe, start_universe)
        # print(packet)
        # Pad out the last packet
        if len(packet) < PACKET_SIZE:
            packet += [ 0 for _ in range(PACKET_SIZE - len(packet))]

        senders[universe - dmx_universes[0]].set(packet)
        # senders[universe - dmx_universes[0]].show()

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

    edgestrip_verticies_upper_1 = [ (s1, c1), (0, 1) ]
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

def normalize_leds(led_positions, output_filename):
    # print(led_positions)
    print(len(led_positions))
    # Write out the normalized positions of each LED
    max_x = max(p[0] for p in led_positions)
    max_y = max(p[1] for p in led_positions)
    min_x = min(p[0] for p in led_positions)
    min_y = min(p[1] for p in led_positions)

    normalized = [ ( led[0] / max_x, led[1] / max_y ) for led in led_positions ]
    import json
    with open(output_filename, "w") as outfile:
        json.dump(normalized, outfile, indent=2)

def uv_to_pixel(uv_point, w, h):
    x = round((uv_point[0] * (w - 10)) + 5)
    y = round((uv_point[1] * (h - 10)) + 5)
    return (y, x)

def project_cylinder(points, width, height, frame):
    uv_coords = pixels_to_uv_cylinder(points)

    max_u = max([p[0] for p in uv_coords])
    max_v = max([p[1] for p in uv_coords])
    min_u = min([p[0] for p in uv_coords])
    min_v = min([p[1] for p in uv_coords])

    pixels = [uv_to_pixel(p, width, height) for p in uv_coords]
    # pixels = [uv_to_pixel(p, 360, 160) for p in uv_coords]

    # OpenCV uses BGR :( pixel order must be reversed
    led_data = tuple([frame[p][::-1].tolist() for p in pixels])

    return led_data


def project_straight(points, width, height, frame):
    # Sample pixels directly from frame (no projection)
    pixels = [uv_to_pixel(p, width, height) for p in points]
    
    # OpenCV uses BGR :( pixel order must be reversed
    led_data = tuple([frame[p][::-1].tolist() for p in pixels])
    return led_data

def pixels_to_uv_cylinder(points):
    zmax = max([p[2] for p in points])
    zmin = min([p[2] for p in points])

    output = []
    for point in points:
        x, y, z = point[0], point[1], point[2]

        xc = x / (math.sqrt(x**2 + y**2))
        yc = y / (math.sqrt(x**2 + y**2))
        zc = z

        theta = math.atan2(yc, xc)

        theta_n = 2 * (theta / (math.pi * 2))
        z_n = 1 - (z - zmin) / (zmax - zmin)

        if theta_n <= 0:
            coord_uv = (theta_n + 1, z_n)
        else:
            coord_uv = (1 - theta_n, z_n)

        output.append(coord_uv)
    return output