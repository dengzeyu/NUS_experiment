from setuptools import setup

setup(
   name='Unisweep',
   version='1.0',
   description='Automation software for acquiring and monitoring data in a routine way.',
   author='Mikhail Kravtsov',
   author_email='mishanya319@gmail.com',
   packages=['devices', 'config', 'mapper', 'addons'],  #same as name
)