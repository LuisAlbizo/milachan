from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'),'r') as f:
    long_description = f.read()
    f.close()

setup(
  name = 'milachan',
  packages = ['milachan'],
  version = '0.1.0',
  description = 'A minimalistic framework for creating simple ImageBoards',
  long_description = long_description,
  author = 'Luis Albizo',
  author_email = 'albizo.luis@gmail.com',
  url = 'https://github.com/LuisAlbizo/milachan',
  keywords = ['imageboard', 'framework', 'chan'],
  license = 'Creative Commons',
  setup_cfg = True,
  classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: Creative Commons Attribution-ShareAlike 4.0 International License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
      ]
)

