# -*- coding:utf-8 -*-
from Generate import Generate
import rhinoscriptsyntax as rs
import time
# import copy
# import random as rnd
import sys
from forMain import Sort
from forMain import timberMethod
from forMain import Instance
from forMain import MoveObject
import Rhino.Geometry
import scriptcontext
from forMain import drawInformatinon
# from matplotlib import pyplot
import GA.Selection
import GA.Evaluation
import GA.Crossover
import GA.Method
import ReGenerate


num_timber = 10         # timberの総本数
divide_range = 2        # 次世代に継承する材の最低本数を指定
num_base_timber = 5
cantilever_num = 2      # 初期生成時の全体の中でのcantileverの数
bridge_num = 3

pop_num = 4             # 初期個体数。世代ごとの個体数　ttm add 181003
elite_num = 1           # エリート選択における選択数。
generation_num = 3      # 世代数
tournament_size = 3     # トーナメントサイズ
tournament_num = 1      # トーナメント選択の回数
mutation_ratio = 3      # 突然変異の確率
initial_population_draw = True
flag_high = True        # ソート昇順の場合True　降順の場合False

connect_count = 10      # 接合制約数
name_list = []          # timberの名前
prototype_ID = 0        # 試作個体の番号
pop_size = pop_num      # 交叉時に生成する個体数
generate_range = 3000   # 生成可能範囲を指定。（現在は立方体） TODO 立方体以外にも対応したいところ。
between_draw_rhino = generation_num  # generation_numを割り切れる数で指定すること。


evaluate_list = []        # 各世代の評価値を保存しておくためのリスト
# temp_center_line = []   # 複製した中心線のリスト
# temp_surface = []       # 複製したサーフェスのリスト
# temp_mark = []
timber_num = []           # Timberクラスの各インスタンスの通し番号を格納するリスト
new_gene_num_list = []

# 制約条件
limit_degree = [45, 135]  # 接合角度制約


# boolean
input_flag = False        # 再生成アルゴリズム用　デバック時に使用すると便利
redraw_flag = False       # 描画を逐一見るためのフラグ。重くなると思うから普段はFalseで
information_flag = False
layer_flag = False


rs.AddLayer('all_pop_layer')
rs.CurrentLayer('all_pop_layer')

# Step0: rhino上のオブジェクトを取得。また通し番号を作成する。
get_center_line = rs.GetObjects("select %s lines" % num_timber, rs.filter.curve)
get_surface = rs.GetObjects("Select %s Surfaces" % num_timber, rs.filter.surface)
get_obj = Sort.scanObjectSort(num_timber, get_center_line, get_surface)

program_start = time.time()

# メンバ変数に格納する
center_line = get_obj[0]
all_surface = get_obj[1]
# all_mark = get_obj[2]

for i in range(0, num_timber):
    name_list.append(i)


# Step1: サーフィスと中心線を（個体数*Timberの種類）だけ複製。後でインスタンス変数に取り込むため、リストに格納する
temp_center_line = Instance.axis_instance(pop_num, center_line)
temp_surface = Instance.surface_instance(pop_num, all_surface)
# temp_mark = inst.mark_instance(pop_num, all_mark)

# print("temp_surface", temp_surface)
# print("temp_center_line", temp_center_line)


# Step2: Generateクラスのインスタンスを個体数だけ作成
dic = {}
for foo in range(pop_num):
    dic['generate' + str(foo)] = foo

for i in range(pop_num):
    timber_num.append(i)

# スキャンデータを生成クラスに渡し、インスタンス化
for i in range(pop_num):
    dic['generate' + str(i)] = Generate(temp_center_line[i], temp_surface[i], name_list, num_timber, prototype_ID,
                                        timber_num[i])


# Step3: 各Generateクラスのインスタンス毎にTimberクラスのインスタンスを作成
for j in range(pop_num):
    dic['generate' + str(j)].instantiate_timber()  # Timberクラスのインスタンスを作成するGenerateクラスのメソッド
    dic['generate' + str(j)].pop_index = j  # 個体番号を振る
    # print("pop_index", dic['generate' + str(j)].pop_index)


# Step4 初期生成
closed_curve = rs.GetObjects("select closed curves, base timber generated")
# base_points = rs.GetObjects("select base points for timber generate")


t1 = time.time()

objects_curve = []
if closed_curve:
    for i in range(len(closed_curve)):
        curve = rs.coercecurve(closed_curve[i])
        objects_curve.append(curve)

# objects_point = []
# if base_points:
#     for i in range(len(base_points)):
#         point = rs.coerce3dpoint(base_points[i])
#         objects_point.append(point)

for j in range(num_base_timber):
    flag_success = dic['generate' + str(0)].generate_ground_init(generate_range, objects_curve=objects_curve)  # Initial Generate Method.
    if flag_success:
        pass
    else:
        raise Exception("init_base_generation fail")

t2 = time.time()

print("time:%s" % (t2 - t1))


for i in range(cantilever_num):
    flag_success = dic['generate' + str(0)].cantilever(limit_degree)
    if not flag_success:
        raise Exception('cantilever fail')

for i in range(bridge_num):
    flag_success = dic['generate' + str(0)].bridge(limit_degree)

    if not flag_success:
        raise Exception('bridge is fail')


for j in range(num_timber):
    if layer_flag:
        a = 'tim'
        b = str(dic['generate' + str(0)].used_list[j].name)
        rs.CurrentLayer(a+b)

    sf = scriptcontext.doc.Objects.AddBrep(dic['generate' + str(0)].used_list[j].surface)
    crv = scriptcontext.doc.Objects.AddCurve(dic['generate' + str(0)].used_list[j].center_line)
