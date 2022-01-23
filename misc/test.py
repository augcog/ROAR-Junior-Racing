import requests

# host = "michaelwu666.mynetgear.com:80"
#
# response = requests.get(f"http://{host}/flash")
# print(response.status_code, response.content)

host = "192.168.1.24"
params = {
    "stop": True,
    "right_spd": 1,
    "left_spd": 1,
}

response = requests.get(f"http://{host}:81", params=params)
print(response.status_code, response.content)

