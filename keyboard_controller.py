from ROAR_Junior_Racing.configurations.junior_config import JuniorConfig
import pygame
from typing import Tuple
from ROAR.utilities_module.vehicle_models import VehicleControl
from pygame import *


class JuniorKeyboardController:
    def __init__(self, config: JuniorConfig):
        self.config = config
        self._throttle_increment = config.throttle_increment
        self._steering_increment = config.steering_increment
        self.throttle = 0
        self.steering = 0
        self.last_switch_press_time = time.get_ticks()

    def parse_events(self, clock: pygame.time.Clock) -> Tuple[bool, VehicleControl, bool]:
        events = pygame.event.get()
        key_pressed = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT or key_pressed[K_q] or key_pressed[K_ESCAPE]:
                return False, VehicleControl(), False

        self.throttle, self.steering = self._parse_vehicle_keys(key_pressed)
        is_switch_auto_pressed = False

        if key_pressed[K_m] and time.get_ticks() - self.last_switch_press_time > 100:
            is_switch_auto_pressed = True
            self.last_switch_press_time = time.get_ticks()

        control = VehicleControl(throttle=self.throttle, steering=self.steering)
        return True, control, is_switch_auto_pressed

    def _parse_vehicle_keys(self, keys) -> Tuple[float, float]:
        """
        Parse a single key press and set the throttle & steering
        Args:
            keys: array of keys pressed. If pressed keys[PRESSED] = 1
        Returns:
            None
        """
        if keys[K_w]:
            self.throttle = min(self.throttle + self._throttle_increment, 1)

        elif keys[K_s]:
            self.throttle = max(self.throttle - self._throttle_increment, -1)
        else:
            self.throttle = 0

        if keys[K_a]:
            self.steering = max(self.steering - self._steering_increment, -1)
        elif keys[K_d]:
            self.steering = min(self.steering + self._steering_increment, 1)
        else:
            self.steering = 0

        return round(self.throttle, 5), round(self.steering, 5)
