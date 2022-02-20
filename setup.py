from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='xyzflow',
      version='0.1',
      description='Simple but powerful python orchestration framework',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/Renneke/xyzflow',
      author='Florian Renneke',
      author_email='florianrenneke@gmail.com',
      license='Apache License Version 2.0',
      packages=['xyzflow'],
      install_requires=[
          'networkx',
          'matplotlib',
          'diskcache',
          'colorama',
          'tabulate',
          'pandas'
      ],
      entry_points = {
              'console_scripts': [
                  'xyzflow = xyzflow:main',                  
              ],              
          },
      zip_safe=False)