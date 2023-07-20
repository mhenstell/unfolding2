import cv2
import json
import random
import itertools
import time
import sys
import math
from stupidArtnet import StupidArtnet, StupidArtnetServer

# Defines
PANELS = range(10)
DMX_UNIVERSES = range(0, len(PANELS) * 8)

# LED defines
LEDS_PER_PANEL = 1328
LEDS_PER_HALF = LEDS_PER_PANEL // 2
CHANNELS_PER_HALF = LEDS_PER_HALF * 3
CHANNELS_PER_10_FACES = LEDS_PER_PANEL * 10 * 3

# Advatek setup
target_ip = '255.255.255.255'
packet_size = 510

senders = []
for universe in DMX_UNIVERSES:
    senders.append(StupidArtnet(target_ip, universe, packet_size, 30, True, True))
    senders[universe].start()

led_data = [ (0, 0, 0) for _ in range(CHANNELS_PER_10_FACES)]

# # Load pixel locations
# with open("leds_2d_normalied.json", "r") as infile:
#     led_pos_2d_norm = json.load(infile)

# # with open("led_3d_normalized.json", "r") as infile:
#     # led_pos_3d_norm = json.load(infile)

# with open("led_3d_unnormalized.json", "r") as infile:
#     led_pos_3d_unnorm = json.load(infile)["panels"]

with open("2d_norm_3d_unnorm_zipped.json", "r") as infile:
    led_pos_2d_3d = json.load(infile)

# Open video file
cap = cv2.VideoCapture("fire.mp4")

video_fps = cap.get(cv2.CAP_PROP_FPS),
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
print(f"Frames Per second: {video_fps } \nTotal Frames: {total_frames} \n Height: {height} \nWidth: {width}")

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def led_to_packet(led_data, universe):
    start = universe * 170
    end = start + 170
    leds = led_data[start:end]
    return [i for sub in leds for i in sub]

def uv_to_pixel(uv_point, w, h):
    x = round((uv_point[0] * (w - 10)) + 5)
    y = round((uv_point[1] * (h - 10)) + 5)
    return (y, x)

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

def project_cylinder(points):
    uv_coords = pixels_to_uv_cylinder(points_3d)

    max_u = max([p[0] for p in uv_coords])
    max_v = max([p[1] for p in uv_coords])
    min_u = min([p[0] for p in uv_coords])
    min_v = min([p[1] for p in uv_coords])

    pixels = [uv_to_pixel(p, width, height) for p in uv_coords]
    # pixels = [uv_to_pixel(p, 360, 160) for p in uv_coords]

    # OpenCV uses BGR :( pixel order must be reversed
    led_data = tuple([frame[p][::-1].tolist() for p in pixels])

    return led_data

def project_straight(points):
    # Sample pixels directly from frame (no projection)
    pixels = [uv_to_pixel(p) for p in points]
    
    # OpenCV uses BGR :( pixel order must be reversed
    led_data = tuple([frame[p][::-1].tolist() for p in pixels])
    return led_data

while (cap.isOpened()):

    ret, frame = cap.read()

    if ret == True:
        cv2.imshow('Frame', frame)

        # Random LED pattern (red on bottom, green on top)
        # for panel in range(0, len(PANELS), 2):
        #     led_data[panel * LEDS_PER_PANEL : (panel * LEDS_PER_PANEL) + LEDS_PER_PANEL] = [ (random.randint(0, 255), 0, 0) for _ in range(LEDS_PER_PANEL)]
        #     led_data[(panel + 1) * LEDS_PER_PANEL : ((panel + 1) * LEDS_PER_PANEL) + LEDS_PER_PANEL] = [ (0, random.randint(0, 255), 0) for _ in range(LEDS_PER_PANEL)]


        # points_2d = [point[0] for point in led_pos_2d_3d]
        # led_data = project_straight(points_2d)

        points_3d = [point[1] for point in led_pos_2d_3d]
        led_data = project_cylinder(points_3d)

        for universe in DMX_UNIVERSES:
            # print(f"Sending universe {universe}")
            packet = led_to_packet(led_data, universe)
            
            # Pad out the last packet
            if len(packet) != packet_size:
                packet += [ 0 for _ in range(packet_size - len(packet))]

            senders[universe].set(packet)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
          break
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


cap.release()
cv2.destroyAllWindows()