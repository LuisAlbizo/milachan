'''
Module to implement robot9000 IRC algorithm.
'''
from hashlib import shake_128 as sha

class BTree:
    def __init__(self):
        self.__nodes = {}

    def insert(self,message,nbytes=8):
        h = int.from_bytes(sha(message).digest(nbytes),'little')
        e = self.__nodes.get(h,0)
        if e:
            return False
        else:
            self.__nodes[h] = 1
            return True

    def __len__(self):
        return len(self.__nodes)

    def __bool__(self):
        return True

