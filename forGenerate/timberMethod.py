# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs
import Rhino
import rhinoscript.utility as rhutil
import scriptcontext


def distanceBetweenTimber(timber1, timber2):
    """
    木材同士の間隔の最小値を計算。
    :param timber1: 木材のオブジェクト1
    :param timber2: 木材のオブジェクト2
    :return: なし
    """

    center_line_tim1 = timber1.center_line
    center_line_tim2 = timber2.center_line
    start_point_tim1 = rs.CurveStartPoint(center_line_tim1, -1)
    end_point_tim1 = rs.CurveEndPoint(center_line_tim1, -1)
    center_point_tim1 = rs.CurveMidPoint(center_line_tim1, -1)
    start_point_tim2 = rs.CurveStartPoint(center_line_tim2, -1)
    end_point_tim2 = rs.CurveEndPoint(center_line_tim2, -1)
    center_point_tim2 = rs.CurveMidPoint(center_line_tim2, -1)


    cul_dis = []
    dis1 = rs.Distance(start_point_tim1, start_point_tim2)
    dis2 = rs.Distance(start_point_tim1, end_point_tim2)
    dis3 = rs.Distance(start_point_tim1, center_point_tim2)
    dis4 = rs.Distance(end_point_tim1, start_point_tim2)
    dis5 = rs.Distance(end_point_tim1, end_point_tim2)
    dis6 = rs.Distance(end_point_tim1, center_point_tim2)
    dis7 = rs.Distance(center_point_tim1, start_point_tim2)
    dis8 = rs.Distance(center_point_tim1, end_point_tim2)
    dis0 = rs.Distance(center_point_tim1, center_point_tim2)

    cul_dis.append(dis0)
    cul_dis.append(dis1)
    cul_dis.append(dis2)
    cul_dis.append(dis3)
    cul_dis.append(dis4)
    cul_dis.append(dis5)
    cul_dis.append(dis6)
    cul_dis.append(dis7)
    cul_dis.append(dis8)

    distance = min(cul_dis)

    # 材同士が接触しているならば、distanceの代わりに100を入力する。接触していなければ、distanceをappendする。
    # check = rs.IntersectBreps(timber1.surface, timber2.surface)
    # if check != None:
    #     timber1.tim_distance[timber2.name] = []
    #     timber2.tim_distance[timber1.name] = []
    #
    #     timber1.tim_distance[timber2.name].append(100)
    #     timber2.tim_distance[timber1.name].append(100)

    # else:
    timber1.tim_distance[timber2.name] = []
    timber2.tim_distance[timber1.name] = []

    timber1.tim_distance[timber2.name].append(distance)
    timber2.tim_distance[timber1.name].append(distance)




def distanceBetweenTimber_RhinoCommon(timber1, timber2):
    ###
    # timber1:  instance of timber
    # timber2:  instance of timber
    ###

    # center_line_tim1 = timber1.center_line
    # center_line_tim2 = timber2.center_line
    # start_point_tim1 = rs.CurveStartPoint(center_line_tim1, -1)
    # end_point_tim1 = rs.CurveEndPoint(center_line_tim1, -1)
    # center_point_tim1 = rs.CurveMidPoint(center_line_tim1, -1)
    # start_point_tim2 = rs.CurveStartPoint(center_line_tim2, -1)
    # end_point_tim2 = rs.CurveEndPoint(center_line_tim2, -1)
    # center_point_tim2 = rs.CurveMidPoint(center_line_tim2, -1)

    tim1_domain = timber1.center_line.Domain
    tim2_domain = timber2.center_line.Domain
    start_point_tim1 = timber1.center_line.PointAt(tim1_domain[0])
    end_point_tim1 = timber1.center_line.PointAt(tim1_domain[1])
    center_point_tim1 = timber1.center_line.PointAt(tim1_domain[0] + (tim1_domain[1] - tim1_domain[0])/2)
    start_point_tim2 = timber2.center_line.PointAt(tim2_domain[0])
    end_point_tim2 = timber2.center_line.PointAt(tim2_domain[1])
    center_point_tim2 = timber2.center_line.PointAt(tim2_domain[0] + (tim2_domain[1] - tim2_domain[0])/2)


    cul_dis = []
    # dis1 = rs.Distance(start_point_tim1, start_point_tim2)
    # dis2 = rs.Distance(start_point_tim1, end_point_tim2)
    # dis3 = rs.Distance(start_point_tim1, center_point_tim2)
    # dis4 = rs.Distance(end_point_tim1, start_point_tim2)
    # dis5 = rs.Distance(end_point_tim1, end_point_tim2)
    # dis6 = rs.Distance(end_point_tim1, center_point_tim2)
    # dis7 = rs.Distance(center_point_tim1, start_point_tim2)
    # dis8 = rs.Distance(center_point_tim1, end_point_tim2)
    # dis0 = rs.Distance(center_point_tim1, center_point_tim2)

    dis0 = (center_point_tim1 - center_point_tim2).Length
    dis1 = (start_point_tim1 - start_point_tim2).Length
    dis2 = (start_point_tim1 - end_point_tim2).Length
    dis3 = (start_point_tim1 - center_point_tim2).Length
    dis4 = (end_point_tim1 - start_point_tim2).Length
    dis5 = (end_point_tim1 - end_point_tim2).Length
    dis6 = (end_point_tim1 - center_point_tim2).Length
    dis7 = (center_point_tim1 - start_point_tim2).Length
    dis8 = (center_point_tim1 - end_point_tim2).Length


    # dic = {}
    # for i in range(9):
    #     dic['dis' + str(i)] = i
    #
    # for i in range(9):
    #     cul_dis.append(dic['dis' + str(i)])

    cul_dis.append(dis0)
    cul_dis.append(dis1)
    cul_dis.append(dis2)
    cul_dis.append(dis3)
    cul_dis.append(dis4)
    cul_dis.append(dis5)
    cul_dis.append(dis6)
    cul_dis.append(dis7)
    cul_dis.append(dis8)

    distance = min(cul_dis)

    # 材同士が接触しているならば、distanceの代わりに100を入力する。接触していなければ、distanceをappendする。
    # check = rs.IntersectBreps(timber1.surface, timber2.surface)
    # if check != None:
    #     timber1.tim_distance[timber2.name] = []
    #     timber2.tim_distance[timber1.name] = []
    #
    #     timber1.tim_distance[timber2.name].append(100)
    #     timber2.tim_distance[timber1.name].append(100)

    # else:
    timber1.tim_distance[timber2.name] = []
    timber2.tim_distance[timber1.name] = []

    timber1.tim_distance[timber2.name].append(distance)
    timber2.tim_distance[timber1.name].append(distance)


def initDistanceBetweenTimber(timber1, timber2):
    center_line_tim1 = timber1.center_line
    center_line_tim2 = timber2.center_line
