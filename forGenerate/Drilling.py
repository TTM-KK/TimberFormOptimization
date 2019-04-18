# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs


def drilling(curve_list, surface1, used_line2, unused_line, closest_p):
    split_num = 4
    point_list = []

    if not curve_list:
        # print("tan2: There is not curve")
        return

    if len(curve_list) != 1:
        cur_length = []
        length = 0

        # Message: unable to convert 0530c598-26e0-4ff5-a15a-389bd334aeff into Curve geometry
        for i in range(0, len(curve_list)):
            if rs.IsCurve(curve_list[i]):
                length = rs.CurveLength(curve_list[i])

        cur_length.append(length)

        curve_index = cur_length.index(max(cur_length))
        curve = curve_list[curve_index]

    else:
        curve = curve_list


    domain = rs.CurveDomain(curve)
    t = (domain[1] - domain[0]) / split_num

    for i in range(0, 4):
        dt = t * i
        point = rs.EvaluateCurve(curve, dt)
        point_list.append(point)


    # 直線の交点を求める
    line1 = rs.AddLine(point_list[0], point_list[2])
    line2 = rs.AddLine(point_list[1], point_list[3])

    vec1 = rs.VectorCreate(point_list[2], point_list[0])
    vec2 = rs.VectorCreate(point_list[3], point_list[1])

    cross = rs.VectorCrossProduct(vec1, vec2)
    normal = rs.VectorUnitize(cross)

    curveOnsurface1 = rs.ProjectCurveToSurface(line1, surface1, normal)
    curveOnsurface2 = rs.ProjectCurveToSurface(line2, surface1, normal)

    if len(curveOnsurface1) == 0:  # ttm add プロジェクションされていない可能性があるため
        new_vec1 = rs.VectorReverse(normal)
        curveOnsurface1 = rs.ProjectCurveToSurface(line1, surface1, new_vec1)

    if len(curveOnsurface2) == 0:  # ttm add プロジェクションされていない可能性があるため
        new_vec2 = rs.VectorReverse(normal)
        curveOnsurface2 = rs.ProjectCurveToSurface(line2, surface1, new_vec2)

    if len(curveOnsurface1) == 2 and len(curveOnsurface2) == 2:

        intersection1 = rs.CurveCurveIntersection(curveOnsurface1[0], curveOnsurface2[0])
        intersection2 = rs.CurveCurveIntersection(curveOnsurface1[1], curveOnsurface2[1])

        # 条件分岐
        if intersection1 is None:
            intersection1 = rs.CurveCurveIntersection(curveOnsurface1[0], line2)

            if intersection1 is None:
                intersection1 = rs.CurveCurveIntersection(curveOnsurface2[0], line1)

            if intersection1 is None:
                intersection1 = rs.CurveCurveIntersection(curveOnsurface1[1], line2)

            if intersection1 is None:
                intersection1 = rs.CurveCurveIntersection(curveOnsurface2[1], line1)

            if intersection1 is None:
                intersection1 = rs.CurveCurveIntersection(curveOnsurface1[0], curveOnsurface2[1])
                intersection2 = rs.CurveCurveIntersection(curveOnsurface1[1], curveOnsurface2[0])

    else:
        # normal_reverce = rs.VectorReverse(normal)
        # curveOnsurface1 = rs.ProjectCurveToSurface(line1, surface1, normal)
        # curveOnsurface2 = rs.ProjectCurveToSurface(line2, surface1, normal)

        intersection1 = rs.CurveCurveIntersection(curveOnsurface1[0], curveOnsurface2[0])  #index out of range: 0
        intersection2 = None

    # console
    # print("intersection1: %s" % (intersection1))
    # print("intersection2: %s" % (intersection2))

    if intersection1 is None and intersection2 is None:
        center_point = rs.CurveMidPoint(curveOnsurface1[0])

    elif intersection2 is None:
        center_point = intersection1[0][1]

    else:
        center_point1 = intersection1[0][1]
        center_point2 = intersection2[0][1]

        dis1 = rs.Distance(center_point1, closest_p)
        dis2 = rs.Distance(center_point2, closest_p)

        if dis1 > dis2:
            center_point = center_point2
        else:
            center_point = center_point1


    parameter1 = rs.CurveClosestPoint(unused_line, center_point)
    parameter2 = rs.CurveClosestPoint(used_line2, center_point)

    point1 = rs.EvaluateCurve(unused_line, parameter1)    # base point
    point2 = rs.EvaluateCurve(used_line2, parameter2)     # base point

    # ドリル穴のベクトルを生成
    drill_line = rs.AddLine(point1, point2)
    rs.CurveArrows(drill_line, 2)
    rs.ExtendCurveLength(drill_line, 0, 2, 100)



    drill_vec = rs.VectorCreate(point2, point1)

    # 外積計算より回転軸を生成
    start_point = rs.CurveStartPoint(unused_line)
    end_point = rs.CurveEndPoint(unused_line)

    distance1 = rs.Distance(start_point, center_point)
    distance2 = rs.Distance(end_point, center_point)

    if distance1 > distance2:
        select_point = end_point
    else:
        select_point = start_point


    # 回転平面を定義する
    origin_point = center_point
    x_point = point1
    y_point = select_point

    new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
    rs.ViewCPlane(None, new_plane)

    rotate_p = origin_point

    vec1 = rs.VectorCreate(x_point, rotate_p)
    vec2 = rs.VectorCreate(y_point, rotate_p)

    cross = rs.VectorCrossProduct(vec1, vec2)
    cross_unit = rs.VectorUnitize(cross)
    rotate_vec = rs.VectorScale(cross_unit, 100)    # Message: Could not convert None to a Vector3d

    # 描画
    # new_rotate_axis = AddVector(center_point, rotate_vector)
    # rotate_axis = AddVector(rotate_p, rotate_vec)
    # rs.AddPoint(point1)
    # rs.AddPoint(point2)
    # rs.AddPoint(center_point)

    # object削除
    rs.DeleteObject(line1)
    rs.DeleteObject(line2)
    for i in range(0, len(curveOnsurface1)):
        rs.DeleteObject(curveOnsurface1[i])
    for i in range(0, len(curveOnsurface2)):
        rs.DeleteObject(curveOnsurface2[i])


    # 平面をもとのxy平面に戻す
    origin_point = (0, 0, 0)
    x_point = (100, 0, 0)
    y_point = (0, 100, 0)
    new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
    rs.ViewCPlane(None, new_plane)


    # 戻り値(ドリルライン、ドリルベクトル、回転軸、回転軸点)
    return drill_line, drill_vec, rotate_vec, center_point


def AddVector(base, vec):
    tip = rs.PointAdd(base, vec)
    line = rs.AddLine(base, tip)
    rs.CurveArrows(line, 2)

    return line







