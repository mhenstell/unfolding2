import cv2
import json
import random
import itertools
import time
import sys
import math
from stupidArtnet import StupidArtnet, StupidArtnetServer

from util import project_cylinder, load_video_file
from util import uv_to_pixel, send_dmx

# Defines
PANELS = range(10)
DMX_UNIVERSES = range(0, len(PANELS) * 8)
EDGE_DMX_UNIVERSES = range(80, 90)

# LED defines
LEDS_PER_PANEL = 1328
LEDS_PER_HALF = LEDS_PER_PANEL // 2
CHANNELS_PER_HALF = LEDS_PER_HALF * 3
CHANNELS_PER_10_FACES = LEDS_PER_PANEL * 10 * 3

# Advatek setup
# Simulator
target_ip = '127.0.0.1'
target_ip2 = '127.0.0.1'

# Actual advatek
# target_ip = '192.168.0.50'
# target_ip2 = '192.168.0.51'

packet_size = 510
DMX_FPS = 15


def project_straight(points, frame, width, height):
    # Sample pixels directly from frame (no projection)
    pixels = [uv_to_pixel(p, width, height) for p in points]
    
    # OpenCV uses BGR :( pixel order must be reversed
    led_data = tuple([frame[p][::-1].tolist() for p in pixels])
    return led_data


if __name__ == "__main__":

    # Start pentagonal face DMX senders
    senders = []
    for universe in DMX_UNIVERSES:
        if universe < 64:
            senders.append(StupidArtnet(target_ip, universe, packet_size, DMX_FPS, True, True))
        else:
            senders.append(StupidArtnet(target_ip2, universe, packet_size, DMX_FPS, True, True))
        senders[universe].start()

    # Start edge strip DMX senders
    # the reason these are separate from the other DMX senders is very important
    # and I would be happy to tell you just let me answer this call real quick
    edge_senders = []
    for universe in EDGE_DMX_UNIVERSES:
        edge_senders.append(StupidArtnet(target_ip, universe, packet_size, 30, True, True))
        edge_senders[universe - EDGE_DMX_UNIVERSES[0]].start()

    # Load pixel locations
    with open("2d_norm_3d_unnorm_zipped.json", "r") as infile:
        led_pos_2d_3d = json.load(infile)

    with open("edge_positions_normalized.json", "r") as infile:
        edge_points_2d = json.load(infile)
    
    # Load movie frames
    cap = load_video_file("fire.mp4")
    width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    while (cap.isOpened()):

        ret, frame = cap.read()

        if ret == True:
            cv2.imshow('Frame', frame)

            # Generate colors for the pentagonal faces by running
            # the 3D points through cylindrical projection
            points_3d = [point[1] for point in led_pos_2d_3d]
            pentagon_led_data = project_cylinder(points_3d, width, height, frame)
            send_dmx(pentagon_led_data, senders, DMX_UNIVERSES)

            # Generate colors for the edge strips by straight 2D projection
            # super dumb and needs work
            edge_led_data = project_straight(edge_points_2d, frame, width, height)

            #Send the DMX data
            send_dmx(edge_led_data, edge_senders, EDGE_DMX_UNIVERSES)


            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
              break
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


    cap.release()
    cv2.destroyAllWindows()