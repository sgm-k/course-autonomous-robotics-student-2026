# Third-party notices

`ros2_ws/src/course_robot/config/nav2_params.yaml` is adapted from
the ROS 2 Jazzy Nav2 default parameter file in `nav2_bringup` 1.3.12.
Nav2 is distributed under the Apache License 2.0. The course-specific changes
set MVSim topic/frame names, robot size, and conservative velocity limits.
The license text is included at `licenses/Apache-2.0.txt`.

Source: <https://github.com/ros-navigation/navigation2/tree/jazzy/nav2_bringup/params>

`ros2_ws/src/course_robot/models/turtlebot3/` contains 3D models of the TurtleBot3
(`burger_base.dae`, `lds.dae`) from ROBOTIS turtlebot3_simulations, distributed under
the Apache License 2.0 (see `LICENSE.md` in that directory and `licenses/Apache-2.0.txt`).
They were obtained from the MVSim model repository (https://mrpt.github.io/mvsim-models/).

`ros2_ws/src/course_robot/worlds/course_burger.vehicle.xml` is based on the
`turtlebot3_burger.vehicle.xml` definition shipped with MVSim (BSD 3-Clause License).
