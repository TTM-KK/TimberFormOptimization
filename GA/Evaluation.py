# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs
# import time
# import copy
# import random as rnd
# import sys
import Rhino
import scriptcontext


def pop_evaluation(tim_number, instance_pop):
    '''
    使用する評価関数を埋め込む用の関数
    :param tim_number:
    :param instance_pop:
    :return:
    '''
    evaluate_value = pop_height_evaluate(tim_number, instance_pop)
    # evaluate_value = partner_num_evaluate(tim_number, instance_pop, 2, 8)
    return evaluate_value


def overlap_num2(tim_number, instance_pop):
    '''
    intersectionを使用していないため実行速度は早い。精度に問題はある。
    :param tim_number:
    :param instance_pop:
    :return:
    '''
    intersect_num = 0
    for i in range(tim_number):
        tim = instance_pop.used_list[i].center_line
        tim_end_1 = tim.PointAtEnd
        tim_start_1 = tim.PointAtStart
        tim_line = Rhino.Geometry.Line(tim_end_1, tim_start_1)
        for j in range(tim_number):
            if j == i:
                continue
            else:
                tim_other = instance_pop.used_list[j].center_line
                tim_end = tim_other.PointAtEnd
                tim_start = tim_other.PointAtStart
                tim_other_line = Rhino.Geometry.Line(tim_end, tim_start)

                distance = tim_line.MinimumDistanceTo(tim_other_line)

                if distance < instance_pop.used_list[i].section_length/2 + instance_pop.used_list[j]\
                        .section_length/2 + 50:
                    intersect_num = intersect_num + 1
                else:
                    # intersect_num = intersect_num + 1
                    continue

    return intersect_num


def partner_num_evaluate(tim_number, instance_pop, num_partner_low, num_partner_high):
    """
    partner_timの数が指定された領域内にあれば点数を与える評価関数。
    :param tim_number:
    :param instance_pop:
    :param num_partner_low:
    :param num_partner_high:
    :return:
    """
    evaluate_point = 0
    for i in range(tim_number):
        tim_partner_num = len(instance_pop.used_list[i].partner_tim)
        if num_partner_low <= tim_partner_num <= num_partner_high:
            evaluate_point = evaluate_point + 1

    return evaluate_point


def pop_height_evaluate(tim_number, instance_pop):
    '''
    個体の高さを評価値として算出する。
    :param tim_number:
    :param instance_pop:
    :return: 高さの最大値
    '''
    tim_height = []
    for i in range(tim_number):
        center_line = instance_pop.used_list[i].center_line
        end_p = center_line.PointAtEnd
        str_p = center_line.PointAtStart
        if end_p[2] > str_p[2]:
            tim_height.append(end_p[2])
        else:
            tim_height.append(str_p[2])

    most_height_value = max(tim_height)

    return most_height_value
