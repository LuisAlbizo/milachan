from setuptools import setup
from os import path

setup(
  name = 'milachan',
  packages = ['milachan'],
  version = '0.3.2',
  description = 'A minimalistic framework for creating simple ImageBoards',
  author = 'Luis Albizo',
  author_email = 'albizo.luis@gmail.com',
  url = 'https://github.com/LuisAlbizo/milachan',
  keywords = ['imageboard', 'framework', 'chan','backend','database'],
  license = 'Creative Commons Attribution-ShareAlike 4.0 International License',
  setup_cfg = True,
  classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: Other/Proprietary License ',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)

