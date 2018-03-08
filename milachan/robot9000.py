'''
Module to implement robot9000 IRC algorithm.
'''
from hashlib import shake_128 as sha

class Nodo:
    def __init__(self,value,parent=None):
        self.__value = value
        self.__r = None
        self.__l = None
        self.parent = parent

    @property
    def value(self):
        return self.__value

    @property
    def r(self):
        return self.__r

    @property
    def l(self):
        return self.__l

    def insert(self,node):
        if node.value == self.value:
            return (False,None)
        elif node.value > self.value:
            self.__r = node
            return (True,'r')
        else:
            self.__l = node
            return (True,'l')

    def insert_r(self,node):
        self.__r = node

    def insert_l(self,node):
        self.__l = node

    def __bool__(self):
        return True

    def __len__(self):
        return 1 + (len(self.r) if self.r else 0) + (len(self.l) if self.l else 0)

    def max(self):
        return 1 + max((self.r.max() if self.r else 0),(self.l.max() if self.l else 0))

    def min(self):
        return 1 + min((self.r.min() if self.r else 0),(self.l.min() if self.l else 0))

class BTree:
    def __init__(self):
        self.node=None

    def insert(self,message):
        h = int.from_bytes(sha(message).digest(8),'little')
        if self.node==None:
            self.node = Nodo(h)
            return True
        node = self.node
        parent = self.node
        while True:
            if node==None:
                parent.insert(Nodo(h))
                return True
            elif node.value == h:
                return False
            elif h > node.value:
                parent = node
                node = node.r
            else:
                parent = node
                node = node.l

    def __bool__(self):
        return True

    def __len__(self):
       return (len(self.node) if self.node else 0) 



