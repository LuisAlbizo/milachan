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
    def __init__(self,_id,ip,board,content,image=None,name='Anonymous'):
        self.__id = _id
        self.__ip = ip
        self.__board = board
        self.__time = int(time.time())
        self.__timestamp = time.localtime()
        self.content = content
        self.image = image
        self.__name = name

    @property
    def id(self):
        return self.__id

    @property
    def ip(self):
        return self.__ip

    @property
    def time(self):
        return self.__time

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def name(self):
        return self.__name

    @property
    def board(self):
        return self.__board

    def update_time(self):
        self.__timestamp = time.localtime()
    
    def move(self):
        raise NoImplementedError('You must to implement your own way to move posts')

    def save(self):
        raise NoImplementedError('You must to implement your own way to save posts')

    def delete(self):
        raise NoImplementedError('You must to implement your own way to move posts')

class OP(Post):
    '''Original Poster class class..
    '''
    def __init__(self,_id,ip,board,content,image=None,name='Anonymous',title=''):
        super().__init__(_id,ip,board,content,image,name)
        self.title=title
        self.__replys = []

    @property
    def replys(self):
        return self.__replys

class Reply(Post):
    '''Reply class
    '''
    def __init__(self,_id,ip,board,op_id,content,image=None,name='Anonymous'):
        super().__init__(_id,ip,board,content,image,name)
        self.__op = op_id

    @property
    def op(self):
        return self.__op

