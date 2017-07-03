from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys
import random

if sys.hexversion >= 0x03000000:# check python version
    import _thread as thread
else:
    import thread


TRACKING_COLOR = pygame.color.Color("purple")
HIGHLIGHT_COLOR = pygame.color.Color("green")


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1,
                                                self._infoObject.current_h >> 1),
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect Game Framework Test")

        self._done = False
        self._clock = pygame.time.Clock()
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                                       PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width,
                                              self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None

        self.vocab_dict = {"cellphone":"noun", "blue":"adjective", "ameliorate":"verb"}

        self._frame_surface.fill((255, 255, 255))

    def text_objects(self, text, font):
        text_surface = font.render(text, True, (0, 0, 0))
        return text_surface, text_surface.get_rect()

    def message_display(self, text, loc_tuple, loc_int):
        # loc_int: 1 center, 2 top left, 3 bottom left, 4 bottom right, 5 top right
        text_surf, text_rect = self.text_objects(text, pygame.font.Font('arial.ttf', 64))
        loc_dict = {1:'text_rect.center', 2:'text_rect.topleft', 3:'text_rect.bottomleft',
                    4:'text_rect.bottomright', 5:'text_rect.topright'}
        exec(loc_dict[loc_int] + ' = loc_tuple')
        self._frame_surface.blit(text_surf, text_rect)
        return text_rect 

    def draw_ind_point(self, joints, jointPoints, color, highlight_color, rect0, rect1, rect2, joint0, words, pos):
        joint0State = joints[joint0].TrackingState;
        
        if (joint0State == PyKinectV2.TrackingState_NotTracked or
            joint0State == PyKinectV2.TrackingState_Inferred):
            return

        center = (int(jointPoints[joint0].x), int(jointPoints[joint0].y))

        if ((rect0.collidepoint(center) and self.vocab_dict[words[0]] == pos) or
            (rect1.collidepoint(center) and self.vocab_dict[words[1]] == pos) or
            (rect2.collidepoint(center) and self.vocab_dict[words[2]] == pos)):
            try:
                pygame.draw.circle(self._frame_surface, highlight_color, center, 20, 0)
            except: # need to catch it due to possible invalid positions (with inf)
                pass
        else:
            try:
                pygame.draw.circle(self._frame_surface, color, center, 20, 0)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

    def update_screen(self, joints, jointPoints, color, highlight_color, words, pos):
        self._frame_surface.fill((255, 255, 0))# blank screen before drawing points

        self.message_display("Touch a(n) {0}.".format(pos), (300, 800), 1)
        rect0 = self.message_display(words[0], (300, 300), 1)
        rect1 = self.message_display(words[1], (self._frame_surface.get_width() / 2, 300), 1)
        rect2 = self.message_display(words[2], (self._frame_surface.get_width() - 300, 300), 1)

        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_Head, words, pos);
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristRight, words, pos);
        # may change PyKinectV2.JointType_WristRight to PyKinectV2.JointType_ElbowRight
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristLeft, words, pos);     

    def run(self):
        words = random.sample(list(self.vocab_dict), 3)
        pos = self.vocab_dict[words[0]]
        random.shuffle(words)
        while not self._done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._done = True

            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 
                    
                    joints = body.joints 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.update_screen(joints, joint_points, TRACKING_COLOR, HIGHLIGHT_COLOR, words, pos)

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface,
                                                     (self._screen.get_width(), target_height));
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
