import argparse
import cv2
import json

from util import project_cylinder, project_straight, load_video_file
from util import create_artnet_pentagon_senders, create_artnet_edge_senders, send_dmx

# Defines
DMX_UNIVERSES = range(0, 90)
EDGE_START_UNIVERSE = 80

# Output setup
# Uncomment to use local Simulator
target_ips = ['127.0.0.1', '127.0.0.1']

# Uncomment to send data to two Advateks
# may throw errors if both are not connected
# target_ips = ['192.168.0.50', '192.168.0.51']

class MovieAnimation:
    def __init__(self, path, display_preview=False):
        self.path = path
        self.display_preview = display_preview

         # Load pixel locations
        with open("2d_norm_3d_unnorm_zipped.json", "r") as infile:
            self.pentagon_led_pos = json.load(infile)

        with open("edge_positions_normalized.json", "r") as infile:
            self.edge_led_pos = json.load(infile)

         # Load movie frames
        self.cap = load_video_file(self.path)
        self.width, self.height = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.edge_led_data = []

    def get_frame(self, ticks=None):
        """ Reads the video file and returns the next frame of animation.
            Returns both pentagon and edge data """

        # Read next video frame
        ret, frame = self.cap.read()

        if ret == True:

            if self.display_preview:
                cv2.imshow('Frame', frame)
            
            # Generate colors for the pentagonal faces by running
            # the 3D points through cylindrical projection
            points_3d = [point[1] for point in self.pentagon_led_pos]
            pentagon_led_data = project_cylinder(points_3d, self.width, self.height, frame)
            
            # Generate colors for the edge strips by straight 2D projection
            # super dumb and needs work
            
            self.edge_led_data = project_straight(self.edge_led_pos, self.width, self.height, frame)

            # Needed to prevent python from crashing for some reason
            cv2.waitKey(25)

            return pentagon_led_data
        else:
            # Restart movie clip
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return []

    def get_edge_frame(self, ticks=None):
        return self.edge_led_data

    def stop(self):
        self.cap.release()
        if self.display_preview:
            cv2.destroyAllWindows()


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

    movie = MovieAnimation(args.filename, display_preview=args.preview)
   
    while True:
        pentagon_data = movie.get_frame()
        edge_data = movie.get_edge_frame()
        
        if len(pentagon_data):
            send_dmx(pentagon_data, pentagon_senders, DMX_UNIVERSES[:EDGE_START_UNIVERSE])
        if len(edge_data):
            send_dmx(edge_data, edge_senders, DMX_UNIVERSES[EDGE_START_UNIVERSE:])
        