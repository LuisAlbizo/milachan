'''
Module for handle posts.
'''
import threading

class EnqueueError(Exception):
    pass

class PostQueue:
    '''
    A queue to handle posts.
    '''
    def __init__(self,ratiolimit,handle):
        self.__posts = []
        self.ratio = int(ratiolimit)
        assert '__call__' in dir(handle), 'handle must be callable'
        self.__handle = handle
        self.running = False

    def put(self,post):
        '''
        Add a post at the end of the queue
        '''
        if len(self.__posts) >= self.ratio:
            raise EnqueError('ratio limit reached')
        else:
            self.__posts.append(post)

    def get(self):
        '''
        Get the first element of the queue
        '''
        return self.__posts.pop(0)

    @property
    def size(self):
        return len(self.__posts)

    def start(self):
        '''
        Start in a new thread the post handler
        '''
        if self.running:
            raise EnqueueError("Handle is already running")
        self.running = True
        return threading.Thread(target=self.__handle, args=(self,), daemon=True).start()

    def stop(self):
        '''
        Stop executing the handler
        '''
        self.running = False

class PostHandler:
    '''
    Decorator to handle posts.

    Usage:
        >>> @PostHandler()
        ... def handler(post):
        ...    #do something
        ... 
        >>> queue = PostQueue(1,handler)
    '''
    def __init__(self):
        pass

    def __call__(self,handler):
        def new_handler(queue):
            while queue.running:
                if queue.size:
                    handler(queue.get())
        return new_handler

