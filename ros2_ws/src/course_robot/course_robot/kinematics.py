"""Kinematics functions for a differential-drive mobile robot."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Pose2D:
    """Planar robot pose in metres and radians."""

    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0


def wheel_speeds_to_twist(
        left_angular_speed: float,
        right_angular_speed: float,
        wheel_radius: float,
        wheel_separation: float,
) -> tuple[float, float]:
    """Return linear and angular velocity from wheel angular velocities."""
    if wheel_radius <= 0.0:
        raise ValueError('wheel_radius must be positive')
    if wheel_separation <= 0.0:
        raise ValueError('wheel_separation must be positive')

    linear = 0.5 * wheel_radius * (
        right_angular_speed + left_angular_speed)
    angular = wheel_radius * (
        right_angular_speed - left_angular_speed) / wheel_separation
    return linear, angular


def integrate_euler(
        pose: Pose2D,
        linear_speed: float,
        angular_speed: float,
        time_step: float,
) -> Pose2D:
    """Advance a planar pose by one explicit-Euler integration step."""
    if time_step <= 0.0:
        raise ValueError('time_step must be positive')

    return Pose2D(
        x=pose.x + linear_speed * math.cos(pose.yaw) * time_step,
        y=pose.y + linear_speed * math.sin(pose.yaw) * time_step,
        yaw=pose.yaw + angular_speed * time_step,
    )
