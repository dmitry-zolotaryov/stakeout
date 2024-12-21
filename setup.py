from setuptools import setup, find_packages

setup(
  name='stakeout',
  version='1.0.2',
  packages=find_packages(),
  entry_points={
    'console_scripts': [
      'stakeout=stakeout.main:run'
    ]
  }
)
