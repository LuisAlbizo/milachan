from flask import Flask, request, render_template, send_file, jsonify
import time
from hashlib import sha256 as sha
import gevent
from gevent import Greenlet
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO, emit, send
from milachan import managers

mongom = managers.MongoManager
app = Flask(__name__)
app.secret_key = 'milachan'
csrf = CSRFProtect(app)
manager = mongom.Manager('imageboard')
io = SocketIO(app)

#Helpers

def ip_to_sha(ip):
    return sha(ip.encode()).hexdigest()

#Handlers 

def filter(message):
    return len(message)<512 and 'laim' not in message.lower()

@manager.handler
def simplehandler(post):
    data = post['data']
    gevent.sleep(2)
    board = eval('manager.db.'+data['board'])
    g = Greenlet(board.find_one,{'queue':True},{'list':True})
    g.start()
    q = g.get()
    if not(q):
        q=[]
    else:
        q=q['list']
    if post['request'] == 'OP':
        g = Greenlet(mongom.makeID,board)
        g.start()
        op = mongom.OP(
            manager.db,
            _id=g.get(),
            **data
        )
        if filter(op.content):
            g = gevent.spawn(op.save)
            g.start()
            g.get()
            q.insert(0,op.id)
            g = gevent.spawn(board.find_one_and_update,{'queue':True},{'$set':{'list':q}},upsert=True)
            g.start()
            g.get()
            response = {'status':True}
        else:
            response = {'status':False}
        response ['data'] = data
        response ['type'] = post['request']
        response ['data'] ['ip'] = ip_to_sha(data['ip'])
        io.emit('newPost',response,namespace='/boarding')
    elif post['request'] == 'Reply':
        pass
    elif post['request'] == 'DeleteOP':
        pass
    elif post['request'] == 'DeleteReply':
        pass
    elif post['request'] == 'UpdateOP':
        pass
    elif post['request'] == 'UpdateReply':
        pass

manager.add_queue('cola',2,simplehandler)
manager.start_all()

#Routes
@app.route('/favicon.ico')
def icon():
    return send_file('static/favicon.ico',attachment_filename='favicon.ico')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/thread/<board>/<int:tid>')
@app.route('/thread/<board>/<int:tid>/')
def thread(board,tid):
    thread = {'board':board, 'id':tid}
    return render_template('thread.html',thread = thread)

@app.route('/<boardname>')
@app.route('/<boardname>/')
def board(boardname):
    if manager.exist_board(boardname):
        visibles = ' / '.join(['<a href="/%s/">%s</a>' % (b['url'],b['url']) 
            for b in manager.db.boards.find({'visible':True})])
        board = manager.get_board(boardname)
        board_col = eval('manager.db.'+boardname)
        q = board_col.find_one({'queue':True},{'list':True})
        if not(q):
            q=[]
        else:
            q=q['list']
        return render_template(
            'board.html',
            board = board,
            visibles = visibles,
            sha = ip_to_sha(request.remote_addr),
            q = q,
            db = manager.db,
            OP = mongom.OP
        )
    else:
        return '<h1>Board not found</h1>'

@app.route('/<board>/post', methods=['POST'])
def post(board):
    data = request.form.to_dict()
    print(data)
    print(request.form)
    data.pop ('csrf_token')
    data ['ip'] = request.remote_addr
    data ['board'] = board
    try:
        manager.put({'data':data,'request':'OP'},'cola')
        resp = {'error':False}
    except:
        resp = {'error':True}
    return jsonify(resp)

#WebSockets
def post_notify(post):
    post = post

if __name__ == '__main__':
    io.run(app,host='0.0.0.0',port=5000)

