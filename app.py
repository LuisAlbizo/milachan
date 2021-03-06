from flask import Flask, request, render_template, send_file, jsonify
import time, gevent, os
from hashlib import sha256 as sha
from gevent import Greenlet
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO, emit, send
from werkzeug.utils import secure_filename
from milachan import managers
mongom = managers.MongoManager

#Declarations

manager = mongom.Manager('imageboard') #IB Manager
#   App
app = Flask(__name__)
app.secret_key = 'milachan'
csrf = CSRFProtect(app)
UPLOAD_FOLDER = 'static/images/res/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','webm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
#   SocketIO
io = SocketIO(app,async_mode='gevent')

#Helpers

def ip_to_sha(ip):
    return sha(ip.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

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
        response ['data'] = op.info
        response ['type'] = post['request']
        response ['data'] ['ip'] = ip_to_sha(data['ip'])
        print(response)
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

manager.add_queue('cola',20,simplehandler)
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
        visibles=' / '.join(
            ['<a href="/%s/">%s<span class="badge" id="%s"></span></a>' % (
                    b['url'],b['url'],b['url']
                )
            for b in manager.db.boards.find({'visible':True})
            ]
        )
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
    data.pop ('csrf_token')
    data ['ip'] = request.remote_addr
    data ['board'] = board
    if 'image' not in request.files:
        resp = {'error':True,'type':'No file part'}
        return jsonify(resp)
    file = request.files['image']
    if file.filename == '':
        resp = {'error':True,'type':'No selected file'}
        return jsonify(resp)
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = '.'+filename.split('.')[-1]
        img_id = mongom.makeID(manager.db.images)
        fileurl = str(img_id)+ext
        file.save(app.config['UPLOAD_FOLDER']+fileurl)
        data ['image'] = {
            'url':'/static/images/res/'+fileurl,
            'name':filename,
            'size':os.stat(app.config['UPLOAD_FOLDER']+fileurl).st_size
        }
        try:
            manager.put({'data':data,'request':'OP'},'cola')
            resp = {'error':False}
        except:
            resp = {'error':True,'type':'Queue is full'}
    else:
        resp = {'error':True,'type':'Not admited file'}
    return jsonify(resp)

#WebSockets
def post_notify(post):
    post = post

manager.create_board('shit','Shit','Shitpost and Testing',nsfw=True,visible=True)
manager.create_board('a','Alpha','Testing',nsfw=True,visible=True)
manager.create_board('b','Beta','Testing',nsfw=True,visible=True)
manager.create_board('c','Charlie','Testing',nsfw=True,visible=True)
manager.create_board('test','Test','Helli',nsfw=False,visible=False)

if __name__ == '__main__':
    io.run(app,host='0.0.0.0',port=5000)

