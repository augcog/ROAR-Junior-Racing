import logging
from typing import List
import asyncio

try:
    from bluetooth.ble import BLEConnection
except:
    from ROAR_Junior.bluetooth.ble import BLEConnection

try:
    from game.game import Game
except:
    from ROAR_Junior.game.game import Game

if __name__ == '__main__':

    # define logging format
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S")

    loop = asyncio.get_event_loop()
    # you may get this by doing BLEConnection.scan() and copy the ID of the device you want to connect to.
    deviceUUID = "095D2164-4A57-47B0-8857-BDA8537BBFA1"

    # prelude: Initialize Game and BLE connection
    connection: BLEConnection = BLEConnection(
        loop=loop,
        device_addr=deviceUUID,
        debug=logging.DEBUG)

    try:
        loop.run_until_complete(connection.connect_to_device())
    except KeyboardInterrupt:
        print("User Stopped Program")


