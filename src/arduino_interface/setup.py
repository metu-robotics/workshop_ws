from setuptools import find_packages, setup

package_name = 'arduino_interface'

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
    description='Interface for Arduino communication',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'serial_node = arduino_interface.serial_node:main'
        ],
    },
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/arduino_interface']),
        ('share/arduino_interface/launch', ['launch/arduino.launch.py']),
        ('share/arduino_interface', ['package.xml']),
    ],
)
