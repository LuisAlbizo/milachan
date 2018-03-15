'''
    ImageBoard Manager for MongoDB implemented with pymongo
'''

from pymongo import MongoClient, MongoReplicaSetClient
from .squema import OP,Reply
from .pqueue import PostQueue as Queue, PostHandler as Handler

def makeID(board):
    '''
        Function to make unique id's in a board.

        :Parameters:
            `board` : a pymongo.collection.Collection instance

        Returns an integer >= 1
    '''
    board.find_one_and_update({'_id':'count'}, {'$inc':{'count':1}}, upsert=True)
    return board.find_one({'_id':'count'}).get('count')

class OP(OP):
    '''
        Original Poster class

        :Parameters:
            `db`        a `pymongo.database.Database` instance
            `_id`       an integer id for the post
            `ip`        the IP addres of the poster
            `board`     the url of the board
            `content`   content of the post 
            `image`     the url of the image (optional, default None)
            `name`      the name of the poster (optional, default is 'Anonymous')
            'title'     a title for the post (optional, default '')
    '''
    def get(db,board,_id):
        '''
        'Static' method of OP
        Not need to instance the class to use.

        :Parameters:
            `db`    a pymongo.database.Database instance
            `board` the url of the board
            `_id`   the unique id of the post
        
        Returns a OP instance if exists
        '''
        match = db.get_collection(board+'.'+str(_id)).find_one({'OP':True},{'OP':False,'time':False,'timestamp':False})
        if match:
            return OP(db,**match)

    def __init__(self,db,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__db = db

    @property
    def replys(self):
        thread = self.__db.get_collection(self.board+'.'+str(self.id))
        for r in thread.find({'reply':True},{'_id':True}):
            yield self.get_reply(r['_id'])

    @property
    def replys_id(self):
        return [r['_id'] for r in
                self.__db.get_collection(self.board+'.'+str(self.id)).find(
                    {'reply':True},{'_id':True})]
    
    @property
    def info(self):
        info = {
            'OP' : True,
            '_id' : self.id,
            'ip' : self.ip,
            'time' : self.time,
            'timestamp' : self.timestamp,
            'board' : self.board,
            'content' : self.content,
            'name' : self.name
        }
        if self.title:
            info['title'] = self.title
        if self.image:
            info['image'] = self.image
        return info

    def get_reply(self,_id):
        '''
        :Parameters:
            `_id` a unique _id of the reply

        Return a Reply instance if the reply exists
        '''
        match = self.__db.get_collection(self.board+'.'+str(self.id)).find_one({'_id':_id},{'reply':False,'time':False,'timestamp':False})
        if match: 
            return Reply(db,**match)

    def save(self):
        '''
        Insert or update if exists in database
        '''
        thread = self.__db.get_collection(self.board+'.'+str(self.id))
        thread.find_one_and_update({'_id':self.id}, {'$set':self.info}, upsert=True)
    
    def move(self,board,new_id,map_id):
        '''
        Move OP post and his replys to another board.
        :Parameters:
            `board`     the url of board to move the post, must not be the actual board
            `new_id`    a new _id to identify the post in the new board
            `map_id`    a function to map all the reply's id's

        Return the new id of the post
        '''
        assert self.board != board, "can't move a thread to his previous board"
        replys = zip(list(self.replys),map(map_id,self.replys_id))
        self.delete()
        info = {
            'moved' : True,
            '_id' : self.id,
            'new_board' : board,
            'new_id' : new_id
        }
        self.__db.get_collection(self.board).insert_one(info)
        self.__board = board
        self.__id = new_id
        for reply in replys:
            reply[0].move(board=self.board,op=self.id,new_id=reply[1])
        self.save()
        return self.id

    def delete(self):
        '''
        Delete the post with all his replys
        '''
        self.__db.get_collection(self.board+'.'+str(self.id)).drop()
        info = {
            'deleted' : True,
            '_id' : self.id
        }
        self.__db.get_collection(self.board).insert_one(info)

class Reply(Reply):
    '''
        Reply class

        :Parameters:
            `db`        a `pymongo.database.Database` instance
            `_id`       an integer id for the post
            `ip`        the IP addres of the poster
            `board`     the url of the board
            `op_id`     the OP._id of the OP for this reply
            `content`   content of the post 
            `image`     the url of the image (optional, default None)
            `name`      the name of the poster (optional, default is 'Anonymous')
    '''
    def __init__(self,db,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__db=db

    def get(db,board,_id):
        '''
        'Static' method of Reply
        Not need to instance the class to use.

        :Parameters:
            `db`    a pymongo.database.Database instance
            `board` the url of the board
            `_id`   the unique id of the post
        
        Returns a Reply instance if exists
        '''
        for thread in db.list_collections():
            match = db.get_collection(thread['name']).find_one({'_id':_id,'reply':True},{'reply':False,'time':False,'timestamp':False})
            if match:
                return Reply(db,**match)

    @property
    def info(self):
        info = {
            'reply' : True,
            '_id' : self.id,
            'ip' : self.ip,
            'time' : self.time,
            'timestamp' : self.timestamp,
            'board' : self.board,
            'op' : self.op.id,
            'content' : self.content,
            'name' : self.name
        }
        if self.image:
            info['image'] = self.image
        return info

    def save(self):
        '''
        Insert or update if exists in database
        '''
        thread = self.__db.get_collection(self.board+'.'+str(self.op))
        thread.find_one_and_update({'_id':self.id}, {'$set':self.info}, upsert=True)

    def move(self,board,op_id,new_id):
        '''
        Move Reply post to another thread.
        :Parameters:
            `board`     the url of board to move the post, must not be the actual board
            `op_id`     the id of the OP, must exists
            `new_id`    a new _id to identify the post in the new thread

        Return the new id of the post
        '''
        assert self.board != board or self.op != op_id, "can't move a reply to his previous thread"
        self.delete()
        self.__op = op_id
        self.__board = board
        self.__id = new_id
        self.save()

    def delete(self):
        '''
        Deletes the entire thread
        '''
        thread = self.__db.get_collection(self.board+'.'+str(self.op))
        #thread.delete_one({'_id':self.id})
        thread.drop()
        info = {
            'deleted' : True,
            '_id' : self.id
        }
        self.__db.get_collection(self.board+'.'+str(self.op)).insert_one(info)

class Manager:
    '''
    A class to manage the database/squema part of an imageboard and the PostQueue.

    :Parameters: (optional)
        `dbname`    the name of the database (default 'imageboard')
        `host`      the hostname of the mongo database (default '127.0.0.1')
        `port`      the port of the mongo database (default 27017)
    '''
    def __init__(self,dbname='imageboard',host='127.0.0.1',port=27017):
        self.__db = MongoClient(host=host, port=port).get_database(dbname)
        self.__handlers = dict()
        self.__queues = dict()

    @property
    def db(self):
        return self.__db

    def handler(self,afunc):
        '''
        Decorator for post handlers.

        Pass a handler function to handle posts.

        Example:
        >>> @manager.handler
        ... def simple_handler(post):
        ...     #do something with post
        ... 
        '''
        self.__handlers[afunc.__name__] = Handler()(afunc)
        return afunc.__name__

    def add_queue(self,name,ratio,handler_name):
        '''
        Add a PostQueue.

        :Parameters:
            `name`      the name of the queue
            `ratio`     the ratio limit of the queue
            `handler_name`      the name of the handler function
        '''
        self.__queues[name] = Queue(ratio,self.__handlers[handler_name])

    def start_queue(self,name):
        '''
        Start a queue by name.
        '''
        self.__queues[name].start()

    def stop_queue(self,name):
        '''
        Stop a queue by name.
        '''
        self.__queues[name].stop()

    def start_all(self):
        '''
        Start all queue's.

        Raises HandleError
        '''
        for q in self.__queues.values():
            q.start()

    def stop_all(self):
        '''
        Stop all queue's.
        '''
        for q in self.__queues.values():
            q.stop()

    def put(self,post,qname):
        '''
        Put post in queue by qname.

        Raises EnqueueError.
        '''
        self.__queues[qname].put(post)

    def create_board(self,url,name,description,**kwargs):
        '''
        Create a board.

        :Parameters:
            `url`   the shortname of the board (this is gonna be the name of the collection)
            `name`  the fullname of the board
            `description`   a short description for the board
            **kwargs for more info if it's necessary
        
        Returns True if the boards not exist before, else returns False.
        '''
        if not(self.exist_board(url)):
            board = {
                'board' : True,
                'url' : url,
                'name' : name,
                'description' : description
            }
            [board.update([(k,kwargs[k])]) for k in kwargs]
            self.__db.get_collection(url).insert_one(board)
            self.__db.boards.insert_one(board)
            return True
        else:
            return False

    def get_board(self,url):
        return self.__db.get_collection(url).find_one({'board':True})

    def delete_board(self,url):
        '''
        Deletes a board.

        :Parameters:
            `url`   the shortname of the board (the name of the collection)
        '''
        self.__db.get_collection(url).drop()

    def exist_board(self,url):
        '''
        Checks if a board exists.

        :Parameters:
            `url`   the shortname of the board (the name of the collection)

        Return True if exists, else False
        '''
        return (url in [c['name'] for c in self.__db.list_collections()])

    def exist_thread(self,board,_id):
        '''
        Checks if a thread exists.

        :Parameters:
            `board`     the shortname of the board (the name of the collection)
            `_id`       the id of the OP

        Return True if exists, else False
        '''
        if not(OP.get(self.__db,board,_id)): 
            return False
        else:
            return True

    def get_thread(self,board,_id):
        '''
        Get a thread basic information.

        :Parameters:
            `board`     the shortname of the board (the name of the collection)
            `_id`       the id of the OP
        '''
        op = OP.get(self.__db,board,_id)
        if not(op): 
            return
        return {
            'op' : op.info,
            'replys_id' : op.replys_id,
            'replys' : op.replys
        }





