import pygame

from typing import Optional, Tuple
import logging
import urllib.request
import numpy as np
import cv2

from manual_control import JuniorManualControl

from utilities import VehicleState


class Game:
    def __init__(self, vehicle_state: VehicleState, cam_ip_addr: Optional[str] = None,
                 cam_resolution="cam-hi", debug_level=logging.DEBUG):
        """
        Initialize a Game object

        :param vehicle_state: Vehicle state object
        :param cam_ip_addr: Ip Address of the camera
        :param cam_resolution: Camera Resolution. Options: cam.bmp, cam-lo.jpg, cam-hi.jpg, cam.mjpeg
        :param debug_level: Debug Level
        """
        self.logger = logging.getLogger("Game")
        self.display_dimension = (800, 600)
        self.logger.setLevel(level=debug_level)
        self.vehicle_state = vehicle_state
        self.display: Optional[pygame.display] = None
        self.controller = JuniorManualControl(
            log_level=logging.INFO
        )
        self.clock: Optional[pygame.time.Clock] = None
        self.setup()
        self.should_continue = True
        self.cam_ip_addr = cam_ip_addr
        self.cam_resolution = cam_resolution

    def setup(self):
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode(self.display_dimension, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

    def run_step(self):
        """
        Start the game loop.
        - if should_continue
            - if BLE is connected
                - Update Pygame
                - Update data from BLE module
                - Execute user action
        - Wait for self.rate for the next execution of this function

        :return:
            None
        """
        try:
            self.clock.tick(40)
            self.should_continue, new_kb_control = self.update_pygame()
            self.vehicle_state.motor_left, self.vehicle_state.motor_right, self.vehicle_state.motor_left_mode, \
            self.vehicle_state.motor_right_mode = new_kb_control
            # self.execute_user_action()
            self.debug_state()
            # print(self.vehicle_state.motor_left, self.vehicle_state.motor_right)
            return self.should_continue
        except Exception as e:
            self.logger.error(f"Something bad happend during game stepping: {e}")
            return False

    def debug_state(self):
        self.logger.info(self.vehicle_state)

    def update_pygame(self) -> Tuple[bool, Tuple[int, int, bool, bool]]:
        if self.cam_ip_addr is not None:
            url = f'http://{self.cam_ip_addr}/{self.cam_resolution}.jpg'
            imgResp = urllib.request.urlopen(url)
            img = cv2.resize(cv2.imdecode(np.array(bytearray(imgResp.read()), dtype=np.uint8), -1),
                             dsize=self.display_dimension)[..., ::-1]
            surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
            self.display.blit(surface, (0, 0))
            pygame.display.flip()

        return self.controller.parse_events(clock=self.clock)

    def execute_user_action(self):
        self.logger.info("Executing User Action")
        # TODO your code here for autonomous driving.
