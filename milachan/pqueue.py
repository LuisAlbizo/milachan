'''
Module for handle posts.
'''
import threading

class EnqueueError(Exception):
    pass

class HandleError(Exception):
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

    @property
    def size(self):
        return len(self.__posts)

    def put(self,post):
        '''
        Add a post at the end of the queue
 
        Raises EnqueueError
        '''
        if self.size >= self.ratio:
            raise EnqueueError('ratio limit reached')
        else:
            self.__posts.append(post)

    def get(self):
        '''
        Get the first element of the queue
        '''
        return self.__posts.pop(0)

    def start(self):
        '''
        Start in a new thread the post handler
        
        Raises HandleError
        '''
        if self.running:
            raise HandleError("handler is already running")
        self.running = True
        threading.Thread(target=self.__handle, args=(self,), daemon=True).start()

    def stop(self):
        '''
        Stop executing the handler
        '''
        self.running = False

class PostHandler:
    '''
    Decorator to make post handler's.

    Usage:
        >>> @PostHandler()
        ... def handler(post):
        ...     #do something
        ...     pass
        ... 
        >>> queue = PostQueue(10,handler)
    '''
    def __init__(self):
        pass

    def __call__(self,handler):
        def new_handler(queue):
            while queue.running:
                if queue.size:
                    handler(queue.get())
        return new_handler

