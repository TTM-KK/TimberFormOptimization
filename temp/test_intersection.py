# -*- coding:utf-8 -*-
from Generate import Generate
import rhinoscriptsyntax as rs
import time
import Sort as sort
import Instance as inst
# from matplotlib import pyplot
import GA.Evaluation
import GA.Method

num_timber = 20
name_list = []
timber_num = []
pop_num = 1
prototype_ID = 0



get_center_line = rs.GetObjects("select %s lines" % num_timber, rs.filter.curve)
get_surface = rs.GetObjects("Select %s Surfaces" % num_timber, rs.filter.surface)
get_obj = sort.scanObjectSort(num_timber, get_center_line, get_surface)

program_start = time.time()

# メンバ変数に格納する
center_line = get_obj[0]
all_surface = get_obj[1]
# all_mark = get_obj[2]

for i in range(0, num_timber):
    name_list.append(i)


# Step1: サーフィスと中心線を（個体数*Timberの種類）だけ複製。後でインスタンス変数に取り込むため、リストに格納する
#-----------------------------------------------------------------------------------------------------------------------
temp_center_line = inst.axis_instance(pop_num, center_line)
temp_surface = inst.surface_instance(pop_num, all_surface)
# temp_mark = inst.mark_instance(pop_num, all_mark)

# print("temp_surface", temp_surface)
print("temp_center_line", temp_center_line)

# Step2: Generateクラスのインスタンスを個体数だけ作成
#-----------------------------------------------------------------------------------------------------------------------
dic = {}
for foo in range(pop_num):
    dic['generate' + str(foo)] = foo

for i in range(pop_num):
    timber_num.append(i)

for i in range(pop_num):  # スキャンデータを生成クラスに渡す
    dic['generate' + str(i)] = Generate(temp_center_line[i], temp_surface[i], name_list, num_timber, prototype_ID, timber_num[i])

for j in range(pop_num):
    dic['generate' + str(j)].objectTimber()  # Timberクラスのインスタンスを作成するGenerateクラスのメソッド
    dic['generate' + str(j)].pop_index = j  # 個体番号を振る
    # print("pop_index", dic['generate' + str(j)].pop_index)





intersect_num = GA.Evaluation.overlap_num2_for_Check(num_timber, dic['generate' + str(0)])

print("Intersect num : %s"%(intersect_num))
