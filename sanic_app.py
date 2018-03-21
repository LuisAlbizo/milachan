import time, async, asyncio
from hashlib import sha256 as sha
from werkzeug.utils import secure_filename
from milachan import managers
from sanic import Sanic, response
from jinja2 import Template, Environment, FileSystemLoader
from socketio import AsyncServer
mongom = managers.MongoManager

#Declarations

manager = mongom.Manager('imageboard') #IB Manager
#   App
app = Sanic()
app.secret_key = 'milachan'
app.static('/static', './static')
UPLOAD_FOLDER = 'static/images/res/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','webm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
#   SocketIO
io = AsyncServer(async_mode='sanic')
io.attach(app)

#Helpers

jsonify = response.json
send_file = response.file
loader = FileSystemLoader('./templates')

def to_dict(form):
    new_dict = {}
    for k in form:
        new_dict[k] = form[k][0]
    return new_dict

def render_template(filename,**kwargs):
    with open('templates/'+filename,'r') as f:
        tpl = Environment(loader=loader).from_string(f.read())
        f.close()
        return response.html(tpl.render(**kwargs))

def save(file,path):
    with open(path,'wb') as f:
        length = f.write(file.body)
        f.close()
    return length

def ip_to_sha(ip):
    return sha(ip.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

#Handlers 

def filter(message):
    return len(message)<1024

@manager.handler
async def simplehandler(post):
    data = post['data']
    board = eval('manager.db.'+data['board'])
    q = board.find_one({'queue':True},{'list':True})
    if not(q):
        q=[]
    else:
        q=q['list']
    if post['request'] == 'OP':
        op = mongom.OP(
            manager.db,
            _id=mongom.makeID(board),
            **data
        )
        if filter(op.content):
            op.save()
            q.insert(0,op.id)
            board.find_one_and_update({'queue':True},{'$set':{'list':q}},upsert=True)
            response = {'status':True}
        else:
            response = {'status':False}
        response ['data'] = op.info
        response ['type'] = post['request']
        response ['data'] ['ip'] = ip_to_sha(data['ip'])
        await io.emit('newPost',response,namespace='/boarding')
        print('emites')
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
def icon(request):
    return send_file('static/favicon.ico')

@app.route('/')
async def index(request):
    return render_template('index.html')

@app.route('/admin/')
async def admin(request):
    return render_template('admin.html')

@app.route('/thread/<board:[a-z]{1,4}>/<tid:int>/')
async def thread(request,board,tid):
    thread = {'board':board, 'id': tid}
    return render_template('thread.html',thread = thread)

@app.route('/<boardname:[a-z]{1,4}>/')
async def board(request,boardname):
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
        return response.html('<h1>Board not found</h1>')

@app.route('/<board:[a-z]{1,4}>/post', methods=['POST'])
async def post(request,board):
    data = to_dict(request.form)
    data ['ip'] = request.remote_addr
    data ['board'] = board
    if 'image' not in request.files:
        resp = {'error':True,'type':'No file part'}
        return jsonify(resp)
    file = request.files['image'][0]
    if file.name == '':
        resp = {'error':True,'type':'No selected file'}
        return jsonify(resp)
    if allowed_file(file.name):
        filename = secure_filename(file.name)
        ext = '.'+filename.split('.')[-1]
        img_id = mongom.makeID(manager.db.images)
        fileurl = str(img_id)+ext
        data ['image'] = {
            'url':'/static/images/res/'+fileurl,
            'name':filename,
            'size':save(file,app.config['UPLOAD_FOLDER']+fileurl)
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
    app.run(host='0.0.0.0',port=5000,debug=True)

