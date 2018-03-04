from pymongo import MongoClient
from .squema import OP,Reply
from .pqueue import PostQueue as Queue, PostHandler as Handler

def makeID(board):
    board.find_one_and_update({'_id':'count'}, {'$inc':{'count':1}}, upsert=True)
    return board.find_one({'_id':'count'}).get('count')

class OP(OP):
    def get(db,board,_id):
        match = db.get_collection(board+'.'+str(_id)).find_one({'OP':True})
        if match:
            return OP(db,**match)

    def __init__(self,db,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__db = db
        self.update_replys()

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
        match = self.__db.get_collection(self.board+'.'+str(self.id)).find_one({'_id':_id})
        if match: 
            return Reply(db,**match)

    def save(self):
        thread = self.__db.get_collection(self.board+'.'+str(self.id))
        thread.find_one_and_update({'_id':self.id}, {'$set':self.info}, upsert=True)
    
    def move(self,board,new_id,map_id):
        assert self.board != board, "can't move a thread to his previous board"
        replys = zip(list(self.replys),map(map_id,self.replys_id))
        self.delete()
        info = {
            'moved' : True,
            'last_board' : self.board,
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
        self.__db.get_collection(self.board+'.'+str(self.id)).drop()

class Reply(Reply):
    def __init__(self,db,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__db=db

    def get(db,board,_id):
        for thread in db.list_collections():
            match = db.get_collection(thread['name']).find_one({'_id':_id,'reply':True})
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
        thread = self.__db.get_collection(self.board+'.'+str(self.op))
        thread.find_one_and_update({'_id':self.id}, {'$set':self.info}, upsert=True)

    def move(self,board,op,new_id):
        assert self.board != board or self.op != op, "can't move a reply to his previous thread"
        self.delete()
        self.__op = op
        self.__board = board
        self.__id 
        self.save()

    def delete(self):
        thread = self.__db.get_collection(self.board+'.'+str(self.op))
        thread.delete_one({'_id':self.id})

class Manager:
    def __init__(self,dbname,host='127.0.0.1',port=27017):
        self.__db = MongoClient(host=host, port=port).get_database(dbname)
        self.__handlers = []

    @property
    def handler(self,afunc):
        pass

    def create_board(self,url,name,description,**kwargs):
        if not(self.exist_board(url)):
            board = dict(set({
                '_id' : 0,
                'url' : url,
                'name' : name,
                'description' : description
            }).union(set(kwargs)))
            self.__db.get_collection(url).insert_one(board)
        else:
            return False
        return True

    def delete_board(self,url):
        self.__db.get_collection(url).drop()

    def exist_board(self,url):
        return (url in [c['name'] for c in self.__db.list_collections()])

    def exist_thread(self,board,_id):
        if not(OP.get(self.__db,board,_id)): 
            return False
        else:
            return True

    def get_thread(self,board,_id):
        op = OP.get(self.__db,board,_id)
        if not(op): 
            return
        return {
            'op' : op.info,
            'replys_id' : op.replys_id,
            'replys' : op.replys
        }

    def post(self,ip,board,content,image,title=None,name='Anonymous'):
        op = OP(
            self.__db, makeID(self.__db.get_collection(board)), ip, board, content, image, name,title
        )
        op.save()
        return op.id

    def reply(self,ip,board,op_id,content,image=None,name='Anonymous'):
        if not(self.exist_thread(board,op_id)):
            return
        reply = Reply(self.__db,_id,ip,board,op_id,content,image,name)
        reply.save()
        return reply.id

    def delete_reply(self,board,op_id,_id):
        try:
            op = OP.get(self.__db,board,op_id)
            reply = op.get_reply(_id)
            reply.delete()
            return True
        except:
            return False

    def delete_post(self,board,_id):
        op = OP.get(self.__db,board,op_id)
        if op:
            op.delete()
            return True
        else:
            return False

