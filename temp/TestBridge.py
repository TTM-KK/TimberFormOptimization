# -*- coding:utf-8 -*-
from Generate import Generate
import rhinoscriptsyntax as rs
import time
import sys
import Sort as sort
import Instance as inst
import MoveObject as move
from GA import Evaluation as eva

#-----------------------------------------------------------------------------------------------------------------------
# variable
num_timber = 5         # timberの総本数
connect_count = 10      # 接合制約数
cantilever_num = 3      # 全体の中でのcantileverの数
opt_tolerance = 1000    # 点接合への近似化の際の許容値
dete_tolerance = 1000   # 他材との接触許容値
name_list = []          # timberの名前
prototype_ID = 0        # 試作個体の番号
pop_num = 1             # 初期個体数。世代ごとの個体数　ttm add 181003
pop_size = 1           # 交叉時に生成する個体数
generate_range = 3000   # 生成可能範囲を指定。（現在は立方体） TODO 立方体以外にも対応したいところ。
tournament_size = 3     # トーナメントサイズ
generation_num = 1

# temp_center_line = []   # 複製した中心線のリスト
# temp_surface = []       # 複製したサーフェスのリスト
# temp_mark = []
timber_num = []         # Timberクラスの各インスタンスの通し番号を格納するリスト
new_gene_num_list = []

#-----------------------------------------------------------------------------------------------------------------------


# Step0: rhino上のオブジェクトを取得。また通し番号を作成する。
#-----------------------------------------------------------------------------------------------------------------------
# centerLine = []
# all_surface = []
# all_mark = []
get_center_line = rs.GetObjects("select %s lines" % num_timber, rs.filter.curve)
get_surface = rs.GetObjects("Select %s Surfaces" % num_timber, rs.filter.surface)
get_mark_line = rs.GetObjects("Select %s mark line" % num_timber, rs.filter.curve)

get_obj = sort.scanObjectSort(num_timber, get_center_line, get_surface, get_mark_line)

# メンバ変数に格納する
center_line = get_obj[0]
all_surface = get_obj[1]
all_mark = get_obj[2]

for i in range(0, num_timber):
    name_list.append(i)  # リスト内包表記に書き換える


# Step1: サーフィスと中心線を（個体数*Timberの種類）だけ複製。後でインスタンス変数に取り込むため、リストに格納する
#-----------------------------------------------------------------------------------------------------------------------
temp_center_line = inst.axis_instance(pop_num, center_line)
temp_surface = inst.surface_instance(pop_num, all_surface)
temp_mark = inst.mark_instance(pop_num, all_mark)


# Step2: Generateクラスのインスタンスを個体数だけ作成
#-----------------------------------------------------------------------------------------------------------------------
dic = {}
for foo in range(pop_num):
    dic['generate' + str(foo)] = foo

for i in range(pop_num):
    timber_num.append(i)

for i in range(pop_num):  # スキャンデータを生成クラスに渡す
    dic['generate' + str(i)] = Generate(temp_center_line[i], temp_surface[i], temp_mark[i], name_list, num_timber, prototype_ID, timber_num[i])


# Step3: 各Generateクラスのインスタンス毎にTimberクラスのインスタンスを作成
#-----------------------------------------------------------------------------------------------------------------------
for j in range(pop_num):
    dic['generate' + str(j)].objectTimber_1()  # Timberクラスのインスタンスを作成するGenerateクラスのメソッド


# Step4 初期生成
#-----------------------------------------------------------------------------------------------------------------------
t1 = time.time()
rs.EnableRedraw(False)
for i in range(pop_num):

    dic['generate' + str(i)].cantilever(connect_count, opt_tolerance, dete_tolerance)  # Initial Generate Method.

    tim1 = dic['generate' + str(i)].used_list[0]
    tim2 = dic['generate' + str(i)].used_list[1]

    copy_from = (0, 0, 0)
    copy_to = ((generate_range * 2) * i, - generate_range * 2, 0)
    vec_move = rs.VectorCreate(copy_to, copy_from)

    move.MoveTimberObjects(tim1, tim2, vec_move)  # Moving Objects method for tim1,tim2

    if cantilever_num   > num_timber - 2:  # if cantilever_num is not good, stop python script
        sys.exit("cantilever_num is not suitable for num_timber")

    cantilever_start = time.time()  # Initial Cantilever generate part
    for j in range(cantilever_num - 2):
        dic['generate' + str(i)].cantilever(connect_count, opt_tolerance, dete_tolerance)
    cantilever_end = time.time()
    print("Initial Cantilever Method end time: %s this is num %s population" %(cantilever_end - cantilever_start, i))

    bridge_start = time.time()  # Initial Bridge generate part
    for j in range(num_timber - (cantilever_num)):
        dic['generate' + str(i)].bridge(connect_count, opt_tolerance, dete_tolerance)
    bridge_end = time.time()
    print("Initial Bridge Method end time: %s this is num %s population" %(bridge_end - bridge_start, i))

# t1_2 = time.time()
# if t1_2 - t1 < 300:
#     input("Initial generate is finished. if you want to continue, please type'1'.")

t2 = time.time()

init_generation_time = t2 - t1  # time of Initial Generate
print("\n")
print("init generation time: %s"%(init_generation_time))

# for i in range(num_timber):
#     print("timber name of generate0", dic['generate' + str(0)].used_list[i].partner_tim)


# Step5: Gene information Generate
#-----------------------------------------------------------------------------------------------------------------------
all_gene_info = []
for i in range(pop_num):
    gene_info = []
    for j in range(num_timber):
        gene_info.append(dic['generate' + str(i)].used_list[j].name)
    all_gene_info.append(gene_info)
print("all gene information", all_gene_info)

for i in range(pop_num):
    for j in range(num_timber):
        dic['generate' + str(i)].gene_information.append(dic['generate' + str(i)].used_list[j].name)

    print("Gene information Pop: %s : %s"%(i, dic['generate' + str(i)].gene_information))


# Step6:  # Evaluate Process
#-----------------------------------------------------------------------------------------------------------------------
evaluation_value = []
t3 = time.time()
for i in range(pop_num):
    instance_pop = dic['generate' + str(i)]
    evaluate_value = eva.overlap_num(num_timber, instance_pop)
    dic['generate' + str(i)].evaluation = evaluate_value

    evaluation_value.append(dic['generate' + str(i)].evaluation)
    # print('evaluation value Pop: %s : value is %s'%(i, dic['generate' + str(i)].evaluation))

t4 = time.time()
print(evaluation_value)
print("Evaluation Time: %s"%(t4- t3))


# Step7:  # Selection
#-----------------------------------------------------------------------------------------------------------------------
sort_generate_instance_list = []  # Genarateクラスインスタンスのリストを作成する。
for i in range(pop_num):
    sort_generate_instance_list.append(dic['generate' + str(i)])

print("sort Generate Instance List", sort_generate_instance_list)

# リスト内のクラスインスタンスの保持する評価値に従いソートを行う。
flag = True
while flag:
    counter = 0
    for i in range(len(sort_generate_instance_list)):
        value_a = sort_generate_instance_list[i].evaluation
        if i == len(sort_generate_instance_list) - 1:
            value_b = sort_generate_instance_list[0].evaluation
        else:
            value_b = sort_generate_instance_list[i + 1].evaluation

        # TODO valueA と valueBを比較して両者を入れ替えるかそのまま保持するかを決定していく。
        if i == len(sort_generate_instance_list) - 1:
            if value_a > value_b:
                sort_generate_instance_list[i], sort_generate_instance_list[0] = sort_generate_instance_list[0], sort_generate_instance_list[i]
            else:
                counter = counter + 1
                continue
        elif i != len(sort_generate_instance_list) - 1:
            if value_a < value_b:
                sort_generate_instance_list[i], sort_generate_instance_list[i + 1] = sort_generate_instance_list[i + 1], sort_generate_instance_list[i]
            else:
                counter = counter + 1
                continue

    if counter == len(sort_generate_instance_list):
        flag = False

print("sort_generate_instance_list", sort_generate_instance_list)

# ソートしたリストから上位2個体を選択肢次世代に継承する。エリート選択
# トーナメント選択のメソッドを作成する。
# select_elite = []
# elite_num = 2
# flag = True
# for i in range(elite_num):
#     select = sort_generate_instance_list[i]
#     select_elite.append(select)
# if flag:
#     for j in range(elite_num):
#         del sort_generate_instance_list[0]
#
# print("select_elite", select_elite)
# print("sort_generate_instance_list", sort_generate_instance_list)
#
#
# tournament_list = []
# tournament_size = 2
# tournament_num = 3
# for i in range(tournament_num):
#     choices = rnd.sample(sort_generate_instance_list, tournament_size)
#     print("choices", choices)
#     rnd_para = rnd.randint(0, tournament_size - 1)
#     tournament_list.append(choices[rnd_para])
#
# print("tournament_list", tournament_list)

