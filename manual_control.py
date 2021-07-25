import pygame
from pygame.locals import *
import logging
from typing import Tuple, Optional
import numpy as np
from utilities import VehicleState
from utilities import LeftModeEnum, RightModeEnum


class JuniorManualControl(object):
    def __init__(self, left_motor_increment=10, right_motor_increment=10, log_level=logging.DEBUG):
        self.logger = logging.getLogger("JuniorKeyboard")
        self.logger.setLevel(log_level)
        self.use_joystick = False
        self.joystick: Optional[pygame.joystick.Joystick] = None

        try:
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.logger.info(f"Joystick [{self.joystick.get_name()}] detected, Using Joytick" )
            self.use_joystick = True
        except Exception as e:
            self.logger.info("No joystick detected. Plz use your keyboard instead")

        self._left_motor_increment = left_motor_increment
        self._right_motor_increment = right_motor_increment
        self.left_motor = 0
        self.right_motor = 0
        self.left_motor_mode = True
        self.right_motor_mode = True

    def parse_events(self, clock: pygame.time.Clock) -> Tuple[bool, Tuple[int, int, bool, bool]]:
        """
        Outer layer will call this function on every step.

        Pygame will query whether an event has happened.

        If so, parse the event.

        :param clock: pygame clock
        :return:
            [SHOULD_CONTINUE, [MOTOR_LEFT, MOTOR_RIGHT]
        """
        events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT or key_pressed[K_q] or key_pressed[K_ESCAPE]:
                return False, (self.left_motor, self.right_motor, self.left_motor_mode, self.right_motor_mode)
            elif event.type == pygame.JOYAXISMOTION:
                self.logger.info("Axis motion")
        if self.use_joystick:
            self._parse_joystick()
        else:
            self._parse_control_keys(key_pressed)
        return True, (self.left_motor, self.right_motor, self.left_motor_mode, self.right_motor_mode)

    def _parse_joystick(self):
        self.logger.info("Parsing joystick")
        steering = self.joystick.get_axis(0)
        throttle = -self.joystick.get_axis(1)
        self.right_motor = int(np.interp(abs(throttle), [0, 1], [0, 255]))
        self.left_motor = int(np.interp(abs(throttle), [0, 1], [0, 255]))

        if steering < -0.01:
            # left turn
            self.right_motor_mode = RightModeEnum.forward.value
            self.left_motor_mode = LeftModeEnum.backward.value
        elif steering > 0.01:
            self.right_motor_mode = RightModeEnum.backward.value
            self.left_motor_mode = LeftModeEnum.forward.value

        else:
            if throttle > 0:
                self.right_motor_mode = RightModeEnum.forward.value
                self.left_motor_mode = LeftModeEnum.forward.value
            else:
                self.right_motor_mode = RightModeEnum.backward.value
                self.left_motor_mode = LeftModeEnum.backward.value

    def _parse_control_keys(self, keys):
        """
        Parse keyboard press

        :param keys: List of keys being pressed
        :return:
            none
        """
        if keys[K_UP]:
            self.right_motor = min(self.right_motor + self._right_motor_increment, 255)

        elif keys[K_DOWN]:
            self.right_motor = max(self.right_motor - self._right_motor_increment, 0)

        if keys[K_w]:
            self.left_motor = min(self.left_motor + self._left_motor_increment, 255)

        elif keys[K_s]:
            self.left_motor = max(self.left_motor - self._left_motor_increment, 0)

        if keys[K_a]:
            self.left_motor_mode = True
        elif keys[K_d]:
            self.left_motor_mode = False

        if keys[K_LEFT]:
            self.right_motor_mode = True
        elif keys[K_RIGHT]:
            self.right_motor_mode = False
