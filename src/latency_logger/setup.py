from setuptools import find_packages, setup

package_name = 'latency_logger'

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
    maintainer='user',
    maintainer_email='vfspurdue@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'data_logger = latency_logger.data_logger:main',
            'jetson_logger = latency_logger.jetson_logger:main',
            'obstacle_logger = latency_logger.obstacle_logger:main',
            'monitor_launcher = latency_logger.monitor_launcher:main',
        ],
    },
)
