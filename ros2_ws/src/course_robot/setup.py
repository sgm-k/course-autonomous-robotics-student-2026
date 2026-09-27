from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'course_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*.world.xml')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.rviz') + glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sgm-k',
    maintainer_email='teacher@example.invalid',
    description='Course materials for mobile robotics with ROS 2 and MVSim.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'constant_velocity = '
            'course_robot.constant_velocity:main',
            'kinematics_demo = '
            'course_robot.kinematics_demo:main',
            'scan_relay = '
            'course_robot.scan_relay:main',
        ],
    },
)
