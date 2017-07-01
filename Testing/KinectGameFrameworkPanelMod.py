from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys

if sys.hexversion >= 0x03000000:# check python version
    import _thread as thread
else:
    import thread


TRACKING_COLOR = pygame.color.Color("purple")


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1), 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect Game Framework Test")

        self._done = False
        self._clock = pygame.time.Clock()
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None

        self._frame_surface.fill((255, 255, 255))

    def draw_ind_point(self, joints, jointPoints, color, joint0):
        joint0State = joints[joint0].TrackingState;

        if joint0State == PyKinectV2.TrackingState_NotTracked or joint0State == PyKinectV2.TrackingState_Inferred:
            return

        center = (int(jointPoints[joint0].x), int(jointPoints[joint0].y))

        try:
            pygame.draw.circle(self._frame_surface, color, center, 5, 0)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_all_points(self, joints, jointPoints, color):
        self._frame_surface.fill((255, 255, 0))# blank screen before drawing points
        self.draw_ind_point(joints, jointPoints, color, PyKinectV2.JointType_Head);
        self.draw_ind_point(joints, jointPoints, color, PyKinectV2.JointType_WristRight); # may change to PyKinectV2.JointType_ElbowRight
        self.draw_ind_point(joints, jointPoints, color, PyKinectV2.JointType_WristLeft);

    def run(self):
        while not self._done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._done = True

            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            if self._bodies is not None: 
                body = self._bodies.bodies[0]
                if not body.is_tracked: 
                    continue 
                
                joints = body.joints 
                joint_points = self._kinect.body_joints_to_color_space(joints)
                self.draw_all_points(joints, joint_points, TRACKING_COLOR)

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


__main__ = "Kinect v2 Game Framework Test"
game = BodyGameRuntime();
game.run();
