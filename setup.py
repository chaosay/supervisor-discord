from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
except (IOError, OSError):
    README = ''

setup(
  name = 'supervisor-discord',
  packages = ['supervisor-discord'],
  version = '1.0.0',
  license='GNU GPL v3',
  description = 'Connect supervisor to discord via webhooks',
  long_description=README,
  long_description_content_type='text/markdown',
  author = 'chaos_a',
  url = 'https://github.com/chaosay/supervisor-discord',
  download_url = 'https://github.com/chaosay/supervisor-discord/archive/1.0.tar.gz',    # I explain this later on
  keywords = ['supervisor', 'discord', 'alerts'],
  scripts=['supervisor-discord/alertHandler.py'],
  install_requires=[
          'pyYaml',
          'ratelimit',
          'requests',
          'rich'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: System Administrators',
    'Topic :: System :: Boot',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.7',
  ],
)