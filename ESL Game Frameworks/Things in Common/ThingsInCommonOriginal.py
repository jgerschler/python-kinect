# for python 3
# You'll need to customize this according to your needs. Proper orientation of
# the kinect is vital; if participants are able to maintain their head or wrists
# continuously inside the word rects, they will repeatedly trigger the collision
# detection
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import pygame
import random


TRACKING_COLOR = pygame.color.Color("purple")
HIGHLIGHT_COLOR = pygame.color.Color("red")
BG_COLOR = pygame.color.Color("white")
GAME_TIME = 60# seconds


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.beep_sound = pygame.mixer.Sound('audio\\beep.ogg')
        self.buzz_sound = pygame.mixer.Sound('audio\\buzz.ogg')
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

        self.score = 0

        self.sentence_dict = {"""I don't like fish.""":["""I don't either.""", """Me neither."""],
                         """I don't know how to swim.""":["""I don't either.""", """Me neither."""],
                         """I don't like potatoes.""":["""I don't either.""", """Me neither."""],
                         """I don't eat donuts at night.""":["""I don't either.""", """Me neither."""],
                         """I don't watch scary movies.""":["""I don't either.""", """Me neither."""],
                         """I don't yell when I get angry.""":["""I don't either.""", """Me neither."""],
                         """I can't ride a bicycle.""":["""I can't either.""", """Me neither."""],
                         """I can't swim.""":["""I can't either.""", """Me neither."""],
                         """I can't drive a car.""":["""I can't either.""", """Me neither."""],
                         """I can't do a pushup.""":["""I can't either.""", """Me neither."""],
                         """I can't run faster than a bus.""":["""I can't either.""", """Me neither."""],
                         """I can't flap my arms and fly.""":["""I can't either.""", """Me neither."""],
                         """I'm not fat.""":["""I'm not either.""", """Me neither."""],
                         """I'm not skinny.""":["""I'm not either.""", """Me neither."""],
                         """I'm not an angry person.""":["""I'm not either.""", """Me neither."""],
                         """I'm not hungry.""":["""I'm not either.""", """Me neither."""],
                         """I'm not happy.""":["""I'm not either.""", """Me neither."""],
                         """I'm not a purple hippopotamus.""":["""I'm not either.""", """Me neither."""],
                         """I like papayas.""":["""I do too.""", """Me too."""],
                         """I know how to drive.""":["""I do too.""", """Me too."""],
                         """I know how to swim.""":["""I do too.""", """Me too."""],
                         """I like oranges.""":["""I do too.""", """Me too."""],
                         """I eat cake on Fridays.""":["""I do too.""", """Me too."""],
                         """I love comedies.""":["""I do too.""", """Me too."""],
                         """I can eat 12 hamburgers at once.""":["""I can too.""", """Me too."""],
                         """I can fly an airplane.""":["""I can too.""", """Me too."""],
                         """I can write quickly.""":["""I can too.""", """Me too."""],
                         """I can run faster than a snail.""":["""I can too.""", """Me too."""],
                         """I can calculate faster than a calculator.""":["""I can too.""", """Me too."""],
                         """I can swim with my eyes open.""":["""I can too.""", """Me too."""],
                         """I'm angry.""":["""I am too.""", """Me too."""],
                         """I'm hungry.""":["""I am too.""", """Me too."""],
                         """I'm sad.""":["""I am too.""", """Me too."""],
                         """I'm busy with work.""":["""I am too.""", """Me too."""],
                         """I'm studying right now.""":["""I am too.""", """Me too."""],
                         """I'm at school at the moment.""":["""I am too.""", """Me too."""]}

        self.reply_list = ["""I don't either.""", """Me neither.""", """I can't either.""",
                      """I'm not either.""", """I do too.""", """Me too.""", """I can too.""",
                      """I am too.""", """I do either.""", """I can either.""", """I am either.""",
                      """I do neither.""", """I can neither.""", """I am neither.""",
                           """I am not too.""", """I don't too.""", """I can't too."""]

        self._frame_surface.fill((255, 255, 255))

    def text_objects(self, text, font):
        text_surface = font.render(text, True, (0, 0, 0))
        return text_surface, text_surface.get_rect()

    def message_display(self, text, loc_tuple, loc_int):
        # loc_int: 1 center, 2 top left, 3 bottom left, 4 bottom right, 5 top right
        text_surf, text_rect = self.text_objects(text, pygame.font.Font('arial.ttf', 48))
        loc_dict = {1:'text_rect.center', 2:'text_rect.topleft', 3:'text_rect.bottomleft',
                    4:'text_rect.bottomright', 5:'text_rect.topright'}
        exec(loc_dict[loc_int] + ' = loc_tuple')
        self._frame_surface.blit(text_surf, text_rect)
        return text_rect 

    def draw_ind_point(self, joints, jointPoints, color, highlight_color, rect0, rect1, rect2, joint0):
        joint0State = joints[joint0].TrackingState;
        
        if (joint0State == PyKinectV2.TrackingState_NotTracked or
            joint0State == PyKinectV2.TrackingState_Inferred):
            return

        center = (int(jointPoints[joint0].x), int(jointPoints[joint0].y))

        if ((rect0.collidepoint(center) and self.filler_replies[0] == self.selected_answer[0]) or
            (rect1.collidepoint(center) and self.filler_replies[1] == self.selected_answer[0]) or
            (rect2.collidepoint(center) and self.filler_replies[2] == self.selected_answer[0])):
            self.score += 1
            self.beep_sound.play()
            pygame.time.delay(500)
            self.new_round()
        elif rect0.collidepoint(center) or rect1.collidepoint(center) or rect2.collidepoint(center):
            try:
                pygame.draw.circle(self._frame_surface, highlight_color, center, 20, 0)
                self.buzz_sound.play()               
            except: # need to catch it due to possible invalid positions (with inf)
                pass
        else:
            try:
                pygame.draw.circle(self._frame_surface, color, center, 20, 0)
            except:
                pass

    def update_screen(self, joints, jointPoints, color, highlight_color, seconds):
        self._frame_surface.fill(BG_COLOR)# blank screen before drawing points

        self.message_display(self.selected_sentence, (300, 900), 2)
        rect0 = self.message_display(self.filler_replies[0], (300, 300), 1)
        rect1 = self.message_display(self.filler_replies[1], (self._frame_surface.get_width() / 2, 100), 1)
        rect2 = self.message_display(self.filler_replies[2], (self._frame_surface.get_width() - 300, 300), 1)
        self.message_display(str(self.score), (self._frame_surface.get_width() / 2, 800), 1)
        self.message_display(str(seconds), (self._frame_surface.get_width() - 300, 800), 1)

        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_Head)
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristRight)
        # may change PyKinectV2.JointType_WristRight to PyKinectV2.JointType_ElbowRight
        self.draw_ind_point(joints, jointPoints, color, highlight_color, rect0,
                            rect1, rect2, PyKinectV2.JointType_WristLeft)

    def end_game(self):
        self._frame_surface.fill(BG_COLOR)
        self.message_display("Score: {}".format(self.score), (self._frame_surface.get_width() / 2, self._frame_surface.get_height() / 2), 1)
        h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
        target_height = int(h_to_w * self._screen.get_width())
        surface_to_draw = pygame.transform.scale(self._frame_surface,
                                                     (self._screen.get_width(), target_height));
        self._screen.blit(surface_to_draw, (0,0))
        surface_to_draw = None
        pygame.display.update()
        pygame.time.delay(3000)
        self.run()

    def new_round(self):
        self.selected_sentence = random.choice(list(self.sentence_dict.keys()))
        self.selected_answer = random.sample(self.sentence_dict[self.selected_sentence], 1)
        self.filler_replies = random.sample(self.reply_list, 2)
        while ((self.sentence_dict[self.selected_sentence][0] in self.filler_replies) or
               (self.sentence_dict[self.selected_sentence][1] in self.filler_replies)):
            self.filler_replies = random.sample(self.reply_list, 2)
        self.filler_replies += self.selected_answer
        random.shuffle(self.filler_replies)

        print(self.filler_replies)
        print(self.selected_answer)
       
        pygame.time.delay(500)
        
        while not self.finished:
            seconds = GAME_TIME - int((pygame.time.get_ticks() - self.start_ticks)/1000)
            if seconds <= 0:
                self.end_game()
                
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
                    self.update_screen(joints, joint_points, TRACKING_COLOR, HIGHLIGHT_COLOR, seconds)

            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface,
                                                     (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            self._clock.tick(60)
            
        self.end_game()

    def run(self):
        self.score = 0
        while not self.finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    self.start_ticks = pygame.time.get_ticks()
                    self.new_round()

        self._kinect.close()
        pygame.quit()

if __name__ == "__main__":
    game = BodyGameRuntime()
    game.run()
