"""Command-line demonstration of differential-drive kinematics."""

from course_robot.kinematics import wheel_speeds_to_twist


def main() -> None:
    """Print the three examples used in lesson 1."""
    wheel_radius = 0.20
    wheel_separation = 1.00
    examples = [(5.0, 5.0), (2.0, 6.0), (-4.0, 4.0)]

    print('left [rad/s]  right [rad/s]  linear [m/s]  angular [rad/s]')
    for left, right in examples:
        linear, angular = wheel_speeds_to_twist(
            left, right, wheel_radius, wheel_separation)
        print(f'{left:12.3f}  {right:13.3f}  '
              f'{linear:12.3f}  {angular:15.3f}')


if __name__ == '__main__':
    main()
