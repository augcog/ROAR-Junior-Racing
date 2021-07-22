import pygame
from pygame.locals import *
import logging
from typing import Tuple


class JuniorKeyboardControl(object):
    def __init__(self, left_motor_increment=10, right_motor_increment=10, log_level=logging.DEBUG):
        self.logger = logging.getLogger("JuniorKeyboard")
        self.logger.setLevel(log_level)
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

        self._parse_control_keys(key_pressed)
        return True, (self.left_motor, self.right_motor, self.left_motor_mode, self.right_motor_mode)

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
