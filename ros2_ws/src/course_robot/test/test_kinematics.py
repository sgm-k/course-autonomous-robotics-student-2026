import math

from course_robot.kinematics import integrate_euler
from course_robot.kinematics import Pose2D
from course_robot.kinematics import wheel_speeds_to_twist
import pytest


def test_equal_wheel_speeds_produce_straight_motion():
    linear, angular = wheel_speeds_to_twist(5.0, 5.0, 0.20, 1.00)
    assert linear == pytest.approx(1.0)
    assert angular == pytest.approx(0.0)


def test_opposite_wheel_speeds_produce_rotation():
    linear, angular = wheel_speeds_to_twist(-4.0, 4.0, 0.20, 1.00)
    assert linear == pytest.approx(0.0)
    assert angular == pytest.approx(1.6)


def test_euler_integration_uses_heading():
    pose = Pose2D(x=1.0, y=2.0, yaw=math.pi / 2.0)
    result = integrate_euler(pose, 0.5, 0.2, 0.1)
    assert result.x == pytest.approx(1.0)
    assert result.y == pytest.approx(2.05)
    assert result.yaw == pytest.approx(math.pi / 2.0 + 0.02)


@pytest.mark.parametrize('radius,separation', [
    (0.0, 0.16),
    (-0.1, 0.16),
    (0.033, 0.0),
    (0.033, -0.2),
])
def test_invalid_dimensions_are_rejected(radius, separation):
    with pytest.raises(ValueError):
        wheel_speeds_to_twist(1.0, 1.0, radius, separation)
