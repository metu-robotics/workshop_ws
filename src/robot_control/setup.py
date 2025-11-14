from setuptools import find_packages, setup

package_name = 'robot_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Aria Karimi',
    maintainer_email='aria.karimi@metu.edu.tr',
    description='Control interface for the robot',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/robot_control']),
        ('share/robot_control/launch', ['launch/robot_control.launch.py']),
        ('share/robot_control', ['package.xml']),
    ],
)
