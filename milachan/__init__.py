__author__ = 'Luis Albizo'
__license__ = 'Creative Commons'
__email__ = 'albizo.luis@gmail.com'
__date__ = '26 feb 2018'
__version__ = '0.1.0'

import milachan.squema
import milachan.pqueue

class managers:
    @property
    def MongoManager(_):
        __import__('milachan.manager-pymongo')
        return getattr(milachan,'manager-pymongo')

managers = managers()

