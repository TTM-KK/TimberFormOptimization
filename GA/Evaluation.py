# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs
# import time
# import copy
# import random as rnd
# import sys
import Rhino
import scriptcontext


def pop_evaluation(tim_number, instance_pop, generation_count, generate_range, generation_num):
    '''
    使用する評価関数を埋め込む用の関数
    :param tim_number: 個体に使用している部材の数
    :param instance_pop: Generateクラスのインスタンス
    :param generation_count: 現在の世代数
    :param generation_num: 全体の個体数
    :return:　評価値
    '''
    evaluate_value = pop_dome_evaluate(tim_number, instance_pop, generation_count, generate_range, generation_num)
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


def pop_dome_evaluate(tim_number, instance_pop, generation_count, generate_range, generation_num):
    '''

    :param tim_number: timberの数
    :param instance_pop:  Generateクラスのインスタンス
    :param generation_count: 現在の世代。
    :param generate_range: 個体間の距離。
    :param generation_num: 全体の個体数。
    :return: 範囲に入っていない部材の数。
    '''

    p = {}
    p[0] = Rhino.Geometry.Point3d(750, 750, 0)
    p[1] = Rhino.Geometry.Point3d(2250, 750, 0)
    p[2] = Rhino.Geometry.Point3d(2250, 2250, 0)
    p[3] = Rhino.Geometry.Point3d(750, 2250, 0)

    p[4] = Rhino.Geometry.Point3d(750, 750, 1500)
    p[5] = Rhino.Geometry.Point3d(2250, 750, 1500)
    p[6] = Rhino.Geometry.Point3d(2250, 2250, 1500)
    p[7] = Rhino.Geometry.Point3d(750, 2250, 1500)

    points_list = []
    for i in range(8):
        points_list.append(p[i])

    brep = Rhino.Geometry.Brep.CreateFromBox(points_list)

    copy_from = Rhino.Geometry.Point3d(0, 0, 0)
    copy_to = Rhino.Geometry.Point3d((generate_range * 2) * instance_pop.population_id,
                                     (-generate_range * 2) * (generation_count + 1), 0)
    vec_move = copy_to - copy_from

    xf = Rhino.Geometry.Transform.Translation(vec_move)
    brep.Transform(xf)

    if generation_num == generation_count:
        rs.AddLayer('dome_box')
        box = scriptcontext.doc.Objects.AddBrep(brep)
        rs.ObjectLayer(box, 'dome_box')

    evaluate_point = 0
    for i in range(tim_number):
        curve = instance_pop.used_list[i].center_line

        curve = rs.coercecurve(curve)

        end = curve.PointAtEnd
        start = curve.PointAtStart

        rc, mid_parameter = curve.NormalizedLengthParameter(0.5)

        mid = curve.PointAt(mid_parameter)

        end_p_check = brep.IsPointInside(end, Rhino.RhinoMath.SqrtEpsilon, True)
        start_p_check = brep.IsPointInside(start, Rhino.RhinoMath.SqrtEpsilon, True)
        mid_p_check = brep.IsPointInside(mid, Rhino.RhinoMath.SqrtEpsilon, True)

        if end_p_check or start_p_check or mid_p_check:
            pass
        else:
            evaluate_point += 1

    return evaluate_point
