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
HIGHLIGHT_COLOR = pygame.color.Color("red")
GAME_TIME = 60


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.beep_sound = pygame.mixer.Sound('audio\\beep.ogg')
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1,
                                                self._infoObject.current_h >> 1),
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect Game Framework Test")

        self.finished = False
        self._clock = pygame.time.Clock()
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color |
                                                       PyKinectV2.FrameSourceTypes_Body)
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width,
                                              self._kinect.color_frame_desc.Height), 0, 32)
        self._bodies = None

        self.score = -1

        self.vocab_dict = {"beach":"playa", "desert":"desierto", "forest":"bosque",
                           "jungle":"selva", "hill":"loma", "island":"isla",
                           "lake":"lago", "mountain":"montaña", "ocean":"oceano",
                           "river":"rio", "valley":"valle", "basin":"cuenca",
                           "volcano":"volcano", "waterfall":"cascada", "creek":"arroyo"}

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

    def draw_ind_point(self, joints, jointPoints, color, highlight_color, rect0, rect1, rect2, joint0, words, selected_word_esp):
        joint0State = joints[joint0].TrackingState;
        
        if (joint0State == PyKinectV2.TrackingState_NotTracked or
            joint0State == PyKinectV2.TrackingState_Inferred):
            return

        center = (int(jointPoints[joint0].x), int(jointPoints[joint0].y))

        if ((rect0.collidepoint(center) and self.vocab_dict[words[0]] == selected_word_esp) or
            (rect1.collidepoint(center) and self.vocab_dict[words[1]] == selected_word_esp) or
            (rect2.collidepoint(center) and self.vocab_dict[words[2]] == selected_word_esp)):
            self.beep_sound.play()
            self.run()
        elif rect0.collidepoint(center) or rect1.collidepoint(center) or rect2.collidepoint(center):
            try:
                pygame.draw.circle(self._frame_surface, highlight_color, center, 20, 0)
            except: # need to catch it due to possible invalid positions (with inf)
                pass
        else:
            try:
                pygame.draw.circle(self._frame_surface, color, center, 20, 0)
            except:
                pass

    def update_screen(self, joints, jointPoints, color, highlight_color, words, selected_word_esp):
        self._frame_surface.fill((255, 255, 0))# blank screen before drawing points

        self.message_display(selected_word_esp, (300, 800), 1)
        rect0 = self.message_display(words[0], (300, 300), 1)
        rect1 = self.message_display(words[1], (self._frame_surface.get_width() / 2, 100), 1)
        rect2 = self.message_display(words[2], (self._frame_surface.get_width() - 300, 300), 1)
        self.message_display(str(self.score), (self._frame_surface.get_width() / 2, 800), 1)

        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_Head, words, selected_word_esp);
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristRight, words, selected_word_esp);
        # may change PyKinectV2.JointType_WristRight to PyKinectV2.JointType_ElbowRight
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristLeft, words, selected_word_esp);     

    def run(self):
        self.score += 1
        print(self.score)
        start_ticks = pygame.time.get_ticks()
        words = random.sample(list(self.vocab_dict), 3)
        selected_word_esp = self.vocab_dict[words[0]]
        random.shuffle(words)
        while not self.finished:
            seconds = (pygame.time.get_ticks() - start_ticks)/1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True

            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 
                    
                    joints = body.joints 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.update_screen(joints, joint_points, TRACKING_COLOR, HIGHLIGHT_COLOR, words, selected_word_esp)

            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface,
                                                     (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            self._clock.tick(60)

        self._kinect.close()
        pygame.quit()


__main__ = "Kinect v2 Game Framework Test"
game = BodyGameRuntime();
game.run();
