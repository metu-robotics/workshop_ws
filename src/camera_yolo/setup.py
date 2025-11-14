from setuptools import find_packages, setup

package_name = 'camera_yolo'

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
    description='Camera and YOLO integration for ROS 2',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'camera_node = camera_yolo.camera_node:main',
        'yolo_node = camera_yolo.yolo_node:main'
        ],
    },
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/camera_yolo']),
        ('share/camera_yolo/launch', ['launch/camera_yolo.launch.py']),
        ('share/camera_yolo', ['package.xml']),
    ],
)
