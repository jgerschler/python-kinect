from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import pygame


TRACKING_COLOR = pygame.color.Color("green")
HIGHLIGHT_COLOR = pygame.color.Color("red")
BG_COLOR = pygame.color.Color("white")


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, 32)

        pygame.display.set_caption("Kinect Base Framework Test")

        self.finished = False
        
        self.clock = pygame.time.Clock()
        
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        
        self.frame_surface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)
        
        self.bodies = None

        self.frame_surface.fill((255, 255, 255))

    def draw_ind_intro_point(self, joints, jointPoints, color, joint0):
        joint0State = joints[joint0].TrackingState;
        
        if (joint0State == PyKinectV2.TrackingState_NotTracked or
            joint0State == PyKinectV2.TrackingState_Inferred):
            return

        center = (int(jointPoints[joint0].x), int(jointPoints[joint0].y))

        try:
            pygame.draw.circle(self.frame_surface, color, center, 20, 0)
        except:
            pass

    def update_intro_screen(self, joints, jointPoints, color):
        self.frame_surface.fill(BG_COLOR)# blank screen before drawing points

        self.draw_ind_intro_point(joints, jointPoints, color, PyKinectV2.JointType_Head)
        self.draw_ind_intro_point(joints, jointPoints, color, PyKinectV2.JointType_WristLeft)
        # may change PyKinectV2.JointType_WristRight to PyKinectV2.JointType_ElbowRight
        self.draw_ind_intro_point(joints, jointPoints, color, PyKinectV2.JointType_WristRight)

    def run(self):
        while not self.finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    # start round here (remove pass and add function ref)
                    self.finished = True

            if self.kinect.has_new_body_frame(): 
                self.bodies = self.kinect.get_last_body_frame()

            if self.bodies is not None:
                for i in range(0, self.kinect.max_body_count):
                    body = self.bodies.bodies[i]
                    if not body.is_tracked: 
                        continue 
                    
                    joints = body.joints 
                    joint_points = self.kinect.body_joints_to_color_space(joints)
                    self.update_intro_screen(joints, joint_points, TRACKING_COLOR)

            self.screen.blit(self.frame_surface, (0,0))
            pygame.display.update()

            self.clock.tick(30)

        self.kinect.close()
        pygame.quit()

if __name__ == "__main__":
    game = BodyGameRuntime()
    game.run()
