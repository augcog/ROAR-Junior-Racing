from pydantic import BaseModel, Field


class JuniorConfig(BaseModel):
    name: str = Field("MyCar")
    ip_addr: str = Field("127.0.0.1")
    cam_port: int = Field("80")
    cmd_port: int = Field("81")

    forward_mode_cmd: str = Field("forward")
    backward_mode_cmd: str = Field("backward")
    stop_mode_cmd: str = Field("stop")
    left_mode_cmd: str = Field("turnLeft")
    right_mode_cmd: str = Field("turnRight")

    left_spd_route: str = Field("left_spd")
    right_spd_route: str = Field("right_spd")

    pygame_display_width: int = Field(1080)
    pygame_display_height: int = Field(810)

    throttle_increment: float = Field(0.05)
    steering_increment: float = Field(0.05)

    base_throttle: float = Field(0.8)
