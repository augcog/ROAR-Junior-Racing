import pygame

from typing import Optional, Tuple
import logging
import asyncio

try:
    from ROAR_Junior.keyboard_control import JuniorKeyboardControl
except:
    from keyboard_control import JuniorKeyboardControl

from utilities import VehicleState


class Game:
    def __init__(self, vehicle_state: VehicleState, debug_level=logging.DEBUG):
        self.logger = logging.getLogger("Game")
        self.logger.setLevel(level=debug_level)
        self.vehicle_state = vehicle_state
        self.display: Optional[pygame.display] = None
        self.controller = JuniorKeyboardControl(
            log_level=logging.INFO
        )
        self.clock: Optional[pygame.time.Clock] = None
        self.setup()
        self.should_continue = True

    def setup(self):
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
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

        self.should_continue, new_kb_control = self.update_pygame()
        self.vehicle_state.motor_left, self.vehicle_state.motor_right, self.vehicle_state.motor_left_mode, \
        self.vehicle_state.motor_right_mode = new_kb_control
        self.execute_user_action()
        self.debug_state()
        return self.should_continue

    def debug_state(self):
        self.logger.info(self.vehicle_state)

    def update_pygame(self) -> Tuple[bool, Tuple[int, int, bool, bool]]:
        return self.controller.parse_events(clock=self.clock)

    def execute_user_action(self):
        self.logger.info("Executing User Action")
        # TODO your code here for autonomous driving.
