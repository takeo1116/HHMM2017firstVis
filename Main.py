import sys
import tkinter
import math
import subprocess
from tkinter import *

now_number = 0

def generate_canvas(output_parsed):  #出力1回ぶんを切り取って渡す
    canvas = tkinter.Canvas(root, width=W + W_info, height=H + H_button)

    #背景
    canvas.create_rectangle(0, 0, W + W_info + 50, H + H_button + 50, fill='lightgray')
    result = [-1 for i in range(V_emb)]
    for l in output_parsed:
        result[l[1] - 1] = l[0] - 1

    #マス目
    for i in range(R_emb):
        for j in range(R_emb):
            canvas.create_rectangle(j * sq, i * sq, (j + 1) * sq, (i + 1) * sq, fill='white' if (i + j) % 2 == 0 else "#37DC94")

    score = 0
    used = 0

    #エッジ
    for i in range(R_emb):
        for j in range(R_emb):
            for di, dj in [(-1, 1), (0, 1), (1, 0), (1, 1)]:
                I = i + di
                J = j + dj
                half = (sq + 1) // 2
                if (0 <= I < R_emb and 0 <= J < R_emb and result[i * R_emb + j] != -1 and result[I * R_emb + J] != -1 and graph[result[i * R_emb + j]][result[I * R_emb + J]] > 0):
                    w = graph[result[i * R_emb + j]][result[I * R_emb + J]]
                    canvas.create_line(j * sq + half, i * sq + half, J * sq + half, I * sq + half, fill="#162C9B", width=4 if w >= edges_aver else 2)
                    score += w
                    used += 1

    #ノード
    for i in range(R_emb):
        for j in range(R_emb):
            if result[i * R_emb + j] != -1:
                canvas.create_oval(j * sq + margin, i * sq + margin, (j + 1) * sq - margin, (i + 1) * sq - margin, fill="#FF5126")

    #文字を配置する
    canvas.create_text(W + 80, 10, text="score : " + str(score), font=("", font_size))
    canvas.create_text(W + 100, 10 + font_size * 3, text="used_edges : " + str(used), font=("", font_size))
    canvas.create_text(W + 120, 10 + font_size * 6, text="unused_edges : " + str(effect_edges - used), font=("", font_size))

    return canvas
    
def update_canvas(now_num, next_num):
    canvas_list[now_num].place_forget()
    canvas_list[next_num].place(x=0, y=H_button)

    return

def next_canvas():
    global now_number
    next_number = min(now_number + 1, canvas_num - 1)
    update_canvas(now_number, next_number)
    now_number = next_number
    return

def prev_canvas():
    global now_number
    next_number = max(now_number - 1, 0)
    update_canvas(now_number, next_number)
    now_number = next_number
    return

def slider_canvas(*val):
    global now_number
    next_number = max(val_slider.get() - 1, 0)
    update_canvas(now_number, next_number)
    now_number = next_number
    return

def save_canvas():  #canvasをpostscriptで保存する
    global now_number
    label_save = tkinter.Label(root, text="保存中……", font=("", font_size))
    label_save.place(x=W + 125, y=10 + font_size * 21)

    dig = 3  #ファイル名の桁数
    canvas_list[now_number].place_forget()
    for idx, can in enumerate(canvas_list):
        can.place(x=0, y=H_button)
        can.update()
        can.postscript(file='./save/canvas_' + str(idx).zfill(dig) + '.ps', colormode='color')
        can.place_forget()
    canvas_list[now_number].place(x=0, y=H_button)
    #gifアニメを生成する
    subprocess.run(["convert -delay 30 *.ps canvas_anime.gif"], cwd="./save", shell=True)
    #生成したpsファイルを消す
    for idx in range(canvas_num):
        subprocess.run(["rm canvas_" + str(idx).zfill(dig) + ".ps"], cwd="./save", shell=True)
        
    label_save.destroy()
    return

args = sys.argv
(graph_type, seed) = (args[1], args[2])
#ジェネレータでテストケースを生成する
subprocess.run(["./graph_generator.out testcase.in " + str(graph_type) + " " + str(seed)], cwd="./problem1_toolkit_JP/scripts", shell=True)

#テストケースを読み込む
input_file = "./problem1_toolkit_JP/scripts/testcase.in"

#input_fileを読み込んでgraph, graph_embをつくる
input_data = open(input_file, "r")
input_lines = input_data.readlines()
V, E = map(int, input_lines[0].split())
V_emb, E_emb = map(int, input_lines[E + 1].split())
effect_edges = E  #0でないエッジの数
edges_aver = 0  #0でないエッジの重みの平均
graph = [[0 for i in range(V)] for j in range(V)]
graph_emb = [[] for i in range(V_emb)]
R_emb = int(math.sqrt(V_emb))   #graph_embの一辺
for i in range(1, E+1):
    u, v, w = map(int, input_lines[i].split())
    graph[u - 1][v - 1] += w
    graph[v - 1][u - 1] += w
    if w == 0:
        effect_edges -= 1
    else:
        edges_aver += w
for i in range(E + 2, E + E_emb + 2):
    a, b = map(int, input_lines[i].split())
    graph_emb[a - 1].append(b - 1)
    graph_emb[b - 1].append(a - 1)
edges_aver //= effect_edges

input_data.close()

#出力を拾う
output_data = subprocess.check_output(["./main.out < ../problem1_toolkit_JP/scripts/testcase.in"], cwd="./src", shell=True)
output_parsed = [list(map(int, s.split())) for s in output_data.decode().split('\n') if s != '']

#テストケースを削除
subprocess.run(["rm testcase.in"], cwd="./problem1_toolkit_JP/scripts", shell=True)

sq = 15  #1マスのサイズ
margin = 3  #ノード間の距離
W, H = R_emb * sq, R_emb * sq  #盤面の幅、高さ
W_info = 250  #情報を書くスペースの幅
H_button = 60 #ボタンとかを置くスペースの幅
root = tkinter.Tk()
root.title("HHMM1 Visualizer")
root.geometry(str(W + W_info) + "x" + str(H + H_button))

#canvasの数
font_size = 13
canvas_num = len(output_parsed) // V
canvas_list = []

for i in range(canvas_num):
    can = generate_canvas(output_parsed[i * V:((i + 1) * V - 1)])
    can.create_text(W + 70, 10 + font_size * 9, text=str(i + 1) + "/" + str(canvas_num), font=("", font_size))
    canvas_list.append(can)

button_prev = tkinter.Button(text='prev', command=prev_canvas)
button_prev.place(x=0, y=0)
button_next = tkinter.Button(text='next', command=next_canvas)
button_next.place(x=60, y=0)
button_save = tkinter.Button(text='save', command=save_canvas)
button_save.place(x=W + 125, y=10 + font_size * 18)

val_slider = IntVar()
val_slider.trace('w', slider_canvas)
slider = tkinter.Scale(root, variable=val_slider, orient=HORIZONTAL, length=max(10, W + W_info - 150), from_=1, to=canvas_num)
slider.place(x=120, y=0)

#now_number = 0  #現在のcanvasの番号
canvas_list[now_number].place(x=0, y=H_button)

root.mainloop()