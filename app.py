from flask import Flask, request, render_template
from milachan import MongoManager
from milachan.pqueue import PostQueue as Queue, PostHandler as Handler

app = Flask(__name__)
manager = MongoManager('imageboard')

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
    return render_template('board.html',boardname = boardname)

app.run(debug=True)

