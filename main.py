import argparse
import pygame

from rain_effect import MatrixAnimation
from play_movie import MovieAnimation
from util import create_artnet_pentagon_senders, create_artnet_edge_senders, send_dmx

# Output setup
# Uncomment to use local Simulator
target_ips = ['127.0.0.1', '127.0.0.1']

# Uncomment to send data to two Advateks
# may throw errors if both are not connected
# target_ips = ['192.168.0.50', '192.168.0.51']

# Defines
DMX_UNIVERSES = range(0, 90)
EDGE_START_UNIVERSE = 80


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='Unfolding Humanity Video Player',
        description='This program reverse-projects a video file onto the LEDs on Unfolding Humanity')
    parser.add_argument('-f', '--filename', default='fire.mp4', help="Filename of the movie to play")
    parser.add_argument('-p', '--preview', action='store_true', help="Show a 2D preview of the movie")
    parser.add_argument('--fps', default=15, help="Frames Per Second for the DMX output")
    args = parser.parse_args()

    pentagon_senders = create_artnet_pentagon_senders(DMX_UNIVERSES[:EDGE_START_UNIVERSE], target_ips, int(args.fps))
    edge_senders = create_artnet_edge_senders(DMX_UNIVERSES[EDGE_START_UNIVERSE:], target_ips, int(args.fps))



ani_matrix = MatrixAnimation()
ani_fire = MovieAnimation("fire.mp4")

pentagon_animations = [ani_matrix, ani_fire]
edge_animations = [ani_fire]

active_pentagon_animation = 0
active_edge_animation = 0

clock = pygame.time.Clock()

pentagon_data = []
edge_data = []

while True:

    pentagon_data = pentagon_animations[active_pentagon_animation].get_frame()
    edge_data = edge_animations[active_edge_animation].get_edge_frame()

    if len(pentagon_data):
        send_dmx(pentagon_data, pentagon_senders, DMX_UNIVERSES[:EDGE_START_UNIVERSE])
    if len(edge_data):
        send_dmx(edge_data, edge_senders, DMX_UNIVERSES[EDGE_START_UNIVERSE:])
    
    clock.tick(args.fps)
