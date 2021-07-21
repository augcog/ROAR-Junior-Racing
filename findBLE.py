import asyncio

try:
    from bluetooth.ble import BLEConnection
except:
    from ROAR_Junior.bluetooth.ble import BLEConnection


async def main(tasks):
    await asyncio.wait(tasks)


if __name__ == '__main__':
    tasks = [BLEConnection.scan()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(tasks))
