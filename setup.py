from setuptools import setup

setup(
   name='Unisweep',
   version='1.0',
   description='Automation software for acquiring and monitoring data in a routine way.',
   author='Mikhail Kravtsov',
   author_email='mishanya319@gmail.com',
   packages=['devices', 'config', 'mapper', 'addons'],  #same as name
   install_requires=[
      'matplotlib',
      'pyvisa-py',
      'pandas',
      'numpy',
      'scipy',
      'pyserial',
      'IPy',
      'imageio',
      'pymeasure',
      'psutil',
      'zeroconf',
      'msl-equipment @ git+https://github.com/MSLNZ/msl-equipment.git'
      ]
)