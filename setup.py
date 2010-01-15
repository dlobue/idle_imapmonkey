from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='idle_imapmonkey',
      version=version,
      description="Monkey patches IDLE functionality into Python's imaplib",
      long_description="""\
This module adds IDLE functionality into the standard Python library imaplib. The aim of this is to add a much sought-after feature while changing as little of the existing imaplib library as possible. The fact of the matter is that there are only two Python IMAP libraries that provide IDLE; one is not free nor open-source, and the other is riddled with bugs. The goal being to retain imaplib's battle-tested code base and be interchangable with imaplib.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='imap network mail',
      author='Dominic LoBue',
      author_email='dominic.lobue@gmail.com',
      url='n/a',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
