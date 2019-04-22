# -*- coding: UTF-8 -*-

import random as rnd
# import copy
# import rhinoscriptsyntax as rs
# import Rhino
# import scriptcontext


def regenerate(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber, limit_degree,
               generation_num, main_loop, loop, between_draw_rhino, list_temp_partner_tim, mutation_ratio=3):
    '''
    再生成用の関数を埋め込むための関数
    :param already_regenerate_id:
    :param yet_regenerate_id:
    :param pop_1:
    :param pop_2:
    :param num_timber:
    :param limit_degree:
    :param generation_num:
    :param main_loop:
    :param loop:
    :param between_draw_rhino:
    :param list_temp_partner_tim:
    :param mutation_ratio:
    :return:
    '''

    regenerate_priory_small_partner(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber, limit_degree,
                                    generation_num, main_loop, loop, between_draw_rhino, list_temp_partner_tim,
                                    mutation_ratio)


def ReGeneratePhaseRelationship(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber, limit_degree, 
                                generation_num, main_loop, loop, between_draw_rhino, list_temp_partner_tim):

    """

    pop_2の個体の接合関係を継承する形で可能な限り再生成させるアルゴリズム。

    :param already_regenerate_id:
    :param yet_regenerate_id:
    :param pop_1:
    :param pop_2:
    :param num_timber:
    :param limit_degree:
    :param generation_num:
    :param main_loop:
    :param loop:
    :param between_draw_rhino:
    :param list_temp_partner_tim:
    :return:
    """

    flag_loop = True
    while_loop_count = -1
    avoid_infinite_loop = 0
    skip_count = 0
    while flag_loop:  # どの個体から再生成すればうまくいくか組み合わせなので

        # ループ終了判定
        if len(already_regenerate_id) == num_timber:
            break

        # 無限ループを避けるためのコード
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 1000:
            input("This is infinite loop in Regenerate near 475, please type ESC key")

        # yet_regenerate_id リストから材を選択するためのインデックス・カウント
        while_loop_count = while_loop_count + 1
        if while_loop_count >= len(yet_regenerate_id):
            while_loop_count = 0

        # 再生成の際に追加する材を選択する。
        tim1_name = yet_regenerate_id[while_loop_count]
        if tim1_name in already_regenerate_id:
            input("select_tim1 is wrong")

        # pop_1から選択した材と同じpop_2の材のpartnerを調べる。
        start_regeneration_flag = False
        for j in range(num_timber):
            timber_name2 = pop_2.used_list[j].name
            if tim1_name == timber_name2:
                partner_tim = pop_2.used_list[j].partner_tim
                start_regeneration_flag = True
                break
            else:
                continue
        if not start_regeneration_flag:
            print("start regeneration flag is not True")
            input("start regeneration flag is not True")

        # partne_timrのうちいくつの材が既に再生成されているか調べる。
        partner_regenerate = 0
        for j in range(len(partner_tim)):
            if partner_tim[j] in already_regenerate_id:
                partner_regenerate = partner_regenerate + 1

        # 追加する材のused_list内におけるインデックスを取得
        for j in range(len(pop_1.used_list)):
            if tim1_name == pop_1.used_list[j].name:
                tim1_index = j
                break

        # Mainアルゴリズム
        # partner_timの数とpartner_regenerateの数に応じて場合分け開始。
        # この場合わけ内部ではスキップされない。
        if len(partner_tim) == 1 and partner_regenerate == 1:

            # Alone再生成　already_regenerate_idが一つのときはどこかでcantileverを始めないと再生成が始まらない。
            if len(already_regenerate_id) == 1:
                for j in range(len(pop_1.used_list)):
                    if already_regenerate_id[0] == pop_1.used_list[j].name:
                        tim2_index = j
                        break
                cantilever_flag = False
                cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id, limit_degree,
                                                           generation_num, main_loop, between_draw_rhino)
                if cantilever_flag:
                    # if input_flag:
                    #     input("cantilever success near in 540")
                    skip_count = 0
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                    yet_regenerate_id.pop(while_loop_count)

                    # 後ほどpartner_timを更新するため for cantilever
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    input("something happen in near line 546")

            # Alone再生成ではないとき
            if len(already_regenerate_id) > 1:

                # tim2 のused_listにおけるインデックスの検索
                for j in range(len(already_regenerate_id)):
                    if partner_tim[0] == already_regenerate_id[j]:
                        index_already = j
                        break

                for j in range(len(pop_1.used_list)):
                    if already_regenerate_id[index_already] == pop_1.used_list[j].name:
                        tim2_index = j
                        break

                # flag = True
                # bridge_fail_counter = 0
                # # while flag
                success_flag = False
                for j in range(len(already_regenerate_id)):

                    # もしtim2_indexと同じならスキップする。
                    if j == index_already:
                        continue

                    # すべてのalready_regenerate_id timber に対してbridgeを試す。
                    # はじめの方のインデックスの材に再生成しやすいというバイアスがかかってる気がする。
                    for k in range(len(pop_1.used_list)):
                        if already_regenerate_id[j] == pop_1.used_list[k].name and tim2_index != k:
                            tim3_index = k

                            success_flag = False
                            success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index,
                                                                already_regenerate_id, limit_degree, generation_num,
                                                                main_loop, between_draw_rhino)

                            if success_flag:
                                break

                    if success_flag:
                        break

                # 成功したときとしていないときの操作
                if success_flag:
                    # if input_flag:
                    #     input("bridge success near line 581")  # OK
                    skip_count = 0
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)
                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near line 597")
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                    else:
                        input("something happen near line:591")
                        break

        elif len(partner_tim) == 1 and partner_regenerate == 0:
            if skip_count < len(yet_regenerate_id):
                skip_count = skip_count + 1
                continue

            else:
                tim2_name = already_regenerate_id[0]
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim2_name:
                        tim2_index = j
                        break

                cantilever_flag = False
                cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                           limit_degree, generation_num, main_loop, between_draw_rhino)
                if cantilever_flag:
                    # if input_flag:
                    #     input("cantilever success near in 728")
                    skip_count = 0
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                    yet_regenerate_id.pop(while_loop_count)

                    # 後ほどpartner_timを更新するため for cantilever
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    input("something happen near in 741")

        elif len(partner_tim) == 2 and partner_regenerate == 0:
            if skip_count < len(yet_regenerate_id):
                skip_count = skip_count + 1
                continue

            else:
                tim2_name = already_regenerate_id[0]
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim2_name:
                        tim2_index = j
                        break

                cantilever_flag = False
                cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                           limit_degree, generation_num, main_loop, between_draw_rhino)
                if cantilever_flag:
                    # if input_flag:
                    #     input("cantilever success near in 763")
                    skip_count = 0
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                    yet_regenerate_id.pop(while_loop_count)

                    # 後ほどpartner_timを更新するため for cantilever
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    input("something happen near in 776")

        elif len(partner_tim) == 2 and partner_regenerate == 1:

            # skip_countがyet_regenerate_idと同じになるということは、生成していない材すべての材においてスキップが適用されたということ。その場合cantileverでもやむなし。
            if skip_count >= len(yet_regenerate_id):
                if len(already_regenerate_id) == 1:
                    for j in range(len(pop_1.used_list)):
                        if already_regenerate_id[0] == pop_1.used_list[j].name:
                            tim2_index = j
                            break

                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)
                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near line 629")  # OK
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                else:
                    for j in range(len(already_regenerate_id)):
                        if partner_tim[0] == already_regenerate_id[j]:
                            index_already = j
                            break
                        if partner_tim[1] == already_regenerate_id[j]:
                            index_already = j
                            break

                    for j in range(len(pop_1.used_list)):
                        if already_regenerate_id[index_already] == pop_1.used_list[j].name:
                            tim2_index = j
                            break

                    # flag = True
                    # bridge_fail_counter = 0
                    # while flag:
                    success_flag = False
                    for j in range(len(already_regenerate_id)):

                        # もしtim2_indexと同じならスキップする。
                        if j == index_already:
                            continue

                        for k in range(len(pop_1.used_list)):
                            if already_regenerate_id[j] == pop_1.used_list[k].name and tim2_index != j:
                                tim3_index = k

                                success_flag = False
                                success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index,
                                                                    already_regenerate_id, limit_degree,
                                                                    generation_num, main_loop, between_draw_rhino)

                                if success_flag:
                                    # input("bridge success near line 666")  # OK
                                    break

                        if success_flag:
                            break

                    if success_flag:
                        # if input_flag:
                        #     input("bridge success near line 676")  # OK
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for bridge
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim3_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                    else:
                        cantilever_flag = False
                        cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                                   limit_degree, generation_num, main_loop,
                                                                   between_draw_rhino)
                        if cantilever_flag:
                            # if input_flag:
                            #     input("cantilever success near line 682")
                            skip_count = 0
                            yet_regenerate_id.pop(while_loop_count)
                            already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                            # 後ほどpartner_timを更新するため for cantilever
                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim2_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                                pop_1.used_list[tim1_index].name)

                            continue
                        else:
                            input("something happen near line 688")
            else:
                skip_count = skip_count + 1
                continue

        elif len(partner_tim) == 2 and partner_regenerate == 2:
            # はじめにpartner_timの2つの材を対象に再生成を試す。
            for j in range(len(pop_1.used_list)):
                if partner_tim[0] == pop_1.used_list[j].name:
                    tim2_index = j
                    break

            for j in range(len(pop_1.used_list)):
                if partner_tim[1] == pop_1.used_list[j].name:
                    tim3_index = j
                    break
            # if input_flag:
            #     input("bridge start near line 734")  # OK
            success_flag = False
            success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                limit_degree, generation_num, main_loop, between_draw_rhino)

            # first try で成功すればここで終了。
            if success_flag:
                # if input_flag:
                #     input("bridge success near line 710")  # OK
                skip_count = 0
                yet_regenerate_id.pop(while_loop_count)
                already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                # 後ほどpartner_timを更新するため for bridge
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim2_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim3_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                    pop_1.used_list[tim1_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                    pop_1.used_list[tim1_index].name)

                continue

            else:
                # if input_flag:
                #     input("bridge fail near line 747")

                for j in range(len(already_regenerate_id)):
                    # もしtim2と同じならスキップする。
                    if already_regenerate_id[j] == pop_1.used_list[tim2_index].name:
                        continue

                    for k in range(len(pop_1.used_list)):
                        if already_regenerate_id[j] == pop_1.used_list[k].name and tim2_index != k:
                            tim3_index = k
                            # if input_flag:
                            #     input("bridge start near line 760")
                            success_flag = False
                            success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index,
                                                                already_regenerate_id, limit_degree, generation_num,
                                                                main_loop, between_draw_rhino)

                            break

                    if success_flag:
                        break
                    else:
                        continue
                        # if input_flag:
                        #     input("bridge fail near line 770")

                if success_flag:
                    # if input_flag:
                    #     input("bridge success near line 735")
                    skip_count = 0
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    # 厳密にはtim3を使用する可能性も含まれるが省かれている。
                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)
                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near line 746")
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                    else:
                        input("something happen near line 752")
                        break

        elif len(partner_tim) > 2 and partner_regenerate == 0:
            if skip_count < len(yet_regenerate_id):
                skip_count = skip_count + 1
                continue

            else:
                tim2_name = already_regenerate_id[0]
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim2_name:
                        tim2_index = j
                        break

                cantilever_flag = False
                cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                           limit_degree, generation_num, main_loop, between_draw_rhino)
                if cantilever_flag:
                    # if input_flag:
                    #     input("cantilever success near in 1008")
                    skip_count = 0
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                    yet_regenerate_id.pop(while_loop_count)

                    # 後ほどpartner_timを更新するため for cantilever
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    input("something happen near in 1021")

        elif len(partner_tim) > 2 and partner_regenerate == 1:

            if skip_count >= len(yet_regenerate_id):
                if len(already_regenerate_id) == 1:

                    for j in range(len(pop_1.used_list)):
                        if already_regenerate_id[0] == pop_1.used_list[j].name:
                            tim2_index = j
                            break

                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)

                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near line 776")  # OK
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                    else:
                        input("something happen near line 782")
                        break

                if len(already_regenerate_id) > 1:
                    flag_A = False
                    for j in range(len(partner_tim)):
                        for k in range(len(already_regenerate_id)):
                            if partner_tim[j] == already_regenerate_id[k]:
                                flag_A = True
                                tim2_name = partner_tim[j]
                                break
                        if flag_A:
                            for l in range(len(pop_1.used_list)):
                                if pop_1.used_list[l].name == tim2_name:
                                    tim2_index = l
                                    break
                            break

                    for j in range(len(already_regenerate_id)):
                        tim3_name = already_regenerate_id[j]
                        if tim3_name == tim2_name:
                            continue

                        for k in range(len(pop_1.used_list)):
                            if tim3_name == pop_1.used_list[k].name:
                                tim3_index = k
                                break

                        # if input_flag:
                        #     input("bridge start near line 846") # OK
                        success_flag = False
                        success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                            limit_degree, generation_num, main_loop, between_draw_rhino)

                        if success_flag:
                            break
                        else:
                            # if input_flag:
                            #     input("bridge fail near line 854")
                            continue

                    if success_flag:
                        # if input_flag:
                        #     input("bridge success near line 820")  # OK
                        skip_count = 0
                        yet_regenerate_id.pop(while_loop_count)
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                        # 後ほどpartner_timを更新するため for bridge
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim3_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue
                    else:

                        # input("something happen near line 858")  # TODO
                        cantilever_flag = False
                        cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                                   limit_degree, generation_num, main_loop,
                                                                   between_draw_rhino)
                        if cantilever_flag:
                            # input("cantilever success near line 830")
                            skip_count = 0
                            yet_regenerate_id.pop(while_loop_count)
                            already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim2_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                                pop_1.used_list[tim1_index].name)

                            continue
                        else:
                            input("something happen near line 836")

            else:
                skip_count = skip_count + 1
                continue

        elif len(partner_tim) > 2 and partner_regenerate == 2:
            if skip_count < len(yet_regenerate_id):

                # すべての組み合わせを実行できる仕様に変更する必要あり。とりあえずpartnerの材のみで再生成を試す。
                flag_1 = False
                for j in range(len(already_regenerate_id)):
                    for k in range(len(partner_tim)):
                        if partner_tim[k] == already_regenerate_id[j]:
                            tim2_name = already_regenerate_id[j]
                            flag_1 = True
                            break
                    if flag_1:
                        break
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim2_name:
                        tim2_index = j
                        break

                flag_2 = False
                for j in range(len(already_regenerate_id)):
                    for k in range(len(partner_tim)):
                        if partner_tim[k] != tim2_name and partner_tim[k] == already_regenerate_id[j]:
                            tim3_name = already_regenerate_id[j]
                            flag_2 = True
                            break
                    if flag_2:
                        break
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim3_name:
                        tim3_index = j
                        break

                # if input_flag:
                #     input("bridge start near line 912")  # OK  重い場合が多い気がする fail することがおかしい
                success_flag = False
                success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                    limit_degree, generation_num, main_loop, between_draw_rhino)

                if success_flag:
                    # if input_flag:
                    #     input("bridge success near line 895")  # OK
                    skip_count = 0
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    # if input_flag:
                    #     input("bridge fail near line 920")
                    # # bridge_conduct = False  # 一度ここのBridgeを失敗したら、現在の個体の再生成においてはこの場合分けをスキップする。
                    skip_count = skip_count + 1
                    continue

            elif skip_count >= len(yet_regenerate_id):
                flag_1 = False
                for j in range(len(already_regenerate_id)):
                    for k in range(len(partner_tim)):
                        if partner_tim[k] == already_regenerate_id[j]:
                            tim2_name = k
                            flag_1 = True
                            break
                    if flag_1:
                        break
                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == tim2_name:
                        tim2_index = j
                        break

                flag = True
                loop_counter = 0
                for j in range(len(already_regenerate_id)):
                    if already_regenerate_id[j] != tim2_name:
                        tim3_name = already_regenerate_id[j]
                        for k in range(len(pop_1.used_list)):
                            if pop_1.used_list[k].name == tim3_name:
                                tim3_index = k
                                break

                        # if input_flag:
                        #     input("bridge start near line 954")
                        success_flag = False
                        success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                            limit_degree, generation_num, main_loop, between_draw_rhino)
                        if success_flag:
                            # if input_flag:
                            #     input("bridge success near line 977")
                            skip_count = 0
                            yet_regenerate_id.pop(while_loop_count)
                            already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                            # 後ほどpartner_timを更新するため for bridge
                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim2_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim3_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                                pop_1.used_list[tim1_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                                pop_1.used_list[tim1_index].name)

                            break
                        else:

                            # if input_flag:
                            #     input("bridge fail near line 966")
                            continue

                    else:
                        continue

                if success_flag:
                    continue
                else:
                    tim2_name = rnd.choice(already_regenerate_id)
                    for j in range(len(pop_1.used_list)):
                        if pop_1.used_list[j].name == tim2_name:
                            tim2_index = j
                            break

                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)
                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near in 1381")
                        skip_count = 0
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                        yet_regenerate_id.pop(while_loop_count)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue

        elif len(partner_tim) > 2 and partner_regenerate > 2:
            if skip_count < len(yet_regenerate_id):
                # for j in range(len(already_regenerate_id)):
                flag = True
                # count = -1
                count_partner = -1
                loop_avoid = 0
                while flag:  # TODO infinite loop occur
                    count_partner = count_partner + 1
                    if count_partner >= len(partner_tim):
                        count_partner = 0

                    loop_avoid = loop_avoid + 1
                    if loop_avoid > 50:
                        input("i can not understand infinite loop occur near line 853")
                        break

                    # tim_choice = rnd.choice(partner_tim)

                    tim_choice = partner_tim[count_partner]
                    for j in range(len(already_regenerate_id)):
                        if tim_choice == already_regenerate_id[j]:
                            index_already_1 = j
                            flag = False
                            break
                        else:
                            continue

                # for j in range(len(already_regenerate_id)):
                flag = True
                # count = -1
                count_partner = -1
                loop_avoid = 0
                while flag:
                    loop_avoid = loop_avoid + 1
                    if loop_avoid > 50:  # TODO modify
                        input("infinite loop occur near line 871")

                    # count = count +1
                    # if count >= len(already_regenerate_id):
                    #     count = 0
                    # tim_choice = rnd.choice(partner_tim)
                    count_partner = count_partner + 1
                    if count_partner >= len(partner_tim):
                        count_partner = 0

                    tim_choice = partner_tim[count_partner]
                    for j in range(len(already_regenerate_id)):
                        if tim_choice == already_regenerate_id[j] and j != index_already_1:
                            index_already_2 = j
                            flag = False
                            break

                if index_already_1 == index_already_2:
                    input("something happen near line 1086")

                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == already_regenerate_id[index_already_1]:
                        tim2_index = j
                        break

                for j in range(len(pop_1.used_list)):
                    if pop_1.used_list[j].name == already_regenerate_id[index_already_2]:
                        tim3_index = j
                        break

                # if input_flag:
                #     input("bridge start near line 1075 ")  # OK
                success_flag = False
                success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                    limit_degree, generation_num, main_loop, between_draw_rhino)

                if success_flag:
                    # if input_flag:
                    #     input("bridge success near line 1103")  # OK
                    skip_count = 0
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    # if input_flag:
                    #     input("bridge fail near line 1040")
                    # bridge_conduct = False  # 一度ここのBridgeを失敗したら、現在の個体の再生成においてはこの場合分けをスキップする。
                    skip_count = skip_count + 1
                    continue

            elif skip_count >= len(yet_regenerate_id):
                # for j in range(len(already_regenerate_id)):
                flag = True
                count = -1
                loop_avoid = 0
                while flag:
                    # print("partner_tim", partner_tim)
                    # print("already_regenerate_id", already_regenerate_id)
                    loop_avoid = loop_avoid + 1
                    if loop_avoid > 50:
                        input("infinite loop occur near line 853")
                        break
                    count = count + 1
                    if count >= len(partner_tim):
                        count = 0

                    tim_choice = partner_tim[count]
                    flag_success = False
                    for j in range(len(already_regenerate_id)):
                        if already_regenerate_id[j] == tim_choice:
                            tim2_name = already_regenerate_id[j]
                            flag_success = True
                            break
                        else:
                            continue
                    if flag_success:
                        break

                # partner_timを起点にbridgeを試みる。
                for j in range(len(partner_tim)):
                    tim2_name = partner_tim[j]
                    if tim2_name not in already_regenerate_id:
                        continue

                    for k in range(len(already_regenerate_id)):
                        tim3_name = already_regenerate_id[k]
                        if tim2_name == tim3_name:
                            continue

                        for l in range(len(pop_1.used_list)):
                            if pop_1.used_list[l].name == tim2_name:
                                tim2_index = l
                                break

                        for l in range(len(pop_1.used_list)):
                            if pop_1.used_list[l].name == tim3_name:
                                tim3_index = l
                                break

                        # if input_flag:
                        #     input("bridge start near line 1126")
                        success_flag = False
                        success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                            limit_degree, generation_num, main_loop, between_draw_rhino)

                        if success_flag:
                            # if input_flag:
                            #     input("bridge success near line 1103")  # OK
                            skip_count = 0
                            yet_regenerate_id.pop(while_loop_count)
                            already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                            # 後ほどpartner_timを更新するため for bridge
                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim2_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                                pop_1.used_list[tim3_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                                pop_1.used_list[tim1_index].name)
                            list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                                pop_1.used_list[tim1_index].name)

                            break
                        else:
                            # if input_flag:
                            #     input("bridge fail near line 1092")
                            continue

                    if success_flag:
                        break
                    else:
                        continue

                if success_flag:
                    continue
                else:
                    # TODO Bridgeを他の材で行う。
                    input("something happen 1328 in ReGenerate")

        elif len(partner_tim) == 0:  # TODO　この場合分けはそもそも生じていいたぐいじゃない気がする。---> ideaとしては殺す個体として設定する。
            if len(already_regenerate_id) == 1:
                for j in range(len(pop_1.used_list)):
                    if already_regenerate_id[0] == pop_1.used_list[j].name:
                        tim2_index = j
                        break
                cantilever_flag = False
                cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id, limit_degree,
                                                           generation_num, main_loop, between_draw_rhino)
                if cantilever_flag:
                    # if input_flag:
                    #     input("cantilever success near in 1313")
                    skip_count = 0
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                    yet_regenerate_id.pop(while_loop_count)

                    # 後ほどpartner_timを更新するため for cantilever
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                    continue
                else:
                    input("something happen near 1399")

            else:
                for j in range(len(already_regenerate_id)):
                    flag_select_tim2 = False
                    for k in range(len(pop_1.used_list)):
                        if already_regenerate_id[j] == pop_1.used_list[k].name:
                            tim2_name = already_regenerate_id[j]
                            tim2_index = k
                            flag_select_tim2 = True
                            break

                    if not flag_select_tim2:
                        input("something happen in near 1509")

                    for k in range(len(already_regenerate_id)):
                        flag_select_tim3 = False
                        if already_regenerate_id[k] != tim2_name:
                            for l in range(len(pop_1.used_list)):
                                if pop_1.used_list[l].name == already_regenerate_id[k]:
                                    tim3_index = l
                                    flag_select_tim3 = True
                                    break
                            if flag_select_tim3:
                                break
                        else:
                            continue

                    if not flag_select_tim3:
                        input("something_happen 1526")

                    success_flag = False
                    success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                        limit_degree, generation_num, main_loop, between_draw_rhino)

                    if success_flag:
                        break
                    else:
                        continue

                    # if success_flag:
                    #     break

                if success_flag:
                    skip_count = 0
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    continue
                else:
                    tim2_name = rnd.choice(already_regenerate_id)
                    for j in range(len(pop_1.used_list)):
                        if pop_1.used_list[j].name == tim2_name:
                            tim2_index = j
                            break

                    cantilever_flag = False
                    cantilever_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                               limit_degree, generation_num, main_loop,
                                                               between_draw_rhino)
                    if cantilever_flag:
                        # if input_flag:
                        #     input("cantilever success near in 1381")
                        skip_count = 0
                        already_regenerate_id.append(pop_1.used_list[tim1_index].name)
                        yet_regenerate_id.pop(while_loop_count)

                        # 後ほどpartner_timを更新するため for cantilever
                        list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                            pop_1.used_list[tim2_index].name)
                        list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                            pop_1.used_list[tim1_index].name)

                        continue

        else:
            input("missing the pattern in case analysis")
            break

    # print("avoid_infinite_loop", avoid_infinite_loop)


def ReGenerateRandom(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber, limit_degree, generation_num,
                     main_loop, loop, between_draw_rhino, list_temp_partner_tim):
    """

    完全にランダムに材を選択しbridgeしている。

    :param already_regenerate_id:
    :param yet_regenerate_id:
    :param pop_1:
    :param pop_2:
    :param num_timber:
    :param limit_degree:
    :param generation_num:
    :param main_loop:
    :param loop:
    :param between_draw_rhino:
    :param list_temp_partner_tim:
    :return:
    """
    flag_loop = True
    while_loop_count = -1
    avoid_infinite_loop = 0

    while flag_loop:  # どの個体から再生成すればうまくいくか組み合わせなので

        # ループ終了判定
        if len(already_regenerate_id) == num_timber:
            break

        # 無限ループを避けるためのコード
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 1000:
            input("This is infinite loop in Regenerate near 475, please type ESC key")

        # yet_regenerate_id リストから材を選択するためのインデックス・カウント
        while_loop_count = while_loop_count + 1
        if while_loop_count >= len(yet_regenerate_id):
            while_loop_count = 0

        # 再生成の際に追加する材を選択する。
        tim1_name = yet_regenerate_id[while_loop_count]
        if tim1_name in already_regenerate_id:
            input("select_tim1 is wrong")

        # 追加する材のused_list内におけるインデックスを取得
        for j in range(len(pop_1.used_list)):
            if tim1_name == pop_1.used_list[j].name:
                tim1_index = j
                break

        for k in range(100):
            random_select_index_1 = rnd.randint(0, len(already_regenerate_id) - 1)
            tim2_name = already_regenerate_id[random_select_index_1]

            flag = True
            avoid_infinite_loop_1 = 0
            while flag:
                avoid_infinite_loop_1 = avoid_infinite_loop_1 + 1
                random_select_index_2 = rnd.randint(0, len(already_regenerate_id) - 1)
                if random_select_index_1 != random_select_index_2:
                    flag = False

                if avoid_infinite_loop_1 >= 1000:
                    input("something happen in ReGenerate line 1096")

            tim3_name = already_regenerate_id[random_select_index_2]

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim2_name:
                    tim2_index = l
                    break

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim3_name:
                    tim3_index = l
                    break

            success_flag = False
            success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id, limit_degree,
                                                generation_num, main_loop, between_draw_rhino)

            if success_flag:
                yet_regenerate_id.pop(while_loop_count)
                already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                # 後ほどpartner_timを更新するため for bridge
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim2_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim3_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                    pop_1.used_list[tim1_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                    pop_1.used_list[tim1_index].name)
                break
            else:
                continue

        if not success_flag:
            input("can not regenerate near line:1135")


def ReGenerateRandomPrioritySmallPartner(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber,
                                         limit_degree, generation_num, main_loop, loop, between_draw_rhino,
                                         list_temp_partner_tim):
    """

    partner_tim（材と接合関係をもつ材）が少ない材を優先的に対象と見なしbridgeさせる。

    :param already_regenerate_id:
    :param yet_regenerate_id:
    :param pop_1:
    :param pop_2:
    :param num_timber:
    :param limit_degree:
    :param generation_num:
    :param main_loop:
    :param loop:
    :param between_draw_rhino:
    :param list_temp_partner_tim:
    :return:
    """
    flag_loop = True
    while_loop_count = -1
    avoid_infinite_loop = 0

    while flag_loop:  # どの個体から再生成すればうまくいくか組み合わせなので

        # ループ終了判定
        if len(already_regenerate_id) == num_timber:
            break

        # 無限ループを避けるためのコード
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 1000:
            input("This is infinite loop in Regenerate near 475, please type ESC key")

        # yet_regenerate_id リストから材を選択するためのインデックス・カウント
        while_loop_count = while_loop_count + 1
        if while_loop_count >= len(yet_regenerate_id):
            while_loop_count = 0

        # 再生成の際に追加する材を選択する。
        tim1_name = yet_regenerate_id[while_loop_count]
        if tim1_name in already_regenerate_id:
            input("select_tim1 is wrong")

        # 追加する材のused_list内におけるインデックスを取得
        for j in range(len(pop_1.used_list)):
            if tim1_name == pop_1.used_list[j].name:
                tim1_index = j
                break

        for k in range(150):

            # パートナーが最小の部材から順に再生成を試みる。
            partner_num = []
            for l in range(len(already_regenerate_id)):
                tim_id = already_regenerate_id[l]
                for m in range(len(pop_1.used_list)):
                    if tim_id == pop_1.used_list[m].name:
                        partner_num.append(len(pop_1.used_list[m].partner_tim))
                        break
            tim_index = [i for i, x in enumerate(partner_num) if x == min(partner_num)]
            select_tim_index = rnd.choice(tim_index)
            # select_tim_index = partner_num.index(min(partner_num))
            # if k > 30:
            #     select_tim_index = partner_num.index(min(partner_num) + 1)
            # elif k > 50:
            #     select_tim_index = partner_num.index(min(partner_num) + 2)
            # elif k > 80:
            #     raise ValueError('not working well, RegenerateRandomPrioritySmallPartner method in Regenerate')
            if k > 100:
                tim_index = [i for i, x in enumerate(partner_num) if x == min(partner_num)+1]
                select_tim_index = rnd.choice(tim_index)

            tim2_name = already_regenerate_id[select_tim_index]

            flag = True
            avoid_infinite_loop_1 = 0
            while flag:
                avoid_infinite_loop_1 = avoid_infinite_loop_1 + 1
                random_select_index_2 = rnd.randint(0, len(already_regenerate_id) - 1)
                if select_tim_index != random_select_index_2:
                    flag = False

                if avoid_infinite_loop_1 >= 1000:
                    input("something happen in ReGenerate line 1096")

            tim3_name = already_regenerate_id[random_select_index_2]

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim2_name:
                    tim2_index = l
                    break

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim3_name:
                    tim3_index = l
                    break

            success_flag = False
            success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id, limit_degree,
                                                generation_num, main_loop, between_draw_rhino)

            if success_flag:
                yet_regenerate_id.pop(while_loop_count)
                already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                # 後ほどpartner_timを更新するため for bridge
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim2_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                    pop_1.used_list[tim3_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                    pop_1.used_list[tim1_index].name)
                list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                    pop_1.used_list[tim1_index].name)
                break
            else:
                continue

        if not success_flag:
            input("can not regenerate near line:1135")


def regenerate_priory_small_partner(already_regenerate_id, yet_regenerate_id, pop_1, pop_2, num_timber, limit_degree,
                                    generation_num, main_loop, loop, between_draw_rhino, list_temp_partner_tim,
                                    mutation_ratio=3):
    """

    partner_tim（材と接合関係をもつ材）が少ない材を優先的に対象と見なしbridgeさせる。

    :param already_regenerate_id:
    :param yet_regenerate_id:
    :param pop_1:
    :param pop_2:
    :param num_timber:
    :param limit_degree:
    :param generation_num:
    :param main_loop:
    :param loop:
    :param between_draw_rhino:
    :param list_temp_partner_tim:
    :return:
    """
    flag_loop = True
    while_loop_count = -1
    avoid_infinite_loop = 0

    while flag_loop:  # どの個体から再生成すればうまくいくか組み合わせなので

        # ループ終了判定
        if len(already_regenerate_id) == num_timber:
            break

        # 無限ループを避けるためのコード
        avoid_infinite_loop = avoid_infinite_loop + 1
        if avoid_infinite_loop > 1000:
            input("This is infinite loop in Regenerate near 475, please type ESC key")

        # yet_regenerate_id リストから材を選択するためのインデックス・カウント
        while_loop_count = while_loop_count + 1
        if while_loop_count >= len(yet_regenerate_id):
            while_loop_count = 0

        # 再生成の際に追加する材を選択する。
        tim1_name = yet_regenerate_id[while_loop_count]
        if tim1_name in already_regenerate_id:
            input("select_tim1 is wrong")

        # 追加する材のused_list内におけるインデックスを取得
        for j in range(len(pop_1.used_list)):
            if tim1_name == pop_1.used_list[j].name:
                tim1_index = j
                break

        for k in range(150):

            # パートナーが最小の部材から順に再生成を試みる。できないならランダムに
            partner_num = []
            for l in range(len(already_regenerate_id)):
                tim_id = already_regenerate_id[l]
                for m in range(len(pop_1.used_list)):
                    if tim_id == pop_1.used_list[m].name:
                        partner_num.append(len(pop_1.used_list[m].partner_tim))
                        break
            tim_index = [i for i, x in enumerate(partner_num) if x == min(partner_num)]
            tim2_select_index = rnd.choice(tim_index)
            # select_tim_index = partner_num.index(min(partner_num))
            # if k > 30:
            #     select_tim_index = partner_num.index(min(partner_num) + 1)
            # elif k > 50:
            #     select_tim_index = partner_num.index(min(partner_num) + 2)
            # elif k > 80:
            #     raise ValueError('not working well, RegenerateRandomPrioritySmallPartner method in Regenerate')
            if 100 >= k > 50:
                tim_index = [i for i, x in enumerate(partner_num) if x == min(partner_num) + 1]
                if tim_index:
                    tim2_select_index = rnd.choice(tim_index)
                else:
                    tim_index = [i for i, x in enumerate(partner_num) if x == min(partner_num) + 2]
                    if tim_index:
                        tim2_select_index = rnd.choice(tim_index)
                    else:
                        tim2_select_index = rnd.randint(0, len(already_regenerate_id) - 1)

            elif k > 100:
                tim2_select_index = rnd.randint(0, len(already_regenerate_id) - 1)

            tim2_name = already_regenerate_id[tim2_select_index]

            flag = True
            avoid_infinite_loop_1 = 0
            while flag:
                avoid_infinite_loop_1 = avoid_infinite_loop_1 + 1

                # はじめの方は極力partnerの少ない部材から生成するようにする。
                if len(tim_index) >= 2 and k < len(tim_index) * 2:
                    for l in range(len(tim_index)):
                        tim3_select_index = tim_index[l]
                        if tim3_select_index != tim2_select_index:
                            flag = False
                            break
                        else:
                            pass
                else:
                    tim3_select_index = rnd.randint(0, len(already_regenerate_id) - 1)
                    if tim2_select_index != tim3_select_index:
                        flag = False

                if avoid_infinite_loop_1 >= 1000:
                    raise ValueError('infinite loop')

            tim3_name = already_regenerate_id[tim3_select_index]

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim2_name:
                    tim2_index = l
                    break

            for l in range(len(pop_1.used_list)):
                if pop_1.used_list[l].name == tim3_name:
                    tim3_index = l
                    break

            # mutation として確率的にcantileverを行う。
            seed_rnd = rnd.randint(0, 100)
            if seed_rnd <= mutation_ratio:
                mutation = True
            else:
                mutation = False

            if mutation:
                success_flag = False
                success_flag = pop_1.cantilever_specify(tim2_index, tim1_index, already_regenerate_id,
                                                        limit_degree, generation_num, main_loop, between_draw_rhino)
            else:
                success_flag = False
                success_flag = pop_1.bridge_specify(tim2_index, tim3_index, tim1_index, already_regenerate_id,
                                                    limit_degree, generation_num, main_loop, between_draw_rhino)

            if success_flag:
                if mutation:
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)

                else:
                    yet_regenerate_id.pop(while_loop_count)
                    already_regenerate_id.append(pop_1.used_list[tim1_index].name)

                    # 後ほどpartner_timを更新するため for bridge
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim2_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim1_index].name].append(
                        pop_1.used_list[tim3_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim2_index].name].append(
                        pop_1.used_list[tim1_index].name)
                    list_temp_partner_tim[loop][pop_1.used_list[tim3_index].name].append(
                        pop_1.used_list[tim1_index].name)
                break
            else:
                continue

        if not success_flag:
            input("can not regenerate near line:1135")
