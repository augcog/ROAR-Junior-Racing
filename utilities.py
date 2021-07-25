from pydantic import Field, BaseModel, validator
import enum


class LeftModeEnum(enum.Enum):
    forward = True
    backward = False


class RightModeEnum(enum.Enum):
    forward = True
    backward = False


class VehicleState(BaseModel):
    aX: float = Field(0)
    aY: float = Field(0)
    aZ: float = Field(0)
    gyroX: float = Field(0)
    gyroY: float = Field(0)
    gyroZ: float = Field(0)
    magX: float = Field(0)
    magY: float = Field(0)
    magZ: float = Field(0)
    motor_left: int = Field(0)
    motor_right: int = Field(0)
    motor_left_mode: bool = Field(True, description="True is Forward")
    motor_right_mode: bool = Field(True, description="True is Forward")

    is_left_tracking: bool = Field(True)
    is_right_tracking: bool = Field(True)
    ultra_dist: int = Field(300)