import asyncio
from bleak import *
from bleak.backends.device import BLEDevice
from typing import List, Optional, Union
import logging
from utilities import VehicleState
import time
import struct
from game.game import Game


def on_roll_char_rx_callback(sender: int, data: bytes):
    print(f"{sender}: {data}")


class BLEConnection:
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 device_addr: str,
                 cam_ip_addr: Optional[str] = None,
                 game_rate: float = 0.01,
                 motor_left_tx_uuid: str = "00000000-0000-0000-0000-000000000000",
                 motor_right_tx_uuid: str = "00000000-0000-0000-0000-000000000001",
                 motor_left_rx_uuid: str = "00000000-0000-0000-0000-000000000002",
                 motor_right_rx_uuid: str = "00000000-0000-0000-0000-000000000003",
                 acc_x_char_rx_uuid: str = "00000000-0000-0000-0000-000000000004",
                 acc_y_char_rx_uuid: str = "00000000-0000-0000-0000-000000000005",
                 acc_z_char_rx_uuid: str = "00000000-0000-0000-0000-000000000006",
                 gyro_x_char_rx_uuid: str = "00000000-0000-0000-0000-000000000007",
                 gyro_y_char_rx_uuid: str = "00000000-0000-0000-0000-000000000008",
                 gyro_z_char_rx_uuid: str = "00000000-0000-0000-0000-000000000009",
                 mag_x_char_rx_uuid: str = "00000000-0000-0000-0000-000000000017",
                 mag_y_char_rx_uuid: str = "00000000-0000-0000-0000-000000000018",
                 mag_z_char_rx_uuid: str = "00000000-0000-0000-0000-000000000019",
                 motor_left_mode_tx_uuid: str = "00000000-0000-0000-0000-000000000010",
                 motor_right_mode_tx_uuid: str = "00000000-0000-0000-0000-000000000011",
                 motor_left_mode_rx_uuid: str = "00000000-0000-0000-0000-000000000012",
                 motor_right_mode_rx_uuid: str = "00000000-0000-0000-0000-000000000013",
                 left_line_tracking_rx_uuid: str = "00000000-0000-0000-0000-000000000014",
                 right_line_tracking_rx_uuid: str = "00000000-0000-0000-0000-000000000015",
                 ultrasonic_rx_uuid: str = "00000000-0000-0000-0000-000000000016",
                 debug: int = logging.INFO):
        self.logger = logging.getLogger("BLEConnection")
        self.logger.setLevel(debug)
        self.loop = loop
        self.device_addr = device_addr
        self.motor_left_tx_uuid = motor_left_tx_uuid
        self.motor_right_tx_uuid = motor_right_tx_uuid
        self.motor_left_rx_uuid = motor_left_rx_uuid
        self.motor_right_rx_uuid = motor_right_rx_uuid
        self.acc_x_char_rx_uuid = acc_x_char_rx_uuid
        self.acc_y_char_rx_uuid = acc_y_char_rx_uuid
        self.acc_z_char_rx_uuid = acc_z_char_rx_uuid
        self.gyro_x_char_rx_uuid = gyro_x_char_rx_uuid
        self.gyro_y_char_rx_uuid = gyro_y_char_rx_uuid
        self.gyro_z_char_rx_uuid = gyro_z_char_rx_uuid
        self.mag_x_char_rx_uuid = mag_x_char_rx_uuid
        self.mag_y_char_rx_uuid = mag_y_char_rx_uuid
        self.mag_z_char_rx_uuid = mag_z_char_rx_uuid

        self.motor_left_mode_tx_uuid = motor_left_mode_tx_uuid
        self.motor_right_mode_tx_uuid = motor_right_mode_tx_uuid
        self.motor_left_mode_rx_uuid = motor_left_mode_rx_uuid
        self.motor_right_mode_rx_uuid = motor_right_mode_rx_uuid

        self.left_line_tracking_rx_uuid = left_line_tracking_rx_uuid
        self.right_line_tracking_rx_uuid = right_line_tracking_rx_uuid
        self.ultrasonic_rx_uuid = ultrasonic_rx_uuid

        self.client = BleakClient(self.device_addr,
                                  loop=self.loop,
                                  timeout=5)

        # state variables
        self.should_continue = True

        self.is_connected = False
        self.device: Optional[BLEDevice] = None
        self.vehicle_state = VehicleState()
        self.game = Game(vehicle_state=self.vehicle_state, cam_ip_addr=cam_ip_addr, debug_level=debug)
        self.game_rate = game_rate

    def on_disconnect(self, any):
        """
        Call back handler for Bleak.BLEClient.set_disconnected_callback
        :return:
            None
        """
        self.is_connected = False
        self.logger.debug("Disconnected")

    async def send_motor_data(self):
        """
        send latest motor data
        :return:
        """

        await self.client.write_gatt_char(self.motor_left_tx_uuid,
                                          bytes(self.ensure_three_digit_str(self.vehicle_state.motor_left),
                                                encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_right_tx_uuid,
                                          bytes(self.ensure_three_digit_str(self.vehicle_state.motor_right),
                                                encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_left_mode_tx_uuid,
                                          bytes(f"{self.vehicle_state.motor_left_mode}", encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_right_mode_tx_uuid,
                                          bytes(f"{self.vehicle_state.motor_right_mode}", encoding='utf-8'))

    @staticmethod
    def ensure_three_digit_str(info: int) -> str:
        if info < 10:
            data = f"00{info}"
        elif info < 100:
            data = f"0{info}"
        else:
            data = str(info)
        return data

    @staticmethod
    async def scan():
        """
        Scan nearby BLE devices and print them out
        :return:
            list of devices
        """
        devices: List[BLEDevice] = await discover()
        for i, device in enumerate(devices):
            print(f"{i} -> {device.name} -> {device.address}")
        return devices

    async def startSendControl(self, rate=0.025):
        """
        Used in Asyncio to create a loop for sending motor data

        :param rate: rate to send it at. 1 / rate = FPS
        :return:
            None
        """
        while self.should_continue:
            if self.is_connected:
                await self.send_motor_data()
                await asyncio.sleep(rate, self.loop)
            else:
                await asyncio.sleep(1, self.loop)

    async def connect_to_device(self):

        while self.should_continue:
            try:
                if self.is_connected is False:
                    self.logger.debug(f"Scanning for device with UUID [{self.device_addr}]")
                    # scan
                    devices: List[BLEDevice] = await discover()
                    # get device name
                    for device in devices:
                        if device.address == self.device_addr:
                            self.device = device
                            break
                    if self.device is None:
                        raise BleakError(f"No Device with Address found {self.device_addr}. "
                                         f"Please use `scan` to find your device address first")

                self.logger.info(f"Connecting to {self.device.name}: {self.device_addr}")
                await self.client.connect()
                self.is_connected = self.client.is_connected
                self.client.set_disconnected_callback(self.on_disconnect)
                if self.is_connected:
                    self.logger.info(f"Connected to {self.device.name}")

                    await self.client.start_notify(self.motor_left_rx_uuid, self.motor_left_notify_callback)
                    await self.client.start_notify(self.motor_right_rx_uuid, self.motor_right_notify_callback)
                    await self.client.start_notify(self.motor_left_mode_rx_uuid, self.motor_left_mode_notify_callback)
                    await self.client.start_notify(self.motor_right_mode_rx_uuid, self.motor_right_mode_notify_callback)

                    await self.client.start_notify(self.gyro_x_char_rx_uuid, self.roll_notify_callback, )
                    await self.client.start_notify(self.gyro_y_char_rx_uuid, self.pitch_notify_callback, )
                    await self.client.start_notify(self.gyro_z_char_rx_uuid, self.yaw_notify_callback, )
                    await self.client.start_notify(self.acc_x_char_rx_uuid, self.acc_x_notify_callback, )
                    await self.client.start_notify(self.acc_y_char_rx_uuid, self.acc_y_notify_callback, )
                    await self.client.start_notify(self.acc_z_char_rx_uuid, self.acc_z_notify_callback, )
                    await self.client.start_notify(self.mag_x_char_rx_uuid, self.mag_x_notify_callback, )
                    await self.client.start_notify(self.mag_y_char_rx_uuid, self.mag_y_notify_callback, )
                    await self.client.start_notify(self.mag_z_char_rx_uuid, self.mag_z_notify_callback, )

                    await self.client.start_notify(self.left_line_tracking_rx_uuid, self.left_line_notify_callback, )
                    await self.client.start_notify(self.right_line_tracking_rx_uuid, self.right_line_notify_callback, )
                    await self.client.start_notify(self.ultrasonic_rx_uuid, self.ultrasonic_notify_callback, )

                    while self.should_continue:
                        self.should_continue = self.game.run_step()
                        if not self.is_connected:
                            break
                        await asyncio.sleep(self.game_rate)

                    self.logger.debug("Stop Notifying")
                    await self.client.stop_notify(self.motor_left_rx_uuid)
                    await self.client.stop_notify(self.motor_right_rx_uuid)
                    await self.client.stop_notify(self.motor_left_mode_rx_uuid)
                    await self.client.stop_notify(self.motor_right_mode_rx_uuid)
                    await self.client.stop_notify(self.gyro_x_char_rx_uuid)
                    await self.client.stop_notify(self.gyro_y_char_rx_uuid)
                    await self.client.stop_notify(self.gyro_z_char_rx_uuid)
                    await self.client.stop_notify(self.mag_x_char_rx_uuid)
                    await self.client.stop_notify(self.mag_y_char_rx_uuid)
                    await self.client.stop_notify(self.mag_z_char_rx_uuid)
                    await self.client.stop_notify(self.acc_x_char_rx_uuid)
                    await self.client.stop_notify(self.acc_y_char_rx_uuid)
                    await self.client.stop_notify(self.acc_z_char_rx_uuid)
                    await self.client.stop_notify(self.left_line_tracking_rx_uuid)
                    await self.client.stop_notify(self.right_line_tracking_rx_uuid)
                    await self.client.stop_notify(self.ultrasonic_rx_uuid)

                    self.should_continue = False
                else:
                    print(f"Failed to connect to Device")
            except Exception as e:
                print(e)

    async def motor_left_notify_callback(self, _, __):
        await self.client.write_gatt_char(self.motor_left_tx_uuid,
                                          bytes(self.ensure_three_digit_str(self.vehicle_state.motor_left),
                                                encoding='utf-8'))

    async def motor_right_notify_callback(self, _, __):
        await self.client.write_gatt_char(self.motor_right_tx_uuid,
                                          bytes(self.ensure_three_digit_str(self.vehicle_state.motor_right),
                                                encoding='utf-8'))

    async def motor_left_mode_notify_callback(self, _, __):
        await self.client.write_gatt_char(self.motor_left_mode_tx_uuid,
                                          bytes(f"{self.vehicle_state.motor_left_mode}", encoding='utf-8'))

    async def motor_right_mode_notify_callback(self, _, __):
        await self.client.write_gatt_char(self.motor_right_mode_tx_uuid,
                                          bytes(f"{self.vehicle_state.motor_right_mode}", encoding='utf-8'))

    def roll_notify_callback(self, _, data):
        [self.vehicle_state.gyroX] = struct.unpack('f', data)

    def pitch_notify_callback(self, _, data):
        [self.vehicle_state.gyroY] = struct.unpack('f', data)

    def yaw_notify_callback(self, _, data):
        [self.vehicle_state.gyroZ] = struct.unpack('f', data)

    def acc_x_notify_callback(self, _, data):
        [self.vehicle_state.aX] = struct.unpack('f', data)

    def acc_y_notify_callback(self, _, data):
        [self.vehicle_state.aY] = struct.unpack('f', data)

    def acc_z_notify_callback(self, _, data):
        [self.vehicle_state.aZ] = struct.unpack('f', data)

    def mag_x_notify_callback(self, _, data):
        [self.vehicle_state.magX] = struct.unpack('f', data)

    def mag_y_notify_callback(self, _, data):
        [self.vehicle_state.magY] = struct.unpack('f', data)

    def mag_z_notify_callback(self, _, data):
        [self.vehicle_state.magZ] = struct.unpack('f', data)

    def left_line_notify_callback(self, _, data):
        self.vehicle_state.is_left_tracking = bool(ord(data))

    def right_line_notify_callback(self, _, data):
        self.vehicle_state.is_right_tracking = bool(ord(data))

    def ultrasonic_notify_callback(self, _, data):
        self.vehicle_state.ultra_dist = int.from_bytes(data, "little", signed=True)
