import requests
from typing import Optional


def sendCmd(ip_addr: str, cmd: dict, timeout: int = 2) -> Optional[bytes]:
    """
    A wrapper for sending command. Command should be in the format of
    {
        DIRECTION: True/False,
        "left_spd": [0-1],
        "right_spd": [0-1],
    }

    This function will send a GET request to target URL with CMD as parameter.
    If the GET request failed, it will print the error and return None, otherwise it will return the content of the response, which is the ultrasonic sensor reading.
    :param ip_addr: ip address of the vehicle
    :param cmd: command to send
    :return:
    None if GET request failed, ultrasonic sensor reading in received in bytes if GET request is successful.
    """
    try:
        response = requests.get(f"http://{ip_addr}:81", params=cmd, timeout=timeout)
        return response.content
    except Exception as e:
        print(e)
        return None
