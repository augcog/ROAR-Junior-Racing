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


async def main(tasks):
    await asyncio.wait(tasks)


def createBLETasks(ble_connection: BLEConnection) -> List:
    """
    Create Bluetooth related tasks
    :param ble_connection: Bluetooth connection object
    :return:
        List of task that asyncio can start
    """
    return [loop.create_task(ble_connection.connectHelper()),
            loop.create_task(ble_connection.startSendControl()),
            # loop.create_task(ble_connection.startUpdateAcc()),
            # loop.create_task(ble_connection.startupdateOrientation()),
            # loop.create_task(ble_connection.startUpdateTrackingAndUltrasonic())
            ]


def createGameTask(game: Game) -> List:
    """
    Create game related Tasks
    :param game: game object
    :return:
        List of task related to game
    """
    return [loop.create_task(game.run())]


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
    game = Game(ble_connection=connection, loop=loop, rate=0.1, debug_level=logging.DEBUG)
    tasks = []
    tasks.extend(createBLETasks(ble_connection=connection))
    tasks.extend(createGameTask(game=game))

    # start all tasks
    try:
        loop.run_until_complete(main(tasks))
        loop.close()
    except KeyboardInterrupt:
        print("User Stopped Program")
    finally:
        connection.on_disconnect()
