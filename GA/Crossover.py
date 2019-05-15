# -*- coding: UTF-8 -*-

import random as rnd
import copy
import rhinoscriptsyntax as rs


def selectDividePoints(num_timber, divide_range):
    divide_point1 = None
    divide_point2 = None

    flag_divide_point = True
    avoid_infinite_loop = 0
    while flag_divide_point:
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 100:
            print("This is infinite loop in generate divide point")
            input("This is infinite loop in generate divide point near 330, please press ESC key")
            break

        divide_point1 = rnd.randint(0, num_timber - 1)
        divide_point2 = rnd.randint(0, num_timber - 1)

        if divide_point1 == divide_point2:
            continue
        # 次世代に継承する木材の最低本数を予め設定する
        # --------------------------------------------------------

        if not abs(divide_point1 - divide_point2) >= divide_range:
            continue
        else:
            break

    return divide_point1, divide_point2


def select2Poplation(selected_list):
    flag_select_index = True
    avoid_infinite_loop = 0
    while flag_select_index:
        avoid_infinite_loop = avoid_infinite_loop + 1
        select_pop_index1 = rnd.randint(0, len(selected_list) - 1)
        select_pop_index2 = rnd.randint(0, len(selected_list) - 1)
        if select_pop_index1 != select_pop_index2:
            flag_select_index = False
        if avoid_infinite_loop > 30:
            print("This is infinite loop in select index")
            input("This is infinite loop in select index near 348, please press ESC key")
            break

    pop_1 = selected_list[select_pop_index1]  # 評価のプロセスで選択された個体から交叉に使用する個体を選択する
    pop_2 = selected_list[select_pop_index2]  # 評価のプロセスで選択された個体から交叉に使用する個体を選択する

    return pop_1, pop_2


def two_point_crossover(num_timber, divide_range, pop1_instance, pop2_instance, list_temp_gene):
    divide_point1 = None
    divide_point2 = None

    flag_divide_point = True
    avoid_infinite_loop = 0
    while flag_divide_point:
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 100:
            print("This is infinite loop in generate divide point")
            input("This is infinite loop in generate divide point near 330, please press ESC key")
            break

        divide_point1 = rnd.randint(0, num_timber - 1)
        divide_point2 = rnd.randint(0, num_timber - 1)

        if divide_point1 == divide_point2:
            continue
        # 次世代に継承する木材の最低本数を予め設定する
        # --------------------------------------------------------

        if not abs(divide_point1 - divide_point2) >= divide_range:
            continue
        else:
            break

    gene_info_temp = []
    gene_info_center_temp = []
    gene_info_front_temp = []
    gene_info_back_temp = []
    if divide_point1 < divide_point2:
        a = divide_point1
        b = divide_point2
    else:
        a = divide_point2
        b = divide_point1
    c = b - a

    pop1_gene_info = copy.deepcopy(pop1_instance.gene_info)
    gene_index = a
    for i in range(c):
        gene_index = gene_index + 1
        gene_info_center_temp.append(pop1_gene_info[gene_index])

    # まずfrontの方に値を入れる。
    if a == 0:
        pass
    else:
        pop2_gene_info = copy.deepcopy(pop2_instance.gene_info)
        for i in range(a):
            for j in range(num_timber):
                # check_gene_index = copy.deepcopy(pop_2.gene_info[j])
                if pop2_gene_info[j] not in gene_info_center_temp and pop2_gene_info[j] not in gene_info_front_temp:
                    gene_info_front_temp.append(pop2_gene_info[j])
                    break
                else:
                    continue

    for i in range(num_timber - b):
        for j in range(num_timber):
            # check_gene_index = copy.deepcopy(pop_2.gene_info[j])
            pop2_gene_info = copy.deepcopy(pop2_instance.gene_info)
            if pop2_gene_info[j] not in gene_info_center_temp and pop2_gene_info[j] not in gene_info_front_temp and \
                    pop2_gene_info[j] not in gene_info_back_temp:
                gene_info_back_temp.append(pop2_gene_info[j])
                break
            else:
                continue

    # 次の世代の遺伝子情報を作成する。後にGenerateクラスのgene_infoクラス変数を更新する。
    gene_info_temp.extend(gene_info_front_temp)
    gene_info_temp.extend(gene_info_center_temp)
    gene_info_temp.extend(gene_info_back_temp)

    list_temp_gene.append(gene_info_temp)  # 次世代の遺伝子更新用リスト

    pop1_instance.temp_used_list = []  # 一度初期化
    # print("gene_info_center_temp", gene_info_center_temp)
    pop1_instance.temp_used_list.extend(gene_info_center_temp)
    # print("pop_1.temp_used_list", pop_1.temp_used_list)
    pop1_instance.temp_yet_regenerate = []
    pop1_instance.temp_yet_regenerate.extend(gene_info_front_temp)
    pop1_instance.temp_yet_regenerate.extend(gene_info_back_temp)

    already_regenerate = []
    already_regenerate.extend(pop1_instance.temp_used_list)

    return already_regenerate


def random_chunk_crossover(num_timber, divide_range, pop1):
    '''
    ランダムに次世代に引き継ぐ部材数を決定する。接合部材関係をたどることで、
    塊として次世代に継承することを可能にしている。
    :param num_timber:
    :param divide_range:
    :param pop1:
    :return:
    '''

    # 次世代への継承部材数を決定する。
    inheritance_num = rnd.randint(divide_range - 1, num_timber - 1)

    select_tim_ids = []
    flag = True
    avoid_infinite_loop = -1
    while flag:
        avoid_infinite_loop += 1
        if avoid_infinite_loop > 1000:
            # raise Exception('random_chunk_crossover is gone')
            print("random_chunk_crossover break cuz init or not work well")
            break

        if avoid_infinite_loop == 0:
            loop = True
            while loop:
                index = rnd.randint(0, num_timber - 1)
                partner_sum = len(pop1.used_list[index].partner_tim)
                if partner_sum == 0:
                    continue
                else:
                    break
        else:
            partner_sum = len(pop1.used_list[index].partner_tim)

        for j in range(partner_sum):
            select_tim_id = pop1.used_list[index].partner_tim[j]

            if select_tim_id not in select_tim_ids:
                select_tim_ids.append(select_tim_id)

                if len(select_tim_ids) >= inheritance_num:
                    flag = False
                    break
            else:
                pass

        if not flag:
            break

        if len(pop1.used_list[index].partner_tim) >= 1:
            choice_id = rnd.choice(pop1.used_list[index].partner_tim)
        else:
            pass
            # print("partner_tim", pop1.used_list[index].partner_tim)

        for k in range(num_timber):
            if pop1.used_list[k].id == choice_id:
                index = k
                break
            else:
                pass

    # print("inheritance_num", inheritance_num)
    # print("select_tim_ids", select_tim_ids)
    # if not len(select_tim_ids) == inheritance_num:
    #     raise Exception('inheritance did not work')

    return select_tim_ids
