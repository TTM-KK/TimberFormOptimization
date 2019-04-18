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


num_timber = 30         # timberの総本数
divide_range = 5        # 次世代に継承する材の最低本数を指定
cantilever_num = 25     # 初期生成時の全体の中でのcantileverの数
pop_num = 30            # 初期個体数。世代ごとの個体数　ttm add 181003
elite_num = 2           # エリート選択における選択数。
generation_num = 30     # 世代数
tournament_size = 5     # トーナメントサイズ
tournament_num = 3      # トーナメント選択の回数
mutation_ratio = 3      # 突然変異の確率
initial_population_draw = False
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
t1 = time.time()
rs.EnableRedraw(False)
for i in range(pop_num):

    # flag_success = False
    flag_success = dic['generate' + str(i)].cantilever(limit_degree)  # Initial Generate Method.
    # if not flag_success:
    #     input("initial cantilever not success")

    tim1 = dic['generate' + str(i)].used_list[0]
    tim2 = dic['generate' + str(i)].used_list[1]

    copy_from = Rhino.Geometry.Point3d(0, 0, 0)
    copy_to = Rhino.Geometry.Point3d((generate_range * 2) * i, - generate_range * 2, 0)
    vec_move = copy_to - copy_from

    MoveObject.MoveTimberObjects(tim1, tim2, vec_move)  # Moving Objects method for tim1,tim2

    if cantilever_num > num_timber - 2:  # if cantilever_num is not good, stop python script
        sys.exit("cantilever_num is not suitable for num_timber")

    cantilever_start = time.time()  # Initial Cantilever generate part
    for j in range(cantilever_num - 2):
        # flag_success = False
        flag_success = dic['generate' + str(i)].cantilever(limit_degree)
        # if not flag_success:
        #     input("line 128 cantilever not success")
    cantilever_end = time.time()
    # print("Initial Cantilever Method end time: %s this is num %s population" %(cantilever_end - cantilever_start, i))

    bridge_start = time.time()  # Initial Bridge generate part
    for j in range(num_timber - cantilever_num):
        # flag_success = False
        flag_success = dic['generate' + str(i)].bridge(limit_degree)
        # if not flag_success:
        #     input("line 137 bridge not success")
    bridge_end = time.time()
    # print("Initial Bridge Method end time: %s this is num %s population" %(bridge_end - bridge_start, i))


# 初期個体が分裂していないか確認。
for i in range(pop_num):
    pop = dic['generate' + str(i)]
    flag_divide = GA.Method.confirm_pop_divide(num_timber, pop)
    print("flag_divide : %s  Time: %s" % flag_divide)


# Rhinoに描画されるオブジェクとに置き換える。
if initial_population_draw:
    for i in range(pop_num):
        for j in range(num_timber):
            if layer_flag:
                a = 'tim'
                b = str(dic['generate' + str(i)].used_list[j].name)
                rs.CurrentLayer(a+b)

            sf = scriptcontext.doc.Objects.AddBrep(dic['generate' + str(i)].used_list[j].surface)
            crv = scriptcontext.doc.Objects.AddCurve(dic['generate' + str(i)].used_list[j].center_line)

t2 = time.time()
init_generation_time = t2 - t1  # time of Initial Generate
print("\n")
print("init generation time: %s" % init_generation_time)


# Step5: 遺伝子情報を生成し、Generateクラスのgene_infoにappendする。
all_gene_info = []
for i in range(pop_num):
    gene_info = []
    for j in range(num_timber):
        gene_info.append(dic['generate' + str(i)].used_list[j].name)
    all_gene_info.append(gene_info)

if information_flag:
    print("\n")
    print("All gene info", all_gene_info)

for i in range(pop_num):
    for j in range(num_timber):
        dic['generate' + str(i)].gene_info.append(dic['generate' + str(i)].used_list[j].name)


# Main Loop 開始
for main_loop in range(generation_num):

    # Step6:  # EVALUATION　評価
    evaluation_value = []  # 一世代分の評価値を格納するリスト
    t3 = time.time()
    for i in range(pop_num):
        instance_pop = dic['generate' + str(i)]

        # 評価関数　一個体ずつ評価値が帰ってくるように設計すること。
        # evaluate_value = GA.Evaluation.overlap_num2(num_timber, instance_pop)
        # evaluate_value = GA.Evaluation.partner_num_evaluate(num_timber, instance_pop, 2, 10)
        # evaluate_value = GA.Evaluation.pop_height_evaluate(num_timber, instance_pop)
        evaluate_value = GA.Evaluation.pop_evaluation(num_timber, instance_pop)

        dic['generate' + str(i)].evaluation = evaluate_value
        evaluation_value.append(dic['generate' + str(i)].evaluation)

    evaluate_list.append(evaluation_value)  # 全世代の評価値を格納するリスト

    t4 = time.time()
    print("\n")
    print("Result of EVALUATION --- Generation : %s  Result : %s" % (main_loop, evaluation_value))
    print("Evaluation Time: %s" % (t4 - t3))

    # Step7:  # SELECTION  選択
    selected_list = []
    sort_generate_instance_list = []  # Genarateクラスインスタンスのリストを作成する。
    for i in range(pop_num):
        sort_generate_instance_list.append(dic['generate' + str(i)])

    # リスト内のクラスインスタンスの保持する評価値に従いソートを行う
    if flag_high:
        GA.Selection.sort_high(sort_generate_instance_list)
    else:
        GA.Selection.sort_low(sort_generate_instance_list)

    # elite selection
    GA.Selection.eliteSelection(elite_num, sort_generate_instance_list, selected_list)

    # tournament selection
    GA.Selection.tournamentSelection_min(tournament_size, tournament_num, sort_generate_instance_list, selected_list)

    # Step8: 交叉　再生成　
    # 更新用リスト各位
    temp_list_center_for_next_generation = [[[] for i in range(num_timber)] for j in range(pop_num)]
    temp_list_srf_for_next_generation = [[[] for i in range(num_timber)] for j in range(pop_num)]
    temp_list_select_domain_list_for_next_generation = [[[] for i in range(num_timber)] for j in range(pop_num)]
    list_temp_partner_tim = [[[] for i in range(num_timber)] for j in range(pop_num)]  # partner_tim更新用のリストを作成
    list_temp_gene_tim = []  # 次世代の遺伝子更新用リスト

    # 前世代のpartner_timを保存する。
    list_partner_tim_prior_generation = [[[] for i in range(num_timber)] for j in range(pop_num)]  # 前世代のpartner_timを保存。
    for i in range(pop_num):
        for j in range(num_timber):
            for k in range(num_timber):
                if dic['generate' + str(i)].used_list[k].name == j:
                    list_partner_tim_prior_generation[i][j].extend(dic['generate' + str(i)].used_list[j].partner_tim)
                    break
    print("list_partner_tim_prior_generation", list_partner_tim_prior_generation)

    for loop in range(pop_size):
        if information_flag:
            print("\n")
            print("start regeneration No.%s" % loop)
            print("------------------------------------------------------------")

        # decide the 2 crossover point
        divide_point1, divide_point2 = GA.Crossover.selectDividePoints(num_timber, divide_range)

        # Get the index in the 'selected_list' of the individual used for crossover
        pop_1, pop_2 = GA.Crossover.select2Poplation(selected_list)

        # 2点交叉　Generateクラス変数の更新とlist_temp_gene_timに新しく生成した遺伝子情報をappendする。 継承する材の番号が格納されたリストをreturnする
        already_regenerate = GA.Crossover.TwoPointCrossover(num_timber, pop_1, pop_2, divide_point1, divide_point2,
                                                            list_temp_gene_tim)

        # pop_2に関して継承する材を決定するアルゴリズム add
        decide_inheritance_num_list, connect_list = GA.Method.DecideInheritanceTimber(pop_1, pop_2, already_regenerate,
                                                                                      generate_range)
        # print('\n')
        # print('connect_list', connect_list)

        # print("decide_inheritance_num_list %s"%(decide_inheritance_num_list))

        # 個体の保持する要素の保存。　　一旦pop_1をコピーしてオブジェクトを保存する。一つの個体生成がおわったら元に戻す。
        list_srf_temp = []
        list_center_line_temp = []
        list_select_domain_temp = []
        GA.Method.saveInstanceInformation(num_timber, pop_1, list_srf_temp, list_center_line_temp,
                                          list_select_domain_temp)

        # pop_2のTimber、select_domain_listのDomainを更新する  add 190218
        GA.Method.RenewalPop2(pop_1, pop_2, decide_inheritance_num_list)

        # select_domain_listの更新。　形態を引き継いでいる材の接合ドメインの更新を行う。前世代では使用していたが、空席になるドメインが生じるはずなので
        GA.Method.selectDomainRenewal(already_regenerate, num_timber, pop_1)

        # select_domain_listの更新2.
        GA.Method.selectDomainRenewal2(decide_inheritance_num_list, num_timber, pop_1)

        # print('inheritance form 1', already_regenerate)
        # print('inheritance form 2', decide_inheritance_num_list)

        # そのまま継承する材をMoveObjectでコピー、partnerを更新する
        GA.Method.MovePopulationUpdate(already_regenerate, pop_1, generate_range, generation_num, between_draw_rhino,
                                       main_loop, loop, list_temp_partner_tim)

        # そのまま継承する材をMoveObjectでコピーし、partnerを更新する。　add 190220
        GA.Method.MovePopulationUpdate2(decide_inheritance_num_list, pop_1, pop_2, generate_range, generation_num,
                                        between_draw_rhino, main_loop, loop, list_temp_partner_tim)

        # pop_2の材の位相関係を継承しながら再生成を行う。
        for i in range(len(connect_list)):
            index = decide_inheritance_num_list.index(connect_list[i][0])
            del decide_inheritance_num_list[index]
            already_regenerate.append(connect_list[i][0])
        # print('check del inheritance form', decide_inheritance_num_list)

        already_regenerate.extend(decide_inheritance_num_list)  # add 190220
        # print('check already_regenerate', already_regenerate)
        # print("already_regenerate_list : %s"%(already_regenerate))
        for i in range(len(connect_list)):
            decide_inheritance_num_list.append(connect_list[i][0])

        yet_regenerate = []
        yet_regenerate.extend(pop_1.temp_yet_regenerate)

        # print("before yet_regenerate_list : %s"%(yet_regenerate))  # add 190220
        for ex in range(len(decide_inheritance_num_list)):
            index_ex = yet_regenerate.index(decide_inheritance_num_list[ex])
            yet_regenerate.pop(index_ex)
        # print("after yet_regenerate_list : %s" % (yet_regenerate))

        # partner_timの確認　check_timber_partner3と一致している必要がある。
        # check_timber_partner1 = []
        # for i in range(num_timber):
        #     for j in range(num_timber):
        #         if pop_1.used_list[j].name == i:
        #             check_timber_partner1.append(pop_1.used_list[j].partner_tim)
        #             break

        # print("check_timber_partner1", check_timber_partner1)

        # pop1のpartner_listを更新する。
        for i in range(num_timber):
            for j in range(num_timber):
                if pop_1.used_list[j].name == i:
                    pop_1.used_list[j].partner_tim = []
                    pop_1.used_list[j].partner_tim.extend(list_temp_partner_tim[loop][i])
                    break

        # partner_timの更新確認
        check_timber_partner2 = []
        for i in range(num_timber):
            for j in range(num_timber):
                if pop_1.used_list[j].name == i:
                    check_timber_partner2.append(pop_1.used_list[j].partner_tim)
                    break
        # print("check temp timber partner : %s" % (check_timber_partner2))
        # print("list_temp_partner_tim", list_temp_partner_tim)

        # 再生成のプロセス
        ReGenerate.regenerate(already_regenerate, yet_regenerate, pop_1, pop_2, num_timber, limit_degree,
                              generation_num, main_loop, loop, between_draw_rhino, list_temp_partner_tim,
                              mutation_ratio)

        # TODO 再生成した個体がバラバラに成っていないか確認するアルゴリズムを記述する。
        t1_flag_divede = time.time()
        flag_divide = GA.Method.confirm_pop_divide(num_timber, pop_1)
        t2_flag_divide = time.time()

        print("flag_divide : %s  Time: %s" % (flag_divide, t2_flag_divide-t1_flag_divede))

        # partner_timの確認
        check_timber_partner3 = []
        for i in range(num_timber):
            for j in range(num_timber):
                if pop_1.used_list[j].name == i:
                    check_timber_partner3.append(pop_1.used_list[j].partner_tim)
                    break

        if check_timber_partner3 == list_temp_partner_tim[loop]:
            pass
        else:
            raise ValueError('check_timber_partner3 & list_temp_partner_tim is not same, did not working')

        # pop_1のpartner_timを再生成前の状態に戻す。
        for i in range(num_timber):
            for j in range(num_timber):
                if pop_1.used_list[j].name == i:
                    pop_1.used_list[j].partner_tim = []
                    pop_1.used_list[j].partner_tim.extend(list_partner_tim_prior_generation[pop_1.population_num][i])
                    break

        # partner_timの更新確認 check_timber_partner1と一致している必要がある。
        # check_timber_partner4 = []
        # for i in range(num_timber):
        #     for j in range(num_timber):
        #         if pop_1.used_list[j].name == i:
        #             check_timber_partner4.append(pop_1.used_list[j].partner_tim)
        #             break
        #
        # print("check_timber_partner4", check_timber_partner4)

        # if check_timber_partner1 == check_timber_partner4:
        #     pass
        # else:
        #     raise ValueError('check_timber_partner1 & check_timber_partner4 is not same')

        # Generateクラスインスタンス変数の更新
        # 戻す。　　次世代の個体生成前に保持していたGenerateクラスの変数に戻す。
        GA.Method.RenewalInstanceInformationSameGeneration(pop_1, temp_list_srf_for_next_generation,
                                                           temp_list_center_for_next_generation,
                                                           temp_list_select_domain_list_for_next_generation,
                                                           list_srf_temp, list_center_line_temp,
                                                           list_select_domain_temp, loop)

        rs.EnableRedraw(True)
        rs.Redraw()
        rs.EnableRedraw(False)

        # print("list_temp_partner_tim", list_temp_partner_tim)
        # input("stop")

    # 全個体のGenerateインスタンス変数を更新する。
    # srf, center_lineの更新
    for i in range(pop_num):
        for j in range(num_timber):
            name_tim = dic['generate' + str(i)].used_list[j].name
            # print("name_tim", name_tim)
            dic['generate' + str(i)].used_list[j].center_line = None  # listで問題ないっぽい
            dic['generate' + str(i)].used_list[j].center_line = temp_list_center_for_next_generation[i][name_tim]

            dic['generate' + str(i)].used_list[j].surface = None
            dic['generate' + str(i)].used_list[j].surface = temp_list_srf_for_next_generation[i][name_tim]

    #  partner_tim　の更新
    for i in range(pop_num):
        for j in range(num_timber):
            for k in range(num_timber):  # TODO
                if dic['generate' + str(i)].used_list[k].name == j:
                    dic['generate' + str(i)].used_list[k].partner_tim = []
                    dic['generate' + str(i)].used_list[k].partner_tim.extend(list_temp_partner_tim[i][j])

            # print("update partner_tim", dic['generate' + str(i)].used_list[j].partner_tim)

            # 中心線を更新しているので、リスト内の値を更新するb
            # print("check error", dic['generate' + str(i)].used_list[j].center_line)
            dic['generate' + str(i)].used_list[j].mesureLength_RhinoCommon()

    # tim_distance の更新
    for i in range(pop_num):
        for j in range(num_timber):
            for k in range(num_timber):
                if k != j:
                    timberMethod.distanceBetweenTimber_RhinoCommon(dic['generate' + str(i)].used_list[j],
                                                                   dic['generate' + str(i)].used_list[k])
                else:
                    dic['generate' + str(i)].used_list[j].tim_distance[dic['generate' + str(i)].used_list[j].name] = []
                    continue

    # gene_information の更新
    for i in range(pop_num):
        dic['generate' + str(i)].gene_info = []
        dic['generate' + str(i)].gene_info.extend(list_temp_gene_tim[i])

    # select_domain_listの更新
    for i in range(pop_num):
        for j in range(num_timber):
            dic['generate' + str(i)].used_list[j].select_domain_list = []
            dic['generate' + str(i)].used_list[j].select_domain_list.extend(
                temp_list_select_domain_list_for_next_generation[i][dic['generate' + str(i)].used_list[j].name])

# Step10:  EVALUATION
evaluation_value = []
t3_1 = time.time()
for i in range(pop_num):
    instance_pop = dic['generate' + str(i)]

    # evaluate_value = GA.Evaluation.overlap_num2(num_timber, instance_pop)
    # evaluate_value = GA.Evaluation.partner_num_evaluate(num_timber, instance_pop, 2, 3)
    evaluate_value = GA.Evaluation.pop_evaluation(num_timber, instance_pop)

    dic['generate' + str(i)].evaluation = evaluate_value

    evaluation_value.append(dic['generate' + str(i)].evaluation)
    # print('evaluation value Pop: %s : value is %s'%(i, dic['generate' + str(i)].evaluation))
evaluate_list.append(evaluation_value)


# 一番適応度が高い個体だけを描画する。ほかはレイヤーに隠す。
eva_high_index = evaluation_value.index(max(evaluation_value))
for i in range(pop_num):
    rs.AddLayer('pop' + str(i))


for i in range(pop_num):
    for j in range(num_timber):
        center_line = scriptcontext.doc.Objects.AddCurve(dic['generate' + str(i)].used_list[j].center_line)
        surface = scriptcontext.doc.Objects.AddBrep(dic['generate' + str(i)].used_list[j].surface)
        rs.ObjectLayer(center_line, 'pop' + str(i))
        rs.ObjectLayer(surface, 'pop' + str(i))

for i in range(pop_num):
    if i == eva_high_index:
        pass
    else:
        rs.LayerVisible('pop' + str(i), False)

rs.CurrentLayer('pop' + str(eva_high_index))
rs.LayerVisible('all_pop_layer', False)


t4_1 = time.time()
print("\n")
print("Result of EVALUATION --- Generation : %s  Result : %s" % (generation_num, evaluation_value))
print("Evaluation Time: %s" % (t4_1 - t3_1))


program_finish = time.time()
print("\n")
print("EVALUATE : result --- %s" % evaluate_list)
print("Processing Time : %s" % (program_finish - program_start))


# グラフに評価値の推移を描画
drawInformatinon.drawEvaluateValue(evaluate_list)

#
# partner_list = []
# for i in range(len(pop_1.used_list)):
#     partner_list.append(pop_1.used_list[i].partner_tim)
# print("partner_list : %s"%(partner_list))

#
# value = []
# for i in range(pop_num):
#     length = len(dic['generate' + str(i)].used_list)
#     value.append(length)
# sum_list = sum(value)
# print("sum of used_timber_num", sum_list)
#
# for i in range(pop_num):
#     for j in range(num_timber):
#         srf = dic['generate' + str(i)].used_list[j].surface
#         print("srf", srf)
