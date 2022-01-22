import time
import requests
from ROAR.agent_module.agent import Agent
from ROAR_Junior_Racing.configurations.junior_config import JuniorConfig
from ROAR_Junior_Racing.keyboard_controller import JuniorKeyboardController
import logging
import pygame
from typing import Optional, Tuple
import numpy as np
import cv2
from ROAR.utilities_module.vehicle_models import VehicleControl, Vehicle
from ROAR.utilities_module.data_structures_models import SensorsData, RGBData
import json


class JuniorRunner:
    def __init__(self, agent: Agent, config: JuniorConfig):
        self.agent = agent
        self.is_auto = False
        self.config: JuniorConfig = config
        self.pygame_display_width = self.config.pygame_display_width
        self.pygame_display_height = self.config.pygame_display_height
        self.logger = logging.getLogger("Junior Runner")
        self.display: Optional[pygame.display] = None
        self.controller = JuniorKeyboardController(config=self.config)
        self.setup_pygame()

    def start_game_loop(self, auto_pilot=False):
        self.is_auto = auto_pilot
        self.logger.info("Starting Game loop")
        try:
            clock = pygame.time.Clock()
            should_continue = True
            while should_continue:
                # update pygame rendering
                should_continue, control, is_manual_toggled = self.update_pygame(clock=clock)

                # update images
                frame = self.fetch_new_frame()
                if frame is not None:
                    sensors_data: SensorsData = SensorsData(
                        front_rgb=RGBData(data=frame)
                    )

                    # run agent step
                    agent_control = self.agent.run_step(sensors_data=sensors_data, vehicle=Vehicle())
                    if self.is_auto:
                        control = agent_control

                differential_control: dict = self.ackermann_to_diff(control=control)

                distance = self.sendControl(differential_control, timeout=2)
        except Exception as e:
            self.logger.error(f"Something bad happend {e}")

        finally:
            self.on_finish()

    def sendControl(self, diff_control: dict, timeout=0.5) -> Optional[float]:
        try:
            response = requests.get(f"http://{self.config.ip_addr}:81", params=diff_control, timeout=timeout)
            distance = float(response.content.decode('utf-8'))
            return distance
        except Exception as e:
            self.logger.error(e)
            return None

    def ackermann_to_diff(self, control: VehicleControl) -> dict:
        msg = dict()
        if control.throttle == 0:
            msg[self.config.stop_mode_cmd] = True
        elif control.throttle > 0:
            msg[self.config.forward_mode_cmd] = True
        else:
            msg[self.config.backward_mode_cmd] = True

        if control.steering == 0:
            msg[self.config.right_spd_route] = 1
            msg[self.config.left_spd_route] = 1
        elif control.steering < 0:
            # 0.2 * (x%)
            msg[self.config.right_spd_route] = self.config.base_throttle + (1 - self.config.base_throttle) * \
                                              control.steering * -1
            msg[self.config.left_spd_route] = 0
        else:
            msg[self.config.left_spd_route] = self.config.base_throttle + (1 - self.config.base_throttle) * \
                                              control.steering
            msg[self.config.right_spd_route] = 0

        return msg

    def fetch_new_frame(self) -> Optional[np.ndarray]:
        try:
            response = requests.get(f"http://{self.config.ip_addr}/cam-lo.jpg", timeout=0.5)
            jpg = response.content
            image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            return image
        except requests.exceptions.Timeout or requests.exceptions.ConnectionError:
            self.logger.error("Video Frame Timed out")
            return None
        except Exception as e:
            self.logger.error(e)
            return None

    def on_finish(self):
        self.logger.info("Finishing...")
        self.sendControl(diff_control={self.config.stop_mode_cmd: True}, timeout=2)
        self.agent.shutdown_module_threads()

    def update_pygame(self, clock) -> Tuple[bool, VehicleControl, bool]:
        """
        Update the pygame window, including parsing keypress
        Args:
            clock: pygame clock
        Returns:
            bool - whether to continue the game
            VehicleControl - the new VehicleControl cmd by the keyboard
        """
        if self.display is not None and self.agent.front_rgb_camera.data is not None:
            frame = self.agent.front_rgb_camera.data.copy()
            if frame is not None:
                frame = cv2.flip(cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE), 0)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame: np.ndarray = cv2.resize(frame,
                                               dsize=(self.pygame_display_height, self.pygame_display_width))
                pygame.surfarray.blit_array(self.display, frame)
                pygame.display.flip()
        pygame.display.flip()
        return self.controller.parse_events(clock=clock)

    def setup_pygame(self):
        """
        Initiate pygame
        Returns:

        """
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode((self.pygame_display_width,
                                                self.pygame_display_height))
        self.logger.debug("PyGame initiated")
