'''
    This module contains the base classes Post, OP and Reply.
'''
import time

class NoImplementedError(Exception):
    '''This is a way to implement an abstract class.
    '''
    pass

class Post:
    '''The base class for posts.
    '''
    def __init__(self,_id,ip,board,content,image=None,name='Anonymous',option=None):
        self._id = _id
        self._ip = ip
        self._board = board
        self._time = int(time.time())
        self._timestamp = time.localtime()
        self.content = content
        self.option = option
        self.image = image
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def ip(self):
        return self._ip

    @property
    def time(self):
        return self._time

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def name(self):
        return self._name

    @property
    def board(self):
        return self._board

    def update_time(self):
        self._timestamp = time.localtime()
        self._time = int(time.time())
    
    def move(self):
        raise NoImplementedError('You must to implement your own way to move posts')

    def save(self):
        raise NoImplementedError('You must to implement your own way to save posts')

    def delete(self):
        raise NoImplementedError('You must to implement your own way to delete posts')

class OP(Post):
    '''Original Poster class class..
    '''
    def __init__(self,_id,ip,board,content,image=None,name='Anonymous',title='',option=None):
        super().__init__(_id,ip,board,content,image,name,option)
        self.title=title
        self._replys = []

    @property
    def replys(self):
        return self._replys

class Reply(Post):
    '''Reply class
    '''
    def __init__(self,_id,ip,board,op_id,content,image=None,name='Anonymous',option=None):
        super().__init__(_id,ip,board,content,image,name,option)
        self._op = op_id

    @property
    def op(self):
        return self._op

