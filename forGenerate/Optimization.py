# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs
from Timber import *
import time


def optimization(used_centerP, used_surfaceP, used_surface, unused_surface,
                 unused_line, unused_poly, unused_mark_line, tolerance):

    start_time = time.time()

    vector = rs.VectorCreate(used_surfaceP, used_centerP)
    normal = rs.VectorUnitize(vector)
    vec_length = rs.VectorScale(normal, 0.01)
    vec_reverse = rs.VectorReverse(normal)
    vec_reverse = rs.VectorScale(vec_reverse, 0.1)

    # 描画
    # AddVector(used_centerP, vector)
    # AddVector(used_centerP, vec_reverse)


    # 接触判定
    for i in range(200):

        curve = rs.IntersectBreps(used_surface, unused_surface)

        if i == 199:
            # print("Can not Optimization tan1")
            if curve:
                for k in range(len(curve)):
                    rs.DeleteObject(curve[k])

            # run time console
            end_time = time.time()
            optimization_run_time = end_time - start_time
            # print("-------------------------------------------------------")
            # print("optimization Run time: %s" % optimization_run_time)

            return False


        # timberが接触していない場合
        if curve is None:
            rs.MoveObject(unused_surface, vec_reverse)
            rs.MoveObject(unused_line, vec_reverse)
            rs.MoveObject(unused_poly, vec_reverse)
            rs.MoveObject(unused_mark_line[0], vec_reverse)
            rs.MoveObject(unused_mark_line[1], vec_reverse)


        # timberが接触している場合
        else:

            length = 0

            for j in range(0, len(curve)):
                if rs.IsCurve(curve[j]):
                    length = length + rs.CurveLength(curve[j])
                else:
                    rs.MoveObject(unused_surface, vec_length)
                    rs.MoveObject(unused_line, vec_length)
                    rs.MoveObject(unused_poly, vec_length)
                    rs.MoveObject(unused_mark_line[0], vec_length)
                    rs.MoveObject(unused_mark_line[1], vec_length)
                    continue

            # console
            # print("curve length[%s]: %s | vec length: %s" % (i, length, vec_length))

            # 接合条件を満たした場合
            if length < tolerance:
                # print("-------------------------------------------------------")
                # print("tan1 <count: %s | curve length: %s>" % (i, length))

                # run time console
                end_time = time.time()
                optimization_run_time = end_time - start_time
                # print("optimization Run time: %s" % optimization_run_time)

                return curve

            # 接合条件を満たさない場合
            else:
                rs.MoveObject(unused_surface, vec_length)
                rs.MoveObject(unused_line, vec_length)
                rs.MoveObject(unused_poly, vec_length)
                rs.MoveObject(unused_mark_line[0], vec_length)
                rs.MoveObject(unused_mark_line[1], vec_length)

                # オフセットする大きさを更新
                if length < 45:
                    vec_length = rs.VectorScale(normal, 0.05)
                elif length < 60:
                    vec_length = rs.VectorScale(normal, 0.55)
                elif length < 80:
                    vec_length = rs.VectorScale(normal, 0.75)
                elif length < 120:
                    vec_length = rs.VectorScale(normal, 2.5)
                elif length < 200:
                    vec_length = rs.VectorScale(normal, 3.5)
                else:
                    vec_length = rs.VectorScale(normal, 8.0)

                # objectを削除
                for k in range(0, len(curve)):
                    rs.DeleteObject(curve[k])

                if i == 199:
                    # print("Can not Optimization tan1")
                    if curve:
                        for k in range(0, len(curve)):
                            rs.DeleteObject(curve[k])

                    # run time console
                    end_time = time.time()
                    optimization_run_time = end_time - start_time
                    # print("-------------------------------------------------------")
                    # print("optimization Run time: %s" % optimization_run_time)

                    return False




# 回転の面積適化(最小化) TODO アルゴリズム要確認
def optimization_rotate(_origin_point, _x_point, _y_point, _unused_srf, _unused_line, _unused_polyline, _unused_mark_line,
                        _used_srf1, unused_timber, tolerance):

    start_time = time.time()

    # 初期変数
    origin_point = _origin_point
    x_point = _x_point
    y_point = _y_point

    unused_srf = _unused_srf
    unused_line = _unused_line
    unused_polyline = _unused_polyline
    unused_mark_line = _unused_mark_line

    used_srf1 = _used_srf1

    angle1 = 0.1
    angle2 = -0.03
    curve_length = []
    count1 = 0
    angle2_flag = False
    end_joint_count = 0


    # 回転平面を定義する
    new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
    rs.ViewCPlane(None, new_plane)

    rotate_p = origin_point

    vec1 = rs.VectorCreate(x_point, rotate_p)
    vec2 = rs.VectorCreate(y_point, rotate_p)

    cross = rs.VectorCrossProduct(vec1, vec2)
    cross_unit = rs.VectorUnitize(cross)
    rotate_vec = rs.VectorScale(cross_unit, 100)

    # 描画
    # rotate_axis = AddVector(rotate_p, rotate_vec)


    # print("-------------------------------------------------------")

    # 衝突判定
    for i in range(200):

        curve = rs.IntersectBreps(unused_srf, used_srf1)

        # もし接触しなかった場合
        if curve is None:

            curve_length = []

            if i == 0:
                angle2_flag = True
                angle2 = -1.0

            if i == 1:
                angle = (angle1 * -1.1)
                rs.RotateObject(unused_srf, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_line, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_polyline, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_mark_line[0], rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_mark_line[1], rotate_p, angle, rotate_vec)

            if i == 199:
                print("tan2: Can not optimize")
                # input("Can not optimize")

                # object削除
                if curve:
                    for k in range(0, len(curve)):
                        rs.DeleteObject(curve[k])

                # 平面をもとのxy平面に戻す
                origin_point = (0, 0, 0)
                x_point = (100, 0, 0)
                y_point = (0, 100, 0)
                new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
                rs.ViewCPlane(None, new_plane)

                # run time console
                end_time = time.time()
                optimization_rotate_run_time = end_time - start_time
                # print("---------------------------------------------------")
                # print("optimization_rotate Run time: %s" % optimization_rotate_run_time)

                return False

            # console
            # print("There is not curve[%s] angle2: %s" % (i, angle2))

            rs.RotateObject(unused_srf, rotate_p, angle2, rotate_vec)
            rs.RotateObject(unused_line, rotate_p, angle2, rotate_vec)
            rs.RotateObject(unused_polyline, rotate_p, angle2, rotate_vec)
            rs.RotateObject(unused_mark_line[0], rotate_p, angle2, rotate_vec)
            rs.RotateObject(unused_mark_line[1], rotate_p, angle2, rotate_vec)

            count1 = count1 + 1

            # もし20回連続で接触しない場合、回転方向を逆転する
            if count1 == 10 and angle2_flag:
                angle2 = angle2 * -1.0

                angle = 10 * angle2
                rs.RotateObject(unused_srf, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_line, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_polyline, rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_mark_line[0], rotate_p, angle, rotate_vec)
                rs.RotateObject(unused_mark_line[1], rotate_p, angle, rotate_vec)

                angle2_flag = False

            continue

        # もし接触した場合
        else:

            length = 0

            for j in range(0, len(curve)):
                if rs.IsCurve(curve[j]):
                    length = length + rs.CurveLength(curve[j])
                else:
                    rs.RotateObject(unused_srf, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_line, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_polyline, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_mark_line[0], rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_mark_line[1], rotate_p, angle1, rotate_vec)
                    continue

            # 接点2の接触部の長さを格納する
            curve_length.append(length)

            # もし衝突交線の値が大きくなる場合、回転の方向を逆転する
            if len(curve_length) == 5:
                if curve_length[0] < curve_length[1] < curve_length[2] < curve_length[3] < curve_length[4]:

                    angle1 = angle1 * -1.0

                    # print("update angle1")
                    # print("angle1: %s" % angle1)

                    angle = 3.0 * angle1
                    rs.RotateObject(unused_srf, rotate_p, angle, rotate_vec)
                    rs.RotateObject(unused_line, rotate_p, angle, rotate_vec)
                    rs.RotateObject(unused_polyline, rotate_p, angle, rotate_vec)
                    rs.RotateObject(unused_mark_line[0], rotate_p, angle, rotate_vec)
                    rs.RotateObject(unused_mark_line[1], rotate_p, angle, rotate_vec)

                curve_length = []


            # 接合条件を満たした場合
            if length < tolerance:
                select_curve = curve[0]
                reference_point = createMidPointFromCurve(select_curve)
                check_domain = unused_timber.judgeSurfaceDomain(reference_point)

                # もし接触部が端部(domainが0か8の時)
                if check_domain == 0 or check_domain == 8:
                    rs.RotateObject(unused_srf, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_line, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_polyline, rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_mark_line[0], rotate_p, angle1, rotate_vec)
                    rs.RotateObject(unused_mark_line[1], rotate_p, angle1, rotate_vec)

                    end_joint_count = end_joint_count + 1

                    if end_joint_count == 2:
                        # print("tan2: Can not optimize(joint is ends)")

                        # run time console
                        end_time = time.time()
                        optimization_rotate_run_time = end_time - start_time
                        # print("---------------------------------------------------")
                        # print("optimization_rotate Run time: %s" % optimization_rotate_run_time)

                        return False

                    continue

                else:
                    # print("tan2 <count: %s | curve_length = %s>" % (i, length))

                    # 平面をもとのxy平面に戻す
                    origin_point = (0, 0, 0)
                    x_point = (100, 0, 0)
                    y_point = (0, 100, 0)
                    new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
                    rs.ViewCPlane(None, new_plane)

                    # run time console
                    end_time = time.time()
                    optimization_rotate_run_time = end_time - start_time
                    # print("optimization_rotate Run time: %s" % optimization_rotate_run_time)

                    return curve


            # 接合条件を満たさなかった場合
            else:

                # angleを更新
                if length < 45:
                    if angle1 > 0:
                        angle1 = 0.05
                    else:
                        angle1 = -0.05

                elif length < 60:
                    if angle1 > 0:
                        angle1 = 0.25
                    else:
                        angle1 = -0.25

                elif length < 70:
                    if angle1 > 0:
                        angle1 = 0.35
                    else:
                        angle1 = -0.35

                elif length < 100:
                    if angle1 > 0:
                        angle1 = 0.65
                    else:
                        angle1 = -0.65

                elif length < 120:
                    if angle1 > 0:
                        angle1 = 1.75
                    else:
                        angle1 = -1.75

                else:
                    if angle1 > 0:
                        angle1 = 2.0
                    else:
                        angle1 = -2.0

                rs.RotateObject(unused_srf, rotate_p, angle1, rotate_vec)
                rs.RotateObject(unused_line, rotate_p, angle1, rotate_vec)
                rs.RotateObject(unused_polyline, rotate_p, angle1, rotate_vec)
                rs.RotateObject(unused_mark_line[0], rotate_p, angle1, rotate_vec)
                rs.RotateObject(unused_mark_line[1], rotate_p, angle1, rotate_vec)

                # print("curve length[%s]: %s | angle1: %s" % (i, length, angle1))

                # object削除
                for k in range(0, len(curve)):
                    rs.DeleteObject(curve[k])

                if i == 199:
                    # print("tan2: Can not optimize")

                    if curve:
                        for k in range(0, len(curve)):
                            rs.DeleteObject(curve[k])

                    # 平面をもとのxy平面に戻す
                    origin_point = (0, 0, 0)
                    x_point = (100, 0, 0)
                    y_point = (0, 100, 0)
                    new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
                    rs.ViewCPlane(None, new_plane)

                    # run time console
                    end_time = time.time()
                    optimization_rotate_run_time = end_time - start_time
                    # print("---------------------------------------------------")
                    # print("optimization_rotate Run time: %s" % optimization_rotate_run_time)

                    return False





def optimization_bridge(_unused_srf, _unused_line, _unused_poly, _unused_mark_line,
                        _used_srf1, _used_srf2, _rotate_point1, _rotate_point2,
                        _rotate_axis1, _rotate_axis2, _move_vec1, _move_vec2, tolerance):

    start_time = time.time()

    unused_surface = _unused_srf
    unused_line = _unused_line
    unused_polyline = _unused_poly
    unused_mark_line = _unused_mark_line

    used_surface1 = _used_srf1
    used_surface2 = _used_srf2

    rotate_point1 = _rotate_point1
    rotate_point2 = _rotate_point2

    rotate_axis1 = _rotate_axis1
    rotate_axis2 = _rotate_axis2

    angle1 = -0.01
    angle2 = -0.01

    move_vec1 = _move_vec1
    move_vec2 = _move_vec2

    normal1 = rs.VectorUnitize(move_vec1)
    normal2 = rs.VectorUnitize(move_vec2)

    vec_length1 = rs.VectorScale(normal1, 0.1)
    vec_length2 = rs.VectorScale(normal2, 0.1)

    vec_reverse1 = rs.VectorReverse(vec_length1)
    vec_reverse2 = rs.VectorReverse(vec_length2)

    curve_length1 = []
    curve_length2 = []

    count1 = 0
    count2 = 0


    # 衝突判定
    for i in range(200):

        curve1 = rs.IntersectBreps(used_surface1, unused_surface)
        curve2 = rs.IntersectBreps(used_surface2, unused_surface)

        # 最適化できなかった場合
        if i == 199:
            # print("-------------------------------------------------------")
            # print("Can not Optimization bridge")

            # run time console
            end_time = time.time()
            optimization_bridge_run_time = end_time - start_time
            # print("---------------------------------------------------")
            # print("optimization_bridge Run time: %s" % optimization_bridge_run_time)

            return False


        # 接点1でも接点2でも接していない時
        if curve1 is None and curve2 is None:

            rs.MoveObject(unused_surface, vec_length1)
            rs.MoveObject(unused_line, vec_length1)
            rs.MoveObject(unused_polyline, vec_length1)
            rs.MoveObject(unused_mark_line[0], vec_length1)
            rs.MoveObject(unused_mark_line[1], vec_length1)

            continue

        # 接点2では接しているが接点1では接していない時
        if curve1 is None:
            # rs.MoveObject(unused_surface, vec_reverse)
            # rs.MoveObject(unused_line, vec_reverse)
            # rs.MoveObject(unused_poly, vec_reverse)

            rs.RotateObject(unused_surface, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_line, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_polyline, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_mark_line[0], rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_mark_line[1], rotate_point2, angle1, rotate_axis2)

            if curve2:
                for k in range(0, len(curve2)):
                    rs.DeleteObject(curve2[k])

            count1 = count1 + 1

            # もし5回連続で接触しない場合、回転方向を逆転する
            if count1 == 5:
                angle1 = angle1 * -1.0

                angle = 5.0 * angle1
                rs.RotateObject(unused_surface, rotate_point2, angle, rotate_axis2)
                rs.RotateObject(unused_line, rotate_point2, angle, rotate_axis2)
                rs.RotateObject(unused_polyline, rotate_point2, angle, rotate_axis2)
                rs.RotateObject(unused_mark_line[0], rotate_point2, angle, rotate_axis2)
                rs.RotateObject(unused_mark_line[1], rotate_point2, angle, rotate_axis2)

            continue

        # 接点1では接しているが接点2では接していない時
        if curve2 is None:
            # rs.MoveObject(unused_surface, vec_length)
            # rs.MoveObject(unused_line, vec_length)
            # rs.MoveObject(unused_poly, vec_length)

            rs.RotateObject(unused_surface, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_line, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_polyline, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_mark_line[0], rotate_point1, angle2,rotate_axis1)
            rs.RotateObject(unused_mark_line[1], rotate_point1, angle2,rotate_axis1)

            if curve1:
                for k in range(0, len(curve1)):
                    rs.DeleteObject(curve1[k])

            count2 = count2 + 1

            # もし5回連続で接触しない場合、回転方向を逆転する
            if count2 == 5:
                angle2 = angle2 * -1.0

                angle = 5.0 * angle2
                rs.RotateObject(unused_surface, rotate_point1, angle, rotate_axis1)
                rs.RotateObject(unused_line, rotate_point1, angle, rotate_axis1)
                rs.RotateObject(unused_polyline, rotate_point1, angle, rotate_axis1)
                rs.RotateObject(unused_mark_line[0], rotate_point1, angle, rotate_axis1)
                rs.RotateObject(unused_mark_line[1], rotate_point1, angle, rotate_axis1)

            continue


        # どちらも接触している場合
        length1 = 0
        length2 = 0

        for j in range(0, len(curve1)):
            if rs.IsCurve(curve1[j]):
                length1 = length1 + rs.CurveLength(curve1[j])
            else:
                rs.RotateObject(unused_surface, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_line, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_polyline, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_mark_line[0], rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_mark_line[1], rotate_point1, angle2, rotate_axis1)
                continue

        for j in range(0, len(curve2)):
            if rs.IsCurve(curve2[j]):
                length2 = length2 + rs.CurveLength(curve2[j])
            else:
                rs.RotateObject(unused_surface, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_line, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_polyline, rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_mark_line[0], rotate_point1, angle2, rotate_axis1)
                rs.RotateObject(unused_mark_line[1], rotate_point1, angle2, rotate_axis1)
                continue


        # 接点1でも接点2でも許容値の制約を満たすとき
        if length1 < tolerance and length2 < tolerance:
            # print("-------------------------------------------------------")
            # print("Final tan1 <count: %s | curve length1: %s>" % (i, length1))
            # print("Final tan2 <count: %s | curve_length2: %s>" % (i, length2))

            # run time console
            end_time = time.time()
            optimization_bridge_run_time = end_time - start_time
            # print("optimization_bridge Run time: %s" % optimization_bridge_run_time)

            return curve1, curve2


        # 接点1で許容値の制約を満たすとき(接点2では満たさない)
        elif length1 < tolerance:

            # angleを更新
            if length2 < 50:
                if angle2 > 0:
                    angle2 = 0.01
                else:
                    angle2 = -0.01

            elif length2 < 60:
                if angle2 > 0:
                    angle2 = 0.04
                else:
                    angle2 = -0.04

            elif length2 < 90:
                if angle2 > 0:
                    angle2 = 0.07
                else:
                    angle2 = -0.07

            elif length2 < 120:
                if angle2 > 0:
                    angle2 = 0.15
                else:
                    angle2 = -0.15

            elif length2 < 150:
                if angle2 > 0:
                    angle2 = 0.35
                else:
                    angle2 = -0.35

            else:
                if angle2 > 0:
                    angle2 = 4.3
                else:
                    angle2 = -4.3

            rs.RotateObject(unused_surface, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_line, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_polyline, rotate_point1, angle2, rotate_axis1)
            rs.RotateObject(unused_mark_line[0], rotate_point1, angle2,rotate_axis1)
            rs.RotateObject(unused_mark_line[1], rotate_point1, angle2,rotate_axis1)

            # print("length1[%s]: %s | angle2: %s" % (i, length1, angle2))
            # print("length2[%s]: %s | angle2: %s" % (i, length2, angle2))

            # 接点2の接触部の長さを格納する
            curve_length2.append(length2)

            # もし衝突交線の値が大きくなる場合、回転の方向を逆転する
            if len(curve_length2) == 3:
                if curve_length2[0] < curve_length2[1] < curve_length2[2]:

                    angle2 = angle2 * -1.0
                    # print("update angle2")
                    # print("angle2: %s" % angle2)
                    angle = 3.0 * angle2
                    rs.RotateObject(unused_surface, rotate_point1, angle, rotate_axis1)
                    rs.RotateObject(unused_line, rotate_point1, angle, rotate_axis1)
                    rs.RotateObject(unused_polyline, rotate_point1, angle, rotate_axis1)
                    rs.RotateObject(unused_mark_line[0], rotate_point1, angle, rotate_axis1)
                    rs.RotateObject(unused_mark_line[1], rotate_point1, angle, rotate_axis1)

                curve_length2 = []


            if curve1:
                for k in range(0, len(curve1)):
                    rs.DeleteObject(curve1[k])
            if curve2:
                for k in range(0, len(curve2)):
                    rs.DeleteObject(curve2[k])

            if i == 199:
                # print("-------------------------------------------------------")
                # print("Can not Optimization bridge")

                # run time console
                end_time = time.time()
                optimization_bridge_run_time = end_time - start_time
                # print("optimization_bridge Run time: %s" % optimization_bridge_run_time)

                return False


        # 接点2で許容値の制約を満たすとき(接点1では満たさない)
        elif length2 < tolerance:

            # angleを更新
            if length1 < 45:
                if angle1 > 0:
                    angle1 = 0.01
                else:
                    angle1 = -0.01

            elif length1 < 60:
                if angle1 > 0:
                    angle1 = 0.04
                else:
                    angle1 = -0.04

            elif length1 < 90:
                if angle1 > 0:
                    angle1 = 0.07
                else:
                    angle1 = -0.07

            elif length1 < 120:
                if angle1 > 0:
                    angle1 = 0.15
                else:
                    angle1 = -0.15

            elif length1 < 150:
                if angle1 > 0:
                    angle1 = 0.35
                else:
                    angle1 = -0.35

            else:
                if angle1 > 0:
                    angle1 = 4.3
                else:
                    angle1 = -4.3

            rs.RotateObject(unused_surface, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_line, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_polyline, rotate_point2, angle1, rotate_axis2)
            rs.RotateObject(unused_mark_line[0], rotate_point2, angle1,rotate_axis2)
            rs.RotateObject(unused_mark_line[1], rotate_point2, angle1,rotate_axis2)

            # console
            # print("length1[%s]: %s | angle1: %s" % (i, length1, angle1))
            # print("length2[%s]: %s | angle1: %s" % (i, length2, angle1))

            # checkしているよ TODO
            # if length2 < 10:
            #     rs.MoveObject(unused_surface, vec_reverse)
            #     rs.MoveObject(unused_line, vec_reverse)
            #     rs.MoveObject(unused_poly, vec_reverse)

            # 接点1の接触部の長さを格納する
            curve_length1.append(length1)

            # もし衝突交線の値が大きくなる場合、回転の方向を逆転する
            if len(curve_length1) == 3:
                if curve_length1[0] < curve_length1[1] < curve_length1[2]:

                    angle1 = angle1 * -1.0
                    # print("update angle1")
                    # print("angle1: %s" % angle1)

                    angle = 3.0 * angle1
                    rs.RotateObject(unused_surface, rotate_point2, angle, rotate_axis2)
                    rs.RotateObject(unused_line, rotate_point2, angle, rotate_axis2)
                    rs.RotateObject(unused_polyline, rotate_point2, angle, rotate_axis2)
                    rs.RotateObject(unused_mark_line[0], rotate_point2, angle, rotate_axis2)
                    rs.RotateObject(unused_mark_line[1], rotate_point2, angle, rotate_axis2)

                curve_length1 = []

            if curve1:
                for k in range(0, len(curve1)):
                    rs.DeleteObject(curve1[k])
            if curve2:
                for k in range(0, len(curve2)):
                    rs.DeleteObject(curve2[k])

            if i == 199:
                # print("-------------------------------------------------------")
                # print("Can not Optimization bridge")

                # run time console
                end_time = time.time()
                optimization_bridge_run_time = end_time - start_time
                # print("optimization_bridge Run time: %s" % optimization_bridge_run_time)

                return False

        else:
            rs.MoveObject(unused_surface, vec_reverse1)
            rs.MoveObject(unused_line, vec_reverse1)
            rs.MoveObject(unused_polyline, vec_reverse1)
            rs.MoveObject(unused_mark_line[0], vec_reverse1)
            rs.MoveObject(unused_mark_line[1], vec_reverse1)

            if curve1:
                for k in range(0, len(curve1)):
                    rs.DeleteObject(curve1[k])
            if curve2:
                for k in range(0, len(curve2)):
                    rs.DeleteObject(curve2[k])

            if i == 199:
                # print("-------------------------------------------------------")
                # print("Can not Optimization bridge")

                # run time console
                end_time = time.time()
                optimization_bridge_run_time = end_time - start_time
                # print("optimization_bridge Run time: %s" % optimization_bridge_run_time)

                return False



def AddVector(base, vec):
    tip = rs.PointAdd(base, vec)
    line = rs.AddLine(base, tip)
    rs.CurveArrows(line, 2)

    return line



def createMidPointFromCurve(curve):
    split_num = 2
    point_list = []
    domain = rs.CurveDomain(curve)
    t = (domain[1] - domain[0]) / split_num

    for int in range(split_num):
        dt = t * int
        point = rs.EvaluateCurve(curve, dt)
        point_list.append(point)

    # 直線の中心点を求める
    line = rs.AddLine(point_list[0], point_list[1])
    mid_point = rs.CurveMidPoint(line)

    return mid_point





if __name__ == "__main__":
    print("###Test Run###")

    rotate_p = rs.GetObject("select a rotate point", rs.filter.point)
    rotate_vec = rs.GetObject("select a rotate vec", rs.filter.curve)
    unused_srf = rs.GetObject("select a unused surface", rs.filter.surface)
    used_srf1 = rs.GetObject("select a used surface", rs.filter.surface)
    unused_line = rs.GetObject("select a unused line", rs.filter.curve)
    tolerance = 40





