# -*- coding: UTF-8 -*-

import random as rnd
import copy
import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry
import scriptcontext


def CopyTimberObjects(timber_instance, list_srf_temp, list_center_line_temp):
    """
    サーフェスと軸線をリストに保存するためにdeepcopyする
    :param timber_instance: Timberインスタンス
    :param list_srf_temp: コピーするリスと
    :param list_center_line_temp: コピーするリスト
    :return: なし。
    """
    # center_line = rs.CopyObject(timber_instance.center_line)
    # srf = rs.CopyObject(timber_instance.surface)
    center_line = copy.deepcopy(timber_instance.center_line)
    srf = copy.deepcopy(timber_instance.surface)
    # mark_line1 = rs.CopyObject(timber_instance.two_mark_line[0])
    # mark_line2 = rs.CopyObject(timber_instance.two_mark_line[1])
    # rs.CopyObject(timber_1.drill_line_list, vector_move)
    list_srf_temp.append(srf)
    list_center_line_temp.append(center_line)


def confirm_pop_divide(num_timber, pop_instance1):
    """
    個体がバラけていないかどうかを判定するアルゴリズム
    :param num_timber: 一個体を構成する木材の数
    :param pop_instance1: 個体のインスタンス
    :return: もし木材同士がバラけていないのならば、Trueを返す。
    """
    # temp_partner_list  = []
    # for i in range(len(pop_instance1.used_list)):
    #     temp_partner_list.append(pop_instance1.used_list[i].partner_tim)

    counter_list = [i - i for i in range(num_timber)]  # [0,0,0,0.....]
    confirm_list = [i for i in range(num_timber)]  # [0,1,2,3,4]
    emerge_list = []
    loop = True
    counter = -1

    # print('counter_list', counter_list)
    # print('confirm_list', confirm_list)
    # print('emerge_list', emerge_list)

    partner = pop_instance1.used_list[0].partner_tim
    tim_name = pop_instance1.used_list[0].id

    if tim_name not in emerge_list:
        emerge_list.append(tim_name)

    counter_list[tim_name] = 1

    if tim_name in confirm_list:
        del confirm_list[confirm_list.index(tim_name)]

    for i in range(len(partner)):
        tim_id = partner[i]
        if tim_id not in emerge_list:
            emerge_list.append(tim_id)

        counter_list[tim_id] = 1

        # if tim_id in confirm_list:
        #     del confirm_list[confirm_list.index(tim_id)]

    # この時点で分裂していること確定。
    if len(partner) == 0:
        # print('partner is 0')
        # print('counter_list', counter_list)
        # print('confirm_list', confirm_list)
        # print('emerge_list', emerge_list)
        return False

    for i in range(len(partner)):
        if partner[i] in confirm_list:
            tim_name = copy.deepcopy(partner[i])
            break

    while loop:
        counter += 1
        if counter > 500:
            raise ValueError('infinite loop')

        re_loop = False

        for i in range(num_timber):
            if pop_instance1.used_list[i].id == tim_name:
                partner = pop_instance1.used_list[i].partner_tim

                # 3つのリストを更新する
                if tim_name not in emerge_list:
                    emerge_list.append(tim_name)
                counter_list[tim_name] = 1
                if tim_name in confirm_list:
                    del confirm_list[confirm_list.index(tim_name)]

                for j in range(len(partner)):
                    tim_id = partner[j]

                    # 2つのリストを更新する
                    if tim_id not in emerge_list:
                        emerge_list.append(tim_id)
                    counter_list[tim_id] = 1
                    # if tim_id in confirm_list:
                    #     del confirm_list[confirm_list.index(tim_id)]

                counter_partner = 0
                for j in range(len(partner)):
                    if partner[j] in confirm_list:
                        tim_name = copy.deepcopy(partner[j])
                        break
                    else:
                        counter_partner += 1

                if counter_partner == len(partner):
                    # まだpartnerを確認していない部材があればtim_nameとしwhileを継続
                    for j in range(len(emerge_list)):
                        if emerge_list[j] in confirm_list:
                            tim_name = copy.deepcopy(emerge_list[j])
                            re_loop = True
                            break

                    if re_loop:
                        break

                    # すべての部材IDがリスト内に現れているならばcounter_list内はすべて１になっているはず。
                    if 0 not in counter_list:
                        # print('counter_list', counter_list)
                        # print('confirm_list', confirm_list)
                        # print('emerge_list', emerge_list)
                        return True
                    else:
                        # print('counter_list', counter_list)
                        # print('confirm_list', confirm_list)
                        # print('emerge_list', emerge_list)
                        return False

                break

            else:
                pass

        if re_loop:
            continue

        # この時点で分裂していること確定。
        if len(partner) == 0:
            # print('partner is 0')
            # print('counter_list', counter_list)
            # print('confirm_list', confirm_list)
            # print('emerge_list', emerge_list)
            return False


def decide_inheritance_timber(pop_instance1, pop_instance2, already_regenerate_list, generate_range):
    """
    pop_2の中で継承する材を決定し、材の個体番号をreturnする。
    :param pop_instance1:
    :param pop_instance2:
    :param already_regenerate_list:
    :param generate_range:
    :return: 1; pop2の継承する材のID　2: 継承する材の内pop1に接合している材のIDと接合相手のID --> [接合している材のID, 接合している相手の材のID]
    """

    inherit_timber_id_list = []
    connect_list = []
    move_pop2_num_list = []

    pop_num_1 = pop_instance1.population_num  # ttm change pop_index -> population_num
    pop_num_2 = pop_instance2.population_num
    num_range = pop_num_1 - pop_num_2

    move_from_p = Rhino.Geometry.Point3d(0,0,0)
    move_to_p = Rhino.Geometry.Point3d(num_range*generate_range*2,0,0)
    vec_move = move_to_p - move_from_p
    xf = Rhino.Geometry.Transform.Translation(vec_move)

    for i in range(len(pop_instance2.used_list)):
        if pop_instance2.used_list[i].id not in already_regenerate_list:
            move_pop2_num_list.append(pop_instance2.used_list[i].id)
        else:
            continue

    list_srf = []
    list_axis = []
    list_section_length = []
    list_timber_num = []
    for i in range(len(move_pop2_num_list)):
        move_index = move_pop2_num_list[i]
        for j in range(len(pop_instance2.used_list)):
            if move_index == pop_instance2.used_list[j].id:
                srf = copy.deepcopy(pop_instance2.used_list[j].surface)
                axis = copy.deepcopy(pop_instance2.used_list[j].center_line)
                srf.Transform(xf)
                axis.Transform(xf)

                list_srf.append(srf)
                list_axis.append(axis)
                list_section_length.append(pop_instance2.used_list[j].section_length)
                list_timber_num.append(pop_instance2.used_list[j].id)

    # 接触判定を行う。 TODO セグメントを増やすなどして精度を向上させる必要あり。
    for i in range(len(list_srf)):
        tim = list_axis[i]
        tim_end_1 = tim.PointAtEnd
        tim_start_1 = tim.PointAtStart
        tim_line = Rhino.Geometry.Line(tim_end_1, tim_start_1)

        intersection_flag = False
        connect_flag = False
        for j in range(len(already_regenerate_list)):
            for k in range(len(pop_instance1.used_list)):
                if already_regenerate_list[j] == pop_instance1.used_list[k].id:
                    tim_other = pop_instance1.used_list[k].center_line
                    tim_end = tim_other.PointAtEnd
                    tim_start = tim_other.PointAtStart
                    tim_other_line = Rhino.Geometry.Line(tim_end, tim_start)
                    distance = tim_line.MinimumDistanceTo(tim_other_line)
                    # print("distance", distance)
                    # if distance < list_section_length[i]/ 2 + pop_instance1.used_list[k].section_length:
                    if distance < 200:
                        intersection_flag = True
                        # print("intersection_distance", distance)

                        if 80 < distance < 150:
                            connect_flag = True
                            intersection_flag = False
                            partner_tim_name = already_regenerate_list[j]
                        break
                    else:
                        break

            if intersection_flag:
                break
        if intersection_flag:
            pass
        else:
            inherit_timber_id_list.append(list_timber_num[i])
            if connect_flag:
                connect_list.append([list_timber_num[i], partner_tim_name])

    return inherit_timber_id_list, connect_list


def decide_inheritance_tim_connected(pop_instance1, pop_instance2, already_regenerate_list, generate_range):
    """
    pop_2の中で継承する材を決定し、材の個体番号をreturnする。
    :param pop_instance1:
    :param pop_instance2:
    :param already_regenerate_list:
    :param generate_range:
    :return: 1; pop2の継承する材のID　2: 継承する材の内pop1に接合している材のIDと接合相手のID --> [接合している材のID, 接合している相手の材のID]
    """

    segment_num = 20

    inherit_timber_id_list = []
    connect_list = []

    # pop2をpop1の位置に動かすことで接触判定を行えるようにしている。
    move_pop2_num_list = []

    pop_num_1 = pop_instance1.population_num  # ttm change pop_index -> population_num
    pop_num_2 = pop_instance2.population_num
    num_range = pop_num_1 - pop_num_2

    move_from_p = Rhino.Geometry.Point3d(0, 0, 0)
    move_to_p = Rhino.Geometry.Point3d(num_range*generate_range*2, 0, 0)
    vec_move = move_to_p - move_from_p
    xf = Rhino.Geometry.Transform.Translation(vec_move)

    # すでに生成されている部材をのぞく部材IDを一旦リスト内に格納する。
    for i in range(len(pop_instance2.used_list)):
        if pop_instance2.used_list[i].id not in already_regenerate_list:
            move_pop2_num_list.append(pop_instance2.used_list[i].id)
        else:
            continue

    list_srf = []
    # list_axis = []
    list_section_length = []
    list_timber_num = []
    for i in range(len(move_pop2_num_list)):
        move_index = move_pop2_num_list[i]
        for j in range(len(pop_instance2.used_list)):
            if move_index == pop_instance2.used_list[j].id:
                srf = copy.deepcopy(pop_instance2.used_list[j].surface)
                # axis = copy.deepcopy(pop_instance2.used_list[j].center_line)
                srf.Transform(xf)
                # axis.Transform(xf)

                list_srf.append(srf)
                # list_axis.append(axis)
                # list_section_length.append(pop_instance2.used_list[j].section_length)
                list_timber_num.append(pop_instance2.used_list[j].id)

    # surfaceを用いた接触判定をおこなう。
    for i in range(len(list_srf)):
        srf = list_srf[i]
        tim1_segment_points, tim1_diameter = calculate_srf_segment_points(srf, segment_num)

        intersection_flag = False
        for j in range(len(already_regenerate_list)):
            for k in range(len(pop_instance1.used_list)):
                if already_regenerate_list[j] == pop_instance1.used_list[k].id:
                    srf_other = pop_instance1.used_list[k].surface
                    tim2_segment_points, tim2_diameter = calculate_srf_segment_points(srf_other, segment_num)

                    tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points,
                                                                            segment_num)

                    tim1_min_p = tim1_segment_points[tim1_index]
                    tim2_min_p = tim2_segment_points[tim2_index]
                    vec = tim1_min_p - tim2_min_p
                    length = vec.Length

                    judge_value = (tim1_diameter[tim1_index] / 2) + (tim2_diameter[tim2_index] / 2)

                    if length <= judge_value:
                        intersection_flag = True
                        partner_tim_name = already_regenerate_list[j]
                    else:
                        pass

                    break

            if intersection_flag:
                break
            else:
                continue

        if intersection_flag:
            inherit_timber_id_list.append(list_timber_num[i])
            connect_list.append([list_timber_num[i], partner_tim_name])
        else:
            pass

    return inherit_timber_id_list, connect_list


def move_and_pop_update_for_already(already_regenerate, pop_instance, generate_range, generation_num,
                         between_draw_rhino, main_loop, loop, list_temp_partner_tim):
    """
    そのまま継承する材をコピーする。
    :param already_regenerate: 次世代に継承する材がはいったリスト
    :param pop_instance: Generateインスタンス
    :param generate_range: 生成可能範囲
    :param generation_num: 現在の世代数
    :param between_draw_rhino: 描画する間隔
    :param main_loop: メインループの現在のカウント
    :param loop: 小ループの現在のカウント
    :param list_temp_partner_tim: パートナーが格納されているリスト
    :return: なし。
    """

    for i in range(len(already_regenerate)):
        success_flag = False
        for j in range(len(pop_instance.used_list)):
            if already_regenerate[i] == pop_instance.used_list[j].id:
                tim_move = pop_instance.used_list[j]

                pop_index = pop_instance.pop_index
                move_from = Rhino.Geometry.Point3d(pop_index * 2 * generate_range, 0, 0)
                move_to = Rhino.Geometry.Point3d(loop * generate_range * 2, -2 * generate_range, 0)
                # vec_move = rs.VectorCreate(move_to, move_from)
                vec_move = move_to - move_from
                SingleTimberMoveObjects(tim_move, vec_move, generation_num, main_loop, between_draw_rhino)

                success_flag = True
                break
            else:
                continue

        if not success_flag:
            input("in GA Method MovePopulationUpdate")

    # そのまま継承した材の接合関係をtemp_partner_timに入れる。
    # ------------------------------------------------------------------------------------------------------------------
    for i in range(len(already_regenerate)):
        tim_num = already_regenerate[i]
        for j in range(len(pop_instance.used_list)):
            if pop_instance.used_list[j].id == tim_num:
                tim_index = j
                break

        for j in range(len(pop_instance.used_list[tim_index].partner_tim)):
            if pop_instance.used_list[tim_index].partner_tim[j] in already_regenerate:
                list_temp_partner_tim[loop][tim_num].append(
                    pop_instance.used_list[tim_index].partner_tim[j])


def move_and_pop_update_for_inheritance(decide_inheritance_num_list, pop_instance1, pop_instance2, generate_range, generation_num,
                         between_draw_rhino, main_loop, loop, list_temp_partner_tim):

    for i in range(len(decide_inheritance_num_list)):
        success_flag = False
        for j in range(len(pop_instance1.used_list)):
            if decide_inheritance_num_list[i] == pop_instance1.used_list[j].id:
                tim_move = pop_instance1.used_list[j]

                pop_index1 = pop_instance1.pop_index
                pop_index2 = pop_instance2.pop_index

                move_from = Rhino.Geometry.Point3d(pop_index2 * 2 * generate_range, 0, 0)
                move_to = Rhino.Geometry.Point3d(loop * generate_range * 2, -2 * generate_range, 0)
                # vec_move = rs.VectorCreate(move_to, move_from)
                vec_move = move_to - move_from
                SingleTimberMoveObjects(tim_move, vec_move, generation_num, main_loop, between_draw_rhino)

                success_flag = True
                break
            else:
                continue

        if not success_flag:
            input("in GA Method MovePopulationUpdate")

    # そのまま継承した材の接合関係をtemp_partner_timに入れる。
    # ------------------------------------------------------------------------------------------------------------------
    for i in range(len(decide_inheritance_num_list)):
        tim_num = decide_inheritance_num_list[i]
        for j in range(len(pop_instance1.used_list)):
            if pop_instance2.used_list[j].id == tim_num:
                tim_index = j
                break

        for j in range(len(pop_instance2.used_list[tim_index].partner_tim)):
            if pop_instance2.used_list[tim_index].partner_tim[j] in decide_inheritance_num_list:
                list_temp_partner_tim[loop][tim_num].append(
                    pop_instance2.used_list[tim_index].partner_tim[j])


def RenewalInstanceInformationSameGeneration(pop_instance, temp_save_list_srf, temp_save_list_line, temp_save_list_domain,
                                             list_srf_temp, list_center_line_temp, list_select_domain_temp, loop):

    """
    同世代において、インスタンス情報を保存するためのメソッド
    :param pop_instance: Generateインスタンス
    :param temp_save_list_srf: 一時的に保存するために使用していたリスト
    :param temp_save_list_line: 一時的に使用するために使用していたリスト
    :param temp_save_list_domain: 一時的に使用するために使用していたリスト
    :param list_srf_temp: 同世代全体の情報を一時的に格納しておくためのリスト
    :param list_center_line_temp: 同世代全体の情報を一時的に格納しておくためのリスト
    :param list_select_domain_temp: 同世代全体の情報を一時的に格納しておくためのリスト
    :param loop: 少ループ
    :return:
    """
    for i in range(len(pop_instance.used_list)):
        name_tim = pop_instance.used_list[i].id

        temp_save_list_srf[loop][name_tim] = pop_instance.used_list[i].surface
        pop_instance.used_list[i].surface = None
        pop_instance.used_list[i].surface = list_srf_temp[i]

        temp_save_list_line[loop][name_tim] = pop_instance.used_list[i].center_line
        pop_instance.used_list[i].center_line = None
        pop_instance.used_list[i].center_line = list_center_line_temp[i]

        temp_save_list_domain[loop][name_tim].extend(
            pop_instance.used_list[i].select_domain_list)  # ttm add list_select
        pop_instance.used_list[i].select_domain_list = []
        pop_instance.used_list[i].select_domain_list.extend(list_select_domain_temp[i])


def RenewalInstanceInformation():
    # dicが入ったものを引数として扱うことはできるのだろうか。

    return None


def RenewalPop2(pop_instance1, pop_instance2, pop_2_inheritance_num):
    for i in range(len(pop_2_inheritance_num)):
        inheritance_num = pop_2_inheritance_num[i]
        for j in range(len(pop_instance1.used_list)):
            if pop_instance1.used_list[j].id == inheritance_num:
                for k in range(len(pop_instance2.used_list)):
                    if pop_instance2.used_list[k].id == inheritance_num:
                        pop_instance1.used_list[j].surface = copy.deepcopy(pop_instance2.used_list[k].surface)
                        pop_instance1.used_list[j].center_line = copy.deepcopy(pop_instance2.used_list[k].center_line)
                        pop_instance1.used_list[j].select_domain_list = copy.deepcopy(pop_instance2.used_list[k].select_domain_list)

                        # pop_instance1.used_list[j].partner_tim = []
                        # for l in range(len(pop_2_inheritance_num)):
                        #     if pop_2_inheritance_num[l] in pop_instance2.used_list[k].partner_tim:
                        #         pop_instance1.used_list[j].partner_tim.append(pop_2_inheritance_num[l])


def saveInstanceInformation(num_timber, pop_instance, list_srf_temp, list_center_line_temp, list_select_domain_temp):
    """
    指定された個体のサーフェス、軸線、接合に使用されているドメインを引数のリストに保存する。
    :param num_timber: 木材の本数
    :param pop_instance: Generateインスタンス
    :param list_srf_temp: 保存に使用するリスト
    :param list_center_line_temp: 保存に使用するリスト
    :param list_select_domain_temp: 保存に使用するリスト
    :return: なし。
    """
    for i in range(num_timber):
        timber_instance = pop_instance.used_list[i]
        CopyTimberObjects(timber_instance, list_srf_temp, list_center_line_temp)

    # select_domain_listの保存。　　使用されているドメインの一覧のこと
    for i in range(num_timber):
        list_select_domain_temp.append(pop_instance.used_list[i].select_domain_list)

    # return list_srf_temp, list_center_line_temp, list_select_domain_temp


def selectDomainRenewal(already_regenerate, num_timber, pop_instance):
    """
     select_domain_listの更新。　形態を引き継いでいる材の接合ドメインの更新を行う。前世代では使用していたが、空席になるドメインが生じるはずなので
    :param already_regenerate:
    :param num_timber:
    :param pop_instance:
    :return:
    """
    for i in range(len(already_regenerate)):
        for j in range(num_timber):
            if already_regenerate[i] == pop_instance.used_list[j].id:
                count_domain_loop = -1
                for _ in range(len(pop_instance.used_list[j].select_domain_list)):
                    count_domain_loop = count_domain_loop + 1
                    tim_name_domain = pop_instance.used_list[j].select_domain_list[count_domain_loop][1]
                    if tim_name_domain not in already_regenerate:
                        pop_instance.used_list[j].select_domain_list.pop(count_domain_loop)  # 削除する。
                        count_domain_loop = count_domain_loop - 1  # 次のループでも同じインデックスを使用するために


def selectDomainRenewal2(inheritance_num_list, num_timber, pop_instance1):
    # for i in range(len(inheritance_num_list)):
    #     inheritance_number = inheritance_num_list[i]
    #     for j in range(len(pop_instance2.used_list)):
    #         if pop_instance2.used_list[j].name == inheritance_number:
    #             for k in range(len(pop_instance2.used_list[j].select_domain_list)):
    #                 if pop_instance2.used_list[j].name == pop_instance2.used_list[j].select_domain_list[k][1]:
    #                     print()

     for i in range(len(inheritance_num_list)):
            for j in range(num_timber):
                if inheritance_num_list[i] == pop_instance1.used_list[j].id:
                    count_domain_loop = -1
                    for _ in range(len(pop_instance1.used_list[j].select_domain_list)):
                        count_domain_loop = count_domain_loop + 1
                        tim_name_domain = pop_instance1.used_list[j].select_domain_list[count_domain_loop][1]
                        if tim_name_domain not in inheritance_num_list:
                            pop_instance1.used_list[j].select_domain_list.pop(count_domain_loop)  # 削除する。
                            count_domain_loop = count_domain_loop - 1  # 次のループでも同じインデックスを使用するために


def SingleTimberMoveObjects(timber_instance, vector_move, generation_num, loop_num, between_draw_num):
    """
    オブジェクトをRhionCommonを使用して移動させるメソッド
    :param timber_instance: timberのインスタンス
    :param vector_move: 移動するためのベクトル
    :param generation_num: 現在の世代数
    :param loop_num: 小ループの数
    :param between_draw_num: 描画する間隔
    :return: なし。
    """
    # rs.MoveObject(timber_instance.center_line, vector_move)
    # rs.MoveObject(timber_instance.surface, vector_move)

    xf = Rhino.Geometry.Transform.Translation(vector_move)
    # print("timber_instance", timber_instance.center_line)
    # print("timber_instance", timber_instance.surface)
    if type(timber_instance.center_line) is list:
        timber_instance.center_line = timber_instance.center_line[0]
        timber_instance.center_line.Transform(xf)
    else:
        timber_instance.center_line.Transform(xf)

    if type(timber_instance.surface) is list:
        timber_instance.surface = timber_instance.surface[0]
        timber_instance.surface.Transform(xf)
    else:
        timber_instance.surface.Transform(xf)

    if generation_num - 1 == loop_num:
        scriptcontext.doc.Objects.AddBrep(timber_instance.surface)
        scriptcontext.doc.Objects.AddCurve(timber_instance.center_line)


def calculate_srf_segment_points(srf, segment_num):
    srf_domain_u = srf.Faces[0].Domain(0)
    srf_domain_v = srf.Faces[0].Domain(1)

    srf_domain_u_segment = (srf_domain_u[1] - srf_domain_u[0]) / segment_num
    srf_domain_v_segment = (srf_domain_v[1] - srf_domain_v[0]) / 10

    segment_points_list = []
    diameter_list = []
    for i in range(segment_num + 1):
        p1_u = srf_domain_u[0] + (srf_domain_u_segment * i)
        p1_v = srf_domain_v[0] + (srf_domain_v_segment * 0)

        p2_u = srf_domain_u[0] + (srf_domain_u_segment * i)
        p2_v = srf_domain_v[0] + (srf_domain_v_segment * 5)

        srf_point1 = srf.Faces[0].PointAt(p1_u, p1_v)
        srf_point2 = srf.Faces[0].PointAt(p2_u, p2_v)

        line = Rhino.Geometry.Line(srf_point2, srf_point1)
        diameter = line.Length

        center_p = line.PointAt(0.5)
        segment_points_list.append(center_p)
        diameter_list.append(diameter)

    return segment_points_list, diameter_list


def calculate_connect_part_indices(tim1_segment_points, tim2_segment_points, segment_num):
    between_length_list = []
    for i in range(len(tim1_segment_points)):
        tim1_p = tim1_segment_points[i]
        for j in range(len(tim2_segment_points)):
            tim2_p = tim2_segment_points[j]

            between_vec = tim2_p - tim1_p
            length = between_vec.Length
            between_length_list.append(length)

    length_min = min(between_length_list)
    index = between_length_list.index(length_min)

    tim1_index = index // (segment_num + 1)
    tim2_index = index % (segment_num + 1)

    return tim1_index, tim2_index


def transform_object_rhinocommon(object, vec_move):
    xf = Rhino.Geometry.Transform.Translation(vec_move)
    object.Transform(xf)

