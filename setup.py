# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='votesim',
    version='0.0.1',
    description='Voting simulation and analysis',
    long_description=readme,
    author='Christopher McComb',
    author_email='chris.c.mccomb@gmail.com',
    url='https://github.com/cmccomb/voteSim',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
