from flask import Flask

import requests

app = Flask(__name__)

client_id = 5000

port_player1 = 5000
port_player2 = 5000

player1_score = 0
player2_score = 0

num = 0

table_player1 = [[0 for i in range(10)] for j in range(10)]

table_player2 = [[0 for i in range(10)] for j in range(10)]


def string_to_table(s):
	table_res = [[0 for i in range(10)] for j in range(10)]
	for i in range(10):
		for j in range(10):
			table_res[i][j] = int(s[i*10 + j])
	return table_res


@app.route('/table/<arg>')
def table(arg):
	port = arg[100:]
	print(port)
	global table_player2
	global table_player1
	if port == str(port_player2):
		table_player2 = string_to_table(arg)
		print("table of player2")
		for i in range(10):
			for j in range(10):
				print(table_player2[i][j], end=' ')
			print()
	else:
		table_player1 = string_to_table(arg)
		print("table of player1")
		for i in range(10):
			for j in range(10):
				print(table_player1[i][j], end=' ')
			print()
	return 'ok'


@app.route('/attack/<arg>')
def attack(arg):
	port = arg[2:]
	print(port)
	global player1_score
	global player2_score
	if port == str(port_player2):
		print("player2 attacks", arg[0], arg[1])
		if table_player1[int(arg[1])][int(arg[0])] == 1:
			send_attack(port_player1, int(arg[0]), int(arg[1]), 'y')
			player2_score += 1
			if player2_score == 20:
				print("player1 wins")
			return 'y'
		else:
			send_attack(port_player1, int(arg[0]), int(arg[1]), 'n')
			return 'n'
	else:
		print("player1 attacks", arg[0], arg[1])
		if table_player2[int(arg[1])][int(arg[0])] == 1:
			send_attack(port_player2, int(arg[0]), int(arg[1]), 'y')
			player1_score += 1
			if player1_score == 20:
				print("player1 wins")
			return 'y'
		else:
			send_attack(port_player2, int(arg[0]), int(arg[1]), 'n')
			return 'n'


@app.route('/connect')
def connect():
	global client_id
	global port_player1
	global port_player2
	global num
	client_id += 1
	res = str(client_id)
	print("Client %d connected" % client_id)
	if num == 0:
		port_player1 = client_id
		num = 1
		res = 'player1' + res
		return res
	else:
		port_player2 = client_id
		num = 0
		res = 'player2' + res
		return res


def send_attack(port, x, y, r):
	arg = str(x) + str(y) + str(r)
	id = 'http://localhost:' + str(port) + '/enemy_attack/' + str(arg)
	req = requests.get(id)


def send(arg, clid):
	id = 'http://localhost:' + str(clid) + '/index/' + str(arg)
	req = requests.get(id)


if __name__ == '__main__':
	app.run()
