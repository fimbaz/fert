from setuptools import setup
setup(name='co2sens',
  version='0.1',
  description='Report CO2 level',
  author='Matthew Baker',
  author_email='fimbaz@gmail.com',
  license='MIT',
  packages=['co2sens'],
  entry_points = {
    'console_scripts': ['co2sens=co2sens.co2detector:main'],

    },
      install_requires = ['paho-mqtt','requests'],
  zip_safe=False)
