import sys
from tkinter import *
from tkinter import messagebox
from flask import Flask
from threading import Thread

import time
import requests

app = Flask(__name__)

tk = Tk()
app_running = True

player_order = 0
player_num = 0

port = 5000

size_canvas_x = 600
size_canvas_y = 600
s_x = s_y = 10
step_x = size_canvas_x // s_x
step_y = size_canvas_y // s_y
size_canvas_x = step_x * s_x
size_canvas_y = step_y * s_y

menu_x = 360


def on_closing():
    global app_running
    if messagebox.askokcancel("Выход из игры", "Хотите выйти из игры?"):
        app_running = False
        tk.destroy()
        sys.exit()


tk.protocol("WM_DELETE_WINDOW", on_closing)
tk.title("Игра Морской Бой")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
canvas = Canvas(tk, width=size_canvas_x*2 + menu_x, height=size_canvas_y, bd=0, highlightthickness=0)
canvas.create_rectangle(0, 0, size_canvas_x, size_canvas_y, fill="white")
canvas.create_rectangle(0, 0, size_canvas_x + size_canvas_x + menu_x, size_canvas_y, fill="white")
canvas.pack()
tk.update()


def attack_cell(event):
    global player_order
    if player_order == player_num:
        mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx() - size_canvas_x - menu_x
        mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
        mouse_x = int((mouse_x) / 60)
        mouse_y = int(mouse_y / 60)
        if mouse_x >= 0:
            print(mouse_x, mouse_y)
            send_attack(str(mouse_x)+str(mouse_y))
            player_order = 1 - player_order


canvas.bind("<Button-1>", attack_cell)


def draw_table(x):
    for i in range(0, s_x + 1):
        canvas.create_line(step_x * i + (size_canvas_x + menu_x)*x, 0, step_x * i + (size_canvas_x + menu_x)*x, size_canvas_y)
    for i in range(0, s_y + 1):
        canvas.create_line((size_canvas_x + menu_x)*x, step_y * i, size_canvas_x + (size_canvas_x + menu_x)*x, step_y * i)


draw_table(0)
draw_table(1)


def button_show_enemy():
    print("Корабль4:", ships[0].posx/60, ships[0].posy/60)
    print("Корабль3-1:", ships[1].posx/60, ships[1].posy/60)



def button_begin():
    for i in ships:
        i.fixship()
    s = ''
    for i in range(s_y):
        for j in range(s_x):
            s = s + str(table[i][j])
            print(table[i][j], end=' ')
        print()
    send_table(s)


def button_connect():
    th = Thread(target=connect)
    th.start()


b0 = Button(tk, text="Показать координаты кораблей", command=button_show_enemy)
b0.place(x=size_canvas_x + 20, y=30)

b1 = Button(tk, text="Готов!", command=button_begin)
b1.place(x=size_canvas_x + 20, y=70)

b2 = Button(tk, text="Подключиться!", command=button_connect)
b2.place(x=size_canvas_x + 80, y=70)


def fill_cell(x, y):
    canvas.create_rectangle(x*60, y*60, x*60 + 60, y*60 + 60, fill="red")


table = [[0 for i in range(s_x)] for j in range(s_y)]


class ship():
    rotation = 0

    def __init__(self, size, posx, posy):

        self.posx = posx
        self.posy = posy
        self.size = size
        self.sh_canvas = Canvas(tk, width=60, height=60 * size, bg="red", borderwidth=0)
        self.sh_canvas.place(x=posx, y=posy, anchor=NW)
        def moveship(event):
            mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
            mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
            if (mouse_x) % 60 != 0:
                mouse_x = round((mouse_x - 30) / 60) * 60
            if mouse_y % 60 != 0:
                mouse_y = round(mouse_y / 60) * 60
            if mouse_x < 0:
                mouse_x = 0
            if mouse_y < 0:
                mouse_y = 0
            if self.rotation == 0:
                if mouse_x + 60 > size_canvas_x:
                    mouse_x = size_canvas_x - 60
                if mouse_y + 60 * self.size > size_canvas_y:
                    mouse_y = size_canvas_y - 60 * self.size
            else:
                if mouse_x + 60 * self.size > size_canvas_x:
                    mouse_x = size_canvas_x - 60 * self.size
                if mouse_y + 60 > size_canvas_y:
                    mouse_y = size_canvas_y - 60
            self.posx = mouse_x
            self.posy = mouse_y
            event.widget.place(x=mouse_x, y=mouse_y, anchor=NW)
        self.sh_canvas.bind("<B1-Motion>", moveship)

        def rotate_ship(event):
            if self.rotation == 0:
                event.widget.config(width=self.size*60, height=60)
                if self.posx + 60 * self.size > size_canvas_x:
                    self.posx = size_canvas_x - 60 * self.size
                    event.widget.place(x=self.posx, y=self.posy, anchor=NW)
                self.rotation = 1
            else:
                event.widget.config(width=60, height=size*60)
                if self.posy + 60 * self.size > size_canvas_y:
                    self.posy = size_canvas_y - 60 * self.size
                    event.widget.place(x=self.posx, y=self.posy, anchor=NW)
                self.rotation = 0
        self.sh_canvas.bind("<Button-3>",rotate_ship)

    def fixship(self):
        self.sh_canvas.destroy()
        for i in range(self.size):
            if self.rotation == 0:
                table[int(self.posy/60)+i][int(self.posx/60)] = 1
                fill_cell(int(self.posx/60), int(self.posy/60) + i)
            else:
                table[int(self.posy / 60)][int(self.posx / 60)+i] = 1
                fill_cell(int(self.posx/60) + i, int(self.posy/60))

    def recreate(self):
        self.sh_canvas = Canvas(tk, width=60, height=60 * self.size, bg="red", borderwidth=0)
        self.sh_canvas.place(x=self.posx, y=self.posy, anchor=NW)

        def moveship(event):
            mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
            mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
            if (mouse_x) % 60 != 0:
                mouse_x = round((mouse_x - 30) / 60) * 60
            if mouse_y % 60 != 0:
                mouse_y = round(mouse_y / 60) * 60
            if mouse_x < 0:
                mouse_x = 0
            if mouse_y < 0:
                mouse_y = 0
            self.posx = mouse_x
            self.posy = mouse_y
            event.widget.place(x=mouse_x, y=mouse_y, anchor=NW)

        self.sh_canvas.bind("<B1-Motion>", moveship)

        def rotate_ship(event):
            if self.rotation == 0:
                event.widget.config(width=self.size * 60, height=60)
                self.rotation = 1
            else:
                event.widget.config(width=60, height=self.size * 60)
                self.rotation = 0

        self.sh_canvas.bind("<Button-3>", rotate_ship)


def restartgame():
    for i in ships:
        i.recreate()


ships = []


def send_attack(arg):
    req = requests.get('http://localhost:5000/attack/' + str(arg) + str(port))
    print(req.text)
    x = int(arg[0])
    y = int(arg[1])
    if req.text == 'n':
        fill_cell_circle(x + 16, y)
    else:
        fill_cell_x(x+16, y)


def fill_cell_circle(x, y):
    canvas.create_oval(x*60, y*60, x*60 + 60, y*60 + 60, fill="blue")


def fill_cell_x(x, y):
    canvas.create_line(x*60, y*60, x*60 + 60, y*60 + 60, fill="blue", width=10)
    canvas.create_line(x * 60, y * 60 + 60, x * 60 + 60, y * 60, fill="blue", width=10)


def send_table(arg):
    req = requests.get('http://localhost:5000/table/' + str(arg) + str(port))
    print(req.text)


@app.route('/enemy_attack/<arg>')
def enemy_attack(arg):
    global player_order
    x = int(arg[0])
    y = int(arg[1])
    r = arg[2]
    if r == 'y':
        table[x][y] = 2
    else:
        table[x][y] = 3
    player_order = 1 - player_order
    return 'ok'


def connect():
    req = requests.get('http://localhost:5000/connect')
    k = int(req.text[7:])
    global port, player_num
    port = k
    print(k)
    print(req.text[:7])
    if req.text[:7]=='player1':
        player_num = 0
    else:
        player_num = 1
    app.run('127.0.0.1', port=req.text[7:])


if __name__ == '__main__':

    ships.append(ship(4, 810, 100))
    ships.append(ship(3, 720, 100))
    ships.append(ship(3, 630, 100))
    ships.append(ship(2, 630, 300))
    ships.append(ship(2, 720, 300))
    ships.append(ship(2, 810, 360))
    ships.append(ship(1, 630, 440))
    ships.append(ship(1, 720, 440))
    ships.append(ship(1, 630, 525))
    ships.append(ship(1, 720, 525))

while app_running:
    if app_running:
        tk.update_idletasks()
        tk.update()
        for i in range(10):
            for j in range(10):
                if table[i][j] == 2:
                    fill_cell_x(i, j)
                    table[i][j] = 4
                if table[i][j] == 3:
                    fill_cell_circle(i, j)
                    table[i][j] = 5
    time.sleep(0.005)
