import asyncio
from bleak import *
from bleak.backends.device import BLEDevice
from typing import List, Optional, Union
import logging
from utilities import VehicleState
import time

class BLEConnection:
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 device_addr: str,
                 motor_left_tx_uuid: str = "00000000-0000-0000-0000-000000000000",
                 motor_right_tx_uuid: str = "00000000-0000-0000-0000-000000000001",
                 motor_left_rx_uuid: str = "00000000-0000-0000-0000-000000000002",
                 motor_right_rx_uuid: str = "00000000-0000-0000-0000-000000000003",
                 acc_x_char_rx_uuid: str = "00000000-0000-0000-0000-000000000004",
                 acc_y_char_rx_uuid: str = "00000000-0000-0000-0000-000000000005",
                 acc_z_char_rx_uuid: str = "00000000-0000-0000-0000-000000000006",
                 roll_char_rx_uuid: str = "00000000-0000-0000-0000-000000000007",
                 pitch_char_rx_uuid: str = "00000000-0000-0000-0000-000000000008",
                 yaw_char_rx_uuid: str = "00000000-0000-0000-0000-000000000009",
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
        self.roll_char_rx_uuid = roll_char_rx_uuid
        self.pitch_char_rx_uuid = pitch_char_rx_uuid
        self.yaw_char_rx_uuid = yaw_char_rx_uuid

        self.motor_left_mode_tx_uuid = motor_left_mode_tx_uuid
        self.motor_right_mode_tx_uuid = motor_right_mode_tx_uuid
        self.motor_left_mode_rx_uuid = motor_left_mode_rx_uuid
        self.motor_right_mode_rx_uuid = motor_right_mode_rx_uuid

        self.left_line_tracking_rx_uuid = left_line_tracking_rx_uuid
        self.right_line_tracking_rx_uuid = right_line_tracking_rx_uuid
        self.ultrasonic_rx_uuid = ultrasonic_rx_uuid

        self.client = BleakClient(self.device_addr, loop=self.loop)

        # state variables
        self.should_continue = True

        self.is_connected = False
        self.device: Optional[BLEDevice] = None

        self.motor_left_tx_data: int = 0
        self.motor_right_tx_data: int = 0
        self.motor_left_rx_data: int = 0
        self.motor_right_rx_data: int = 0
        self.motor_left_mode_rx: bool = True
        self.motor_right_mode_rx: bool = True
        self.motor_left_mode_tx: bool = True
        self.motor_right_mode_tx: bool = True

        self.acc_x: float = 0
        self.acc_y: float = 0
        self.acc_z: float = 0
        self.roll: float = 0
        self.pitch: float = 0
        self.yaw: float = 0

        self.is_left_tracking: bool = False
        self.is_right_tracking: bool = False
        self.ultrasonic_distance: int = 300

    def on_disconnect(self):
        """
        Call back handler for Bleak.BLEClient.set_disconnected_callback
        :return:
            None
        """
        self.is_connected = False
        self.logger.debug("Disconnected")

    async def connectHelper(self):
        """
        Attempt to connect to the device with the address provided.
        Set the disconnection call back on connection successfully established

        :return:
            None
        """
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
        try:
            self.logger.info(f"Attempting to connect to {self.device.name}")
            await self.client.connect()

            self.is_connected = self.client.is_connected
            if self.is_connected:
                self.logger.info(f"Connected to {self.device.name}")
                self.client.set_disconnected_callback(self.on_disconnect)
        except Exception as e:
            self.logger.error(e)

    def get_state(self) -> str:
        """
        Get a String representation of the current State
        :return:
            comma delimited string of states.
        """
        return f"{self.acc_x}, {self.acc_y}, {self.acc_z} | {self.roll}, {self.pitch}, {self.yaw} | {self.motor_left_rx_data}, {self.motor_right_rx_data}"

    async def getTrackingAndUltrasonicData(self):
        """
        Send BLE call for getting left and right line tracking sensor data
        NOTE: will overwrite original data
        :return:
            None
        """
        # print("Getting Tracking Data")
        self.is_left_tracking = bool(ord(await self.client.read_gatt_char(self.left_line_tracking_rx_uuid)))
        self.is_right_tracking = bool(ord(await self.client.read_gatt_char(self.right_line_tracking_rx_uuid)))
        self.ultrasonic_distance = int.from_bytes(await self.client.read_gatt_char(self.ultrasonic_rx_uuid), "little", signed=True)

    async def get_motor_data(self):
        """
        Send BLE call for getting motor data
        Note: Will overwrite original data
        :return:
            None
        """
        self.motor_left_rx_data = int.from_bytes(await self.client.read_gatt_char(self.motor_left_rx_uuid),
                                                 "little", signed=True)
        self.motor_right_rx_data = int.from_bytes(await self.client.read_gatt_char(self.motor_right_rx_uuid),
                                                  "little", signed=True)
        self.motor_left_mode_rx = bool(await self.client.read_gatt_char(self.motor_left_mode_rx_uuid))
        self.motor_right_mode_rx = bool(await self.client.read_gatt_char(self.motor_right_mode_rx_uuid))

    async def get_acc(self):
        """
        Send BLE call for getting accelerometer data
        Note:
        :return:
            None
        """
        self.acc_x = float(await self.client.read_gatt_char(self.acc_x_char_rx_uuid))
        self.acc_y = float(await self.client.read_gatt_char(self.acc_y_char_rx_uuid))
        self.acc_z = float(await self.client.read_gatt_char(self.acc_z_char_rx_uuid))

    async def get_orientation(self):
        """
        Send BLE call to get the Orientation data
        Note: Will overwrite original data

        :return:
            None
        """
        self.roll = float(await self.client.read_gatt_char(self.roll_char_rx_uuid))
        self.pitch = float(await self.client.read_gatt_char(self.pitch_char_rx_uuid))
        self.yaw = float(await self.client.read_gatt_char(self.yaw_char_rx_uuid))

    async def send_motor_data(self):
        """
        send latest motor data
        :return:
        """
        await self.client.write_gatt_char(self.motor_left_tx_uuid,
                                          bytes(f"{self.motor_left_tx_data}", encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_right_tx_uuid,
                                          bytes(f"{self.motor_right_tx_data}", encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_left_mode_tx_uuid,
                                          bytes(f"{self.motor_left_mode_tx}", encoding='utf-8'))
        await self.client.write_gatt_char(self.motor_right_mode_tx_uuid,
                                          bytes(f"{self.motor_right_mode_tx}", encoding='utf-8'))

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

    async def startUpdateTrackingAndUltrasonic(self, rate=0.025):
        while self.should_continue:
            if self.is_connected:
                await self.getTrackingAndUltrasonicData()
                await asyncio.sleep(rate, self.loop)
            else:
                await asyncio.sleep(1, self.loop)

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

    async def startUpdateAcc(self, rate=0.025):
        """
        Used in Asyncio to create a loop for getting accelerometer data

        :param rate: rate to send it at. 1 / rate = FPS
        :return:
            None
        """
        while self.should_continue:
            if self.is_connected:
                await self.get_acc()
                await asyncio.sleep(rate, self.loop)
            else:
                await asyncio.sleep(1, self.loop)

    async def startupdateOrientation(self, rate=0.025):
        """
        Used in Asyncio to create a loop for getting Gyro data, converted to orientation

        :param rate: rate to send it at. 1 / rate = FPS
        :return:
            None
        """
        while self.should_continue:
            if self.is_connected:
                await self.get_orientation()
                await asyncio.sleep(rate, self.loop)
            else:
                await asyncio.sleep(1, self.loop)

    async def connect(self):
        await self.connectHelper()


async def main(loop, connection):
    # f1 = loop.create_task(connect(connection=connection))
    f1 = loop.create_task(connection.connectHelper())
    f2 = loop.create_task(connection.startUpdateAcc())
    f3 = loop.create_task(connection.startupdateOrientation())
    await asyncio.wait([f1, f2, f3])


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S")
    loop = asyncio.get_event_loop()
    deviceUUID = "095D2164-4A57-47B0-8857-BDA8537BBFA1"
    connection: BLEConnection = BLEConnection(
        loop=loop,
        device_addr=deviceUUID,
        debug=logging.DEBUG
    )
    try:
        loop.run_until_complete(main(loop, connection))
        loop.close()
    except KeyboardInterrupt:
        print("User Stopped Program")
    finally:
        connection.on_disconnect()
