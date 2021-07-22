from pydantic import Field, BaseModel


class VehicleState(BaseModel):
    aX: float = Field(0)
    aY: float = Field(0)
    aZ: float = Field(0)
    roll: float = Field(0)
    pitch: float = Field(0)
    yaw: float = Field(0)
    motor_left: int = Field(0)
    motor_right: int = Field(0)
    motor_left_mode: bool = Field(True, description="True is Forward")
    motor_right_mode: bool = Field(True, description="True is Forward")

    is_left_tracing: bool = Field(True)
    is_right_tracking: bool = Field(True)
    ultra_dist: int = Field(300)