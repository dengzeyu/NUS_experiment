from setuptools import setup

setup(
   name='Unisweep',
   version='1.0',
   description='Automation software for acquiring and monitoring data in a routine way.',
   author='Mikhail Kravtsov',
   author_email='mishanya319@gmail.com',
   packages=['devices', 'config', 'mapper', 'addons'],  #same as name
   install_requires=['os', 'sys', 'json', 'csv', 'threading', 'tkinter', 'matplotlib', 'pyvisa-py'
                     'time', 'datetime', 'pandas', 'numpy', 'scipy', 'glob', 'serial', 'IPy', 'pillow',
                     'itertools', 'pymeasure',
                     'git+ssh://git@github.com/MSLNZ/msl-equipment/releases/download/v0.1.0/msl_equipment-0.1.0-py2.py3-none-any.whl#egg=msl-equipment'],
)