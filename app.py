from flask import Flask, request, jsonify, render_template
from datetime import datetime
from qvm import vm
from qvm.vm import isolate_qubit
import program
import re
import requests

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/compiler')
def compiler():
    return render_template('compiler.html')

@app.route('/qpl')
def qpl():
    return render_template('qpl.html')

@app.route('/vm')
def vm():
    return render_template('vm.html')

@app.route('/tic-tac-toe')
def tic_tac_toe():
    return render_template('tic-tac-toe.html')


@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    content = request.json
    print (content['mytext'])
    p = content['mytext']
    wvf, msg = program.run(p)
    return jsonify({"results" : msg})


@app.route('/move', methods=['POST'])
def move():
    post = request.get_json()

    game = Game()
    game.board = post.get('board')
    game.player = post.get('player')
    game.computer = post.get('computer')

    # Check if player won
    if game.has_won(game.player):
        return jsonify(tied = False, computer_wins = False, player_wins = True, board = game.board)
    elif game.is_board_full():
        return jsonify(tied = True, computer_wins = False, player_wins = False, board = game.board)

    # Calculate computer move
    computer_move = game.calculate_move()

    # Make the next move
    game.make_computer_move(computer_move['row'], computer_move['col'])

    # Check if computer won
    if game.has_won(game.computer):
        return jsonify(computer_row = computer_move['row'], computer_col = computer_move['col'],
                       computer_wins = True, player_wins = False, tied=False, board = game.board)
    # Check if game is over
    elif game.is_board_full():
        return jsonify(computer_row = computer_move['row'], computer_col = computer_move['col'],
                       computer_wins = False, player_wins = False, tied=True, board=game.board)

    # Game still going
    return jsonify(computer_row = computer_move['row'], computer_col = computer_move['col'],
                   computer_wins = False, player_wins = False, board = game.board)


@app.route('/api/teleportsend', methods=['get', 'post'])
def teleportsend():
    sendit = request.form.get('sendit')
    if not sendit is None:
        url = request.url_root + 'api/teleportrecieve'
        p = """QUBITS 3
H 1
CNOT 1 2
CNOT 0 1
H 0
MEASURE 0
MEASURE 1"""
    wvf, msg = program.run(p)

    # Very hacky way of doing this... @TODO make this better
    m = re.findall('====== MEASURE qubit (\d) : (\d)', msg)
    if m[0][0] == '0':
        q0 = int(m[0][1])
        q1 = int(m[1][1])
    else :
        q1 = int(m[0][1])
        q0 = int(m[1][1])
    print(url)
    res = requests.post(url, json={
        "q0": q0,
        "q1" : q1
    })

    if res.ok:
        j = res.json()
        p = j['program']
        p_split = p.splitlines()
        p_str = "<ol>"
        for i in p_split:
            p_str += '<li><samp class="code-block">' + i + '</li>'
        p_str += '</ol>'
        j['program'] = p_str
        j['a'] = f"Qubit 0 : {q0}<br />Qubit 1 : {q1}"
        return (jsonify(j))



@app.route('/api/teleportrecieve', methods=['get', 'post'])
def teleportrecieve():
    content = request.json
    q0 = content["q0"]
    q1 = content["q1"]

    p = """QUBITS 4
MEASURE 0
MEASURE 1
H 2
CNOT 2 3
CLASSICAL 1 1 1
X 3
CLASSICAL 0 1 1
Z 3"""

    p_list = p.splitlines()
    if q0 == 1:
        p_list.insert(1, "X 0")
    if q1 == 1:
        p_list.insert(1, "X 1")

    p = "\n".join(p_list)
    wvf, msg = program.run(p)

    msg = isolate_qubit(wvf, 3)
    return jsonify({"program" : p, 'wvf' : msg})

@app.route('/teleportation', methods=['GET', 'POST'])
def teleporation():
    return render_template('teleportation.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True)
