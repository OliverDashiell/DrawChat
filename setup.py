#!/usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version = '0.01'

setup(name='DrawChat',
      version=version,
      description="A chat app",
      long_description="""A chat app""",
      author='Oliver Dashiell Bunyan',
      author_email='oliverdashiell@gmail.com',
      packages=find_packages('src',exclude=['*tests*']),
      package_dir = {'':'src'},
      include_package_data = True, 
      exclude_package_data = { '': ['tests/*'] },
      install_requires = [
        'setuptools',
        'tornado',
        'sqlalchemy'
      ],
      entry_points = {
      'console_scripts' : [
                           'drawchat = draw_chat.rpc_server:main'
                           ]
      })