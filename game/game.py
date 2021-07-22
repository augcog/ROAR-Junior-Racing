import pygame

from typing import Optional, Tuple
import logging
import asyncio

try:
    from bluetooth.ble import BLEConnection
except:
    from ROAR_Junior.bluetooth.ble import BLEConnection
try:
    from ROAR_Junior.keyboard_control import JuniorKeyboardControl
except:
    from keyboard_control import JuniorKeyboardControl

from utilities import VehicleState


class Game:
    def __init__(self, ble_connection: BLEConnection, loop, rate: float = 0.05, debug_level=logging.DEBUG):
        self.logger = logging.getLogger("Game")
        self.logger.setLevel(level=debug_level)
        self.vehicle_state = VehicleState()
        self.ble_connection = ble_connection
        self.loop = loop
        self.rate = rate
        self.display: Optional[pygame.display] = None
        self.controller = JuniorKeyboardControl(
            log_level=logging.INFO
        )

        self.setup()

        self.should_continue = True

    def setup(self):
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)

    async def run(self):
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
        clock = pygame.time.Clock()
        try:
            while self.should_continue:
                if self.ble_connection.is_connected:
                    if clock.get_time() == 0:
                        self.logger.info("Starting Game")
                    clock.tick_busy_loop(60)
                    self.should_continue, \
                    (self.vehicle_state.motor_left, self.vehicle_state.motor_right,
                     self.vehicle_state.motor_left_mode, self.vehicle_state.motor_right_mode) = self.update_pygame(clock)
                    self.update_ble()
                    # self.execute_user_action()
                    self.debug_state()
                await asyncio.sleep(self.rate, loop=self.loop)
        except KeyboardInterrupt:
            self.logger.info("Keyboard Interrupt detected, safely quitting.")

        except Exception as e:
            self.logger.error(f"Something bad happened: [{e}]")
        finally:
            self.on_finish()

    def debug_state(self):
        self.logger.info(self.vehicle_state)

    def update_ble(self):
        # get data
        self.vehicle_state.aX = self.ble_connection.acc_x
        self.vehicle_state.aY = self.ble_connection.acc_y
        self.vehicle_state.aZ = self.ble_connection.acc_z
        self.vehicle_state.roll = self.ble_connection.roll
        self.vehicle_state.pitch = self.ble_connection.pitch
        self.vehicle_state.yaw = self.ble_connection.yaw
        self.vehicle_state.is_left_tracing = self.ble_connection.is_left_tracking
        self.vehicle_state.is_right_tracking = self.ble_connection.is_left_tracking
        self.vehicle_state.ultra_dist = self.ble_connection.ultrasonic_distance

        # send data
        self.ble_connection.motor_left_tx_data = self.vehicle_state.motor_left
        self.ble_connection.motor_right_tx_data = self.vehicle_state.motor_right
        self.ble_connection.motor_left_mode_tx = self.vehicle_state.motor_left_mode
        self.ble_connection.motor_right_mode_tx = self.vehicle_state.motor_right_mode

    def on_finish(self):
        self.ble_connection.motor_left_tx_data = self.vehicle_state.motor_left = 0
        self.ble_connection.motor_left_tx_data = self.vehicle_state.motor_right = 0
        self.should_continue = False
        self.ble_connection.should_continue = False

        self.logger.info("Game Stopped")

    def update_pygame(self, clock) -> Tuple[bool, Tuple[int, int, bool, bool]]:
        return self.controller.parse_events(clock=clock)

    def execute_user_action(self):
        self.logger.info("Executing User Action")
        # TODO your code here for autonomous driving.
