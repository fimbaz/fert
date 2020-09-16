from setuptools import setup
setup(name='tasmonitor',
  version='0.1',
  description='Monitor Local Tasmota Modules',
  author='Matthew Baker',
  author_email='fimbaz@gmail.com',
  license='MIT',
  packages=['tasmonitor'],
  entry_points = {
    'console_scripts': ['tasmonitor=tasmonitor.tasmonitor:main'],

    },
      install_requires = ['requests','paho-mqtt'],
  zip_safe=False)
