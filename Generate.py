# -*- coding:utf-8 -*-

from Timber import Timber
import random as rnd
import math  # ttm add 181003
from forGenerate import timberMethod as timber
import Rhino
from forGenerate import RhinoCommonOriginalMethods as oriRhino
import copy


class Generate:

    # 初期化
    def __init__(self, center_line, surface, id, sum_timber, population_id, generate_range):
        self.center_line_list = center_line  # center line list
        self.surface_list = surface  # surface list
        self.id_list = id  # timber name list
        self.sum_timber = sum_timber  # timberの総本数
        self.timber_list = []  # まだ使用していないtimberのリスト
        self.used_list = []  # 使用したtimberのリスト
        self.population_id = population_id

        self.evaluation = 0
        self.yet_regenerate_tim_id = []  # 再生成されずにいる部材のidを格納
        self.already_regenerate_tim_id = []  # 再生成すでにされている部材のidを格納する。

        self.generate_range = generate_range

    def instantiate_timber(self):

        # スキャンデータをtimberクラスのオブジェクトにする
        for i in range(0, self.sum_timber):
            timber = Timber(self.center_line_list[i], self.surface_list[i], self.id_list[i])  # インスタンス生成
            self.timber_list.append(timber)  # timber_listに追加

            # 中心線の長さを取得する
            timber.measure_length()
            timber.measure_section_length()
            timber.init_tim_distance(self.sum_timber)

    def generate_ground_init(self, generate_range, objects_curve=None, objects_point=None):
        """
        :param generate_range: 生成可能範囲の入力ー＞int
        :param objects_curve Rhinocerosの閉じたCurveで範囲を指定。Rhino.Objectに変換したものを引数へ
        :param generate_point: RhinocerosのPointで指定するRhino.Objectに変換したものを引数へ
        :return:
        """

        # 部材の選択。
        if len(self.used_list) == 0:
            tim = self.timber_list[0]
        else:
            index = rnd.randint(0, len(self.timber_list) - 1)
            tim = self.timber_list[index]

        tim_srf = tim.surface
        tim_axis = tim.center_line

        axis_start_p = tim_axis.PointAtStart
        axis_end_p = tim_axis.PointAtEnd

        # if generate range is predetermined
        # objects_curve = []
        # if len(self.used_list) == 0 and generate_range_curve:
        #     for i in range(len(generate_range_curve)):
        #         curve = rs.coercecurve(generate_range_curve[i])
        #         objects_curve.append(curve)

        # if generate base point is predetermined
        # objects_point = []
        # if len(self.used_list) == 0 and generate_point:
        #     for i in range(len(generate_point)):
        #         point = rs.coerce3dpoint(generate_point[i])
        #         objects_point.append(point)

        # 生成される範囲が予めCurveで決められている場合
        if objects_curve:
            flag = True
            loop = 0
            while flag:
                loop += 1
                x = rnd.randint(0, generate_range)
                y = rnd.randint(0, generate_range)

                point_base = Rhino.Geometry.Point3d(x, y, 0)

                for i in range(len(objects_curve)):
                    rc = objects_curve[i].Contains(point_base)
                    if rc == Rhino.Geometry.PointContainment.Inside:
                        flag = False
                        break

                if loop > 100:
                    raise Exception("while infinite loop")

        # 生成される範囲がPointで決められている場合。
        elif objects_point:
            select_index = rnd.randint(0, len(objects_point)-1)

            point_base = objects_point[select_index]
            del objects_point[select_index]  # TODO 他の場所と干渉する恐れがあるので要注意

        # 生成される場所が特に決定されていない場合。
        else:
            x = rnd.randint(0, generate_range)
            y = rnd.randint(0, generate_range)
            point_base = Rhino.Geometry.Point3d(x, y, 0)

        # selectされたpointとaxisの端点とのベクトルを計算
        if axis_end_p[2] > axis_start_p[2]:
            point_base_tim = axis_start_p
        else:
            point_base_tim = axis_end_p

        vector_from_tim = point_base - point_base_tim

        # timをbaseまでMoveさせる
        xf = Rhino.Geometry.Transform.Translation(vector_from_tim)
        tim_axis.Transform(xf)
        tim_srf.Transform(xf)

        # 指定した生成可能範囲内に収まるように試行する。
        # 接点からのフリをランダムにする。 TODO 一旦部材がほとんど垂直に置かれていることを前提にアルゴリズムを構築
        restriction_angle = 45

        # rotateを行うための平面を定義。
        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 0, 10)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)
        plane1 = Rhino.Geometry.Plane(p1, p2, p3)

        p1_ = Rhino.Geometry.Point3d(0, 0, 0)
        p2_ = Rhino.Geometry.Point3d(0, 10, 0)
        p3_ = Rhino.Geometry.Point3d(10, 0, 0)
        plane2 = Rhino.Geometry.Plane(p1_, p2_, p3_)

        # 指定した生成可能範囲に部材が収まるまで試行を繰り返す。
        # Curveの端部が外に出ている場合のみなので、精度をまだ上げることが可能。
        # 他部材との接触判定を含める必要あり。
        init_generate = True
        avoid_infinite_loop = 1
        while init_generate:
            avoid_infinite_loop += 1
            if avoid_infinite_loop > 100:
                raise Exception('infinite loop occur')

            rotate_angle = math.radians(rnd.randint(-restriction_angle, restriction_angle))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], point_base)
            tim_srf.Transform(xf)
            tim_axis.Transform(xf)

            rotate_angle = math.radians(rnd.randint(-restriction_angle, -restriction_angle))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], point_base)
            tim_srf.Transform(xf)
            tim_axis.Transform(xf)

            start_p = tim_axis.PointAtStart
            end_p = tim_axis.PointAtEnd
            for i in start_p:
                if i < self.generate_range:
                    init_generate = False
                    pass
                else:
                    init_generate = True
                    break

            for i in end_p:
                if i < self.generate_range:
                    init_generate = False
                    pass
                else:
                    init_generate = True
                    break

        # 各パラメータの更新
        # 木材同士の間隔の最小値を計測。
        if len(self.used_list) == 0:
            pass
        else:
            for i in range(len(self.used_list)):
                timber.distanceBetweenTimber_RhinoCommon(self.used_list[i], tim)

        # 木材未使用、使用リストの更新
        if len(self.used_list) == 0:
            self.used_list.append(tim)
            self.timber_list.pop(0)
        else:
            self.used_list.append(tim)
            self.timber_list.pop(index)

        return True

    def cantilever(self, limit_degree):
        divide_domain_num = 10

        for h in range(50):
            if h == 49:
                raise Exception('GL avoid is not work well')

            # 各オブジェクトの取得　--->  Timber Instanceに置き換える
            if len(self.used_list) == 0:
                used_timber = self.timber_list[0]
                unused_timber = self.timber_list[1]

            else:
                x = rnd.randint(0, len(self.used_list) - 1)
                used_timber = self.used_list[x]

                y = rnd.randint(0, len(self.timber_list) - 1)
                unused_timber = self.timber_list[y]

            tim1_srf = used_timber.surface
            tim2_srf = unused_timber.surface

            tim1_center_crv = used_timber.center_line
            tim2_center_crv = unused_timber.center_line

            domain_crv1 = tim1_center_crv.Domain
            domain_crv2 = tim2_center_crv.Domain

            each_domain_length1 = (domain_crv1[1] - domain_crv1[0]) / divide_domain_num
            each_domain_length2 = (domain_crv2[1] - domain_crv2[0]) / divide_domain_num

            # select_domainの値を変化させることで接合部を変化させる事ができる。
            select_domain1 = used_timber.select_surface_domain()
            select_domain2 = unused_timber.select_surface_domain()

            tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + select_domain1 * each_domain_length1)
            tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + select_domain2 * each_domain_length2)

            vec_move = tim1_point - tim2_point

            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            # Rotateするために回転平面を規定。Plane1
            p1 = Rhino.Geometry.Point3d(0, 0, 0)
            p2 = Rhino.Geometry.Point3d(0, 0, 10)
            p3 = Rhino.Geometry.Point3d(10, 0, 0)
            plane1 = Rhino.Geometry.Plane(p1, p2, p3)

            # Rotateするために回転平面を規定。Plane2
            p1_ = Rhino.Geometry.Point3d(0, 0, 0)
            p2_ = Rhino.Geometry.Point3d(0, 10, 0)
            p3_ = Rhino.Geometry.Point3d(10, 0, 0)
            plane2 = Rhino.Geometry.Plane(p1_, p2_, p3_)

            # GLに部材を生成しないために部材端のz座標値を計算
            # 生成可能範囲に部材が収まるように制限。
            flag_gl = True
            avoid_infinite_loop = 0
            while flag_gl:

                avoid_infinite_loop += 1
                if avoid_infinite_loop > 50:
                    # print('infinite loop is occur')
                    break

                # Rotate1回目
                rotate_angle = math.radians(rnd.randint(0, 360))
                xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], tim1_point)
                tim2_center_crv.Transform(xf)
                tim2_srf.Transform(xf)

                # Rotate2回目
                rotate_angle = math.radians(rnd.randint(0, 360))
                xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], tim1_point)
                tim2_center_crv.Transform(xf)
                tim2_srf.Transform(xf)

                tim2_crv_end = tim2_center_crv.PointAtEnd
                tim2_crv_start = tim2_center_crv.PointAtStart

                # GL との接触を判定
                if 4000 > tim2_crv_end[2] > 100 and 4000 > tim2_crv_start[2] > 100:
                    gl_check = True
                else:
                    gl_check = False

                # 生成可能範囲に収まっているか判定。
                counter = 0
                if (self.generate_range * 2) * self.population_id < tim2_crv_start[0] < (self.generate_range * 2) * (self.population_id) + self.generate_range\
                        and (self.generate_range * 2) * self.population_id < tim2_crv_end[0] < (self.generate_range * 2) * (self.population_id) + self.generate_range:
                    counter += 1
                if -(self.generate_range) > tim2_crv_start[1] > -(self.generate_range * 2) and  \
                        -(self.generate_range) > tim2_crv_end[1] > -(self.generate_range * 2):
                    counter += 1

                if counter == 2:
                    range_check = True
                else:
                    range_check = False

                # 両条件を満たしていればOK
                if range_check and gl_check:
                    pass
                else:
                    continue

                contact_judge_flag = False
                # contact_judge_flag = self.contact_judgement_cantilever(unused_timber.id, used_timber.id)
                if contact_judge_flag:
                    flag_gl = True
                else:
                    flag_gl = False
                    # print('cantilever contact judgement clear : while{} loop{}'.format(avoid_infinite_loop, h))

            if flag_gl:
                continue
            else:
                pass

            # 接合部の接合範囲最適化。
            # ここも現状は精度がイマイチなため、修正が必要。
            length1, rc1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim1_srf, tim1_point)
            length2, rc2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim2_srf, tim2_point)

            vec_move = rc1 - tim2_point
            if length1 > length2:
                rc = Rhino.Geometry.Vector3d(vec_move.X, vec_move.Y, vec_move.Z)
                rc.Unitize()
                vec_move = rc * ((length1 / 2) + (length2 / 3))
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim2_srf.Transform(xf)
                tim2_center_crv.Transform(xf)
            else:
                rc = Rhino.Geometry.Vector3d(vec_move.X, vec_move.Y, vec_move.Z)
                rc.Unitize()
                vec_move = rc * ((length1 / 2) + (length2 / 3))
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim2_srf.Transform(xf)
                tim2_center_crv.Transform(xf)

            tim2_crv_end = tim2_center_crv.PointAtEnd
            tim2_crv_start = tim2_center_crv.PointAtStart

            # GLとの接触判定。
            if tim2_crv_end[2] > 100 and tim2_crv_start[2] > 100:
                break
            else:
                continue

        # domainの更新
        used_timber.select_domain_list.append([select_domain1, unused_timber.id])
        unused_timber.select_domain_list.append([select_domain2, used_timber.id])

        # 接合した相手の木材のIDを格納。
        used_timber.partner_tim.append(unused_timber.id)
        unused_timber.partner_tim.append(used_timber.id)
        if used_timber.id == unused_timber.id:
            raise Exception('partner tim renewal fail')

        # 木材同士の間隔の最小値を計測。
        if len(self.used_list) == 0:
            timber.distanceBetweenTimber_RhinoCommon(used_timber, unused_timber)
        else:
            for i in range(len(self.used_list)):
                timber.distanceBetweenTimber_RhinoCommon(self.used_list[i], unused_timber)

        # 木材未使用、使用リストの更新
        if len(self.used_list) == 0:
            self.used_list.append(used_timber)
            self.used_list.append(unused_timber)
            self.timber_list.pop(0)
            self.timber_list.pop(0)
        else:
            self.used_list.append(unused_timber)
            self.timber_list.pop(y)

        return True

    def cantilever_specify(self, tim_preexist_num, tim_add_num, already_regenerated_list, limit_degree,
                           generation_num, loop_num, loop, between_draw_rhino):

        gl_distance = 0
        divide_domain_num = 10

        # 各オブジェクトの取得　--->  Timber Instanceに置き換える
        used_timber = self.used_list[tim_preexist_num]
        unused_timber = self.used_list[tim_add_num]

        tim1_srf = self.used_list[tim_preexist_num].surface
        tim2_srf = self.used_list[tim_add_num].surface

        tim1_center_crv = self.used_list[tim_preexist_num].center_line
        tim2_center_crv = self.used_list[tim_add_num].center_line

        domain_crv1 = tim1_center_crv.Domain
        domain_crv2 = tim2_center_crv.Domain

        each_domain_length1 = (domain_crv1[1] - domain_crv1[0]) / divide_domain_num
        each_domain_length2 = (domain_crv2[1] - domain_crv2[0]) / divide_domain_num

        select_domain1 = used_timber.select_surface_domain()
        select_domain2 = unused_timber.select_surface_domain()

        tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + select_domain1 * each_domain_length1)
        tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + select_domain2 * each_domain_length2)

        vec_move = tim1_point - tim2_point

        xf = Rhino.Geometry.Transform.Translation(vec_move)
        tim2_center_crv.Transform(xf)
        tim2_srf.Transform(xf)

        # Rotateを行うための平面を定義。Plane1
        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 0, 10)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)
        plane1 = Rhino.Geometry.Plane(p1, p2, p3)

        # Rotateを行うための平面を定義。Plane2
        p1_ = Rhino.Geometry.Point3d(0, 0, 0)
        p2_ = Rhino.Geometry.Point3d(0, 10, 0)
        p3_ = Rhino.Geometry.Point3d(10, 0, 0)
        plane2 = Rhino.Geometry.Plane(p1_, p2_, p3_)

        # GL Method
        flag = True
        avoid_infinite_loop = 0
        while flag:
            avoid_infinite_loop += 1
            if avoid_infinite_loop > 100:
                break

            # Rotate1回目
            rotate_angle = math.radians(rnd.randint(0, 360))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], tim1_point)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            # Rotate2回目
            rotate_angle = math.radians(rnd.randint(0, 360))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], tim1_point)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            end_p = tim2_center_crv.PointAtEnd
            start_p = tim2_center_crv.PointAtStart

            # GL との接触を判定 + 高さ制限
            if 4000 > end_p[2] > 100 and 4000> start_p[2] > 100:
                gl_check = True
            else:
                gl_check = False

            # 生成可能範囲に収まっているか判定。
            counter = 0
            if (self.generate_range * 2) * loop < start_p[0] < (self.generate_range * 2) * (
                    loop) + self.generate_range \
                    and (self.generate_range * 2) * loop < end_p[0] < (self.generate_range * 2) * (
                    loop) + self.generate_range:
                counter += 1

            if -(self.generate_range * 2) * (loop_num + 1) + self.generate_range > start_p[1] > -(self.generate_range * 2) * (loop_num + 1) - (self.generate_range * 2) \
                    and -(self.generate_range * 2) * (loop_num + 1) + self.generate_range > end_p[1] > -(self.generate_range * 2) * (loop_num + 1) - (self.generate_range * 2):
                counter += 1

            if counter == 2:
                range_check = True
            else:
                range_check = False

            # 両条件を満たしていればOK
            if range_check and gl_check:
                pass
            else:
                continue
            # contact_judge_flag = False
            contact_judge_flag = self.contact_judgement_cantilever_specify(unused_timber.id, used_timber.id, already_regenerated_list)
            if contact_judge_flag:
                flag = True
            else:
                # print('cantilever_specify contact judgement clear : while{}'.format(avoid_infinite_loop))
                flag = False

        if flag:
            return False
        else:
            pass

        # 接合部最適化開始。
        length1, rc1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim1_srf, tim1_point)
        length2, rc2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim2_srf, tim2_point)

        vec_move = rc1 - tim2_point
        if length1 > length2:
            rc = Rhino.Geometry.Vector3d(vec_move.X, vec_move.Y, vec_move.Z)
            rc.Unitize()
            vec_move = rc * ((length1 / 2) + (length2 / 3))
            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim2_srf.Transform(xf)
            tim2_center_crv.Transform(xf)
        else:
            rc = Rhino.Geometry.Vector3d(vec_move.X, vec_move.Y, vec_move.Z)
            rc.Unitize()
            vec_move = rc * ((length1 / 2) + (length2 / 3))
            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim2_srf.Transform(xf)
            tim2_center_crv.Transform(xf)

        # GL Method
        end_p = tim2_center_crv.PointAtEnd
        start_p = tim2_center_crv.PointAtStart

        if end_p[2] > gl_distance and start_p[2] > gl_distance:
            pass
        else:
            return False

        # 変数の更新
        # domainの更新
        used_timber.select_domain_list.append([select_domain1, unused_timber.id])
        unused_timber.select_domain_list.append([select_domain2, used_timber.id])

        # partnerの更新
        used_timber.partner_tim.append(unused_timber.id)
        unused_timber.partner_tim.append(used_timber.id)
        if used_timber.id == unused_timber.id:
            raise Exception('partner_tim renewal fail')

        # 木材同士の間隔の最小値を計測。
        for i in range(len(self.used_list)):
            already_exist_timber = self.used_list[i]
            already_exist_timber_name = self.used_list[i].id
            if already_exist_timber_name in already_regenerated_list:
                timber.distanceBetweenTimber_RhinoCommon(already_exist_timber, unused_timber)

        return True

    def bridge(self, limit_degree):

        split_ = 200
        split_domain_range_num = 10

        for h in range(100):

            if h > 99:
                raise Exception('bridge GL method is not work well')

            # 部材の選択を行い、部材間の距離を測定することにより、Bridge可能かどうか判定する。
            for i in range(20):
                flag_select_timber_domain = True
                flag_select_timber_domain_success = False

                flag_select_timber = False
                samples = [sample for sample in range(len(self.used_list))]

                # 部材の選択を行う
                for _ in range(1000):
                    # used_timberの選択
                    index = rnd.sample(samples, 2)
                    x1 = index[0]
                    x2 = index[1]
                    used_timber1 = self.used_list[x1]
                    used_timber2 = self.used_list[x2]

                    # unused_timberの選択
                    y = rnd.randint(0, len(self.timber_list) - 1)
                    unused_timber = self.timber_list[y]

                    length_of_between = used_timber1.tim_distance[used_timber2.id][0]
                    length_of_timber = unused_timber.timber_length

                    if length_of_timber < length_of_between:
                        continue
                    else:
                        flag_select_timber = True
                        break

                if not flag_select_timber:
                    raise Exception('select timber does not work')

                tim3_srf = unused_timber.surface
                tim1_center_crv = used_timber1.center_line
                tim2_center_crv = used_timber2.center_line
                tim3_center_crv = unused_timber.center_line

                # Get each crv domain
                domain_crv1 = tim1_center_crv.Domain
                domain_crv2 = tim2_center_crv.Domain
                domain_crv3 = tim3_center_crv.Domain
                split_range = (domain_crv3[1] - domain_crv3[0]) / split_

                # 指定したdomain内にある点を算出する。
                domain_range1 = abs((domain_crv1[1] - domain_crv1[0]) / split_domain_range_num)
                domain_range2 = abs((domain_crv2[1] - domain_crv2[0]) / split_domain_range_num)
                domain_range3 = abs((domain_crv3[1] - domain_crv3[0]) / split_domain_range_num)

                select_domain_3_start = 0  # TODO 今のところ固定値
                for select_domain_loop in range(200):
                    select_domain_1 = used_timber1.select_surface_domain()  # select_domain はドメインの値をintで返される。
                    select_domain_2 = used_timber2.select_surface_domain()

                    # TODO　ドメインの指定に関しては範囲内をランダムにする、中心線を単純にするなどによって精度を向上させること可能。
                    tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + domain_range1 * select_domain_1)
                    tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + domain_range2 * select_domain_2)

                    # tim1, tim2間の点と点の長さを取得する
                    distance_between = (tim1_point - tim2_point).Length

                    # bridge可能か判断　
                    length_tim3 = tim3_center_crv.GetLength() / split_domain_range_num * 2
                    if distance_between > length_tim3 - (length_tim3 / 10) * 4:
                        if select_domain_loop == 199:
                            flag_select_timber_domain = False
                            break

                        else:
                            continue
                    else:
                        flag_select_timber_domain_success = True
                        break

                # 部材の再選択へもどる。
                if not flag_select_timber_domain:
                    continue

                # 部材がBridge可能と判断されたなら。部材の選択を終了。
                if flag_select_timber_domain_success:
                    break
                else:
                    raise Exception("select timber domain is fail in Generate line 1422")

            # distance_betweenの距離よりもlength_tim3のほうが長かったとしても、EvaluateCurveで選択される点次第で長さが足りなくなることも十分に考えられるだろう。
            # このｔの値が変化することによってかけられるDomainの範囲が自由になる。
            t = domain_crv3[0] + domain_range3 * select_domain_3_start
            tim3_start_point_coordinate = tim3_center_crv.PointAt(t)

            # distance_between と同じ長さとなるcrv3上のパラメータを取得。　点を加える。
            t_ = domain_crv3[0]
            flag_select = True
            avoid_ = 0
            while flag_select:
                avoid_ = avoid_ + 1
                t_ = t_ + split_range * 5  # ここを調整することでスピードを上げることができるはず。
                tim3_end_point_coordinate = tim3_center_crv.PointAt(t_)  # RhinoCommon
                distance = (tim3_end_point_coordinate - tim3_start_point_coordinate).Length  # RhinoCommon
                if distance > distance_between:
                    break
                if avoid_ > 100:
                    raise ValueError("infinite loop: select_domain_3_end")

            # ObjectのMove
            vec_move = tim1_point - tim3_start_point_coordinate  # RhinoCommon
            # print("vec_move", vec_move)
            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim3_center_crv.Transform(xf)
            tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)

            # 1回目のRotate
            vec1 = tim1_point - tim3_end_point
            vec2 = tim1_point - tim2_point
            rotate_angle1 = oriRhino.VectorAngle_RhinoCommon(vec1, vec2)
            plane1 = Rhino.Geometry.Plane(tim1_point, tim3_end_point, tim2_point)
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle1, plane1[3], tim1_point)
            tim3_center_crv.Transform(xf)
            tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)
            # tim3_start_point = tim3_center_crv.PointAt(t)

            # 2回目のRotate
            vec3 = tim3_end_point - tim1_point
            vec4 = tim2_point - tim1_point
            rotate_angle2 = oriRhino.VectorAngle_RhinoCommon(vec3, vec4)
            plane2 = Rhino.Geometry.Plane(tim1_point, tim3_end_point, tim2_point)

            if int(tim3_end_point[0]) - 10 <= int(tim2_point[0]) <= int(tim3_end_point[0]) + 10 or \
                    int(tim3_end_point[1]) - 10 <= int(tim2_point[1]) <= int(tim3_end_point[1] + 10 or \
                                                                             int(tim3_end_point[2]) - 10 <= int(
                tim2_point[2]) <= int(tim3_end_point[2])) + 10:  # TODO 範囲の式に書き換える。
                pass
            else:

                xf = Rhino.Geometry.Transform.Rotation(rotate_angle2, plane2[3], tim1_point)
                tim3_center_crv.Transform(xf)
                tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)
            tim3_start_point = tim3_center_crv.PointAt(t)

            # 接合部の接触面積最適化
            # tim1とtim2のtim3にたいする外積をそれぞれ求める。
            vec_tim3 = tim3_end_point - tim3_start_point
            tim1_end_point = tim1_center_crv.PointAtEnd
            vec_tim1 = tim1_end_point - tim1_point
            tim2_end_point = tim2_center_crv.PointAtEnd

            vec_tim2 = tim2_end_point - tim2_point

            cross_vec1 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim1)
            cross_vec2 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim2)
            add_vec = cross_vec1 + cross_vec2

            # 接合部の直径を求めることにより、移動距離を決定する。
            dis1, rp1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim3_srf, tim3_start_point)
            dis2, rp2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim3_srf, tim3_end_point)

            # 移動距離を決定。
            if dis1 >= dis2:
                rc = Rhino.Geometry.Vector3d(add_vec.X, add_vec.Y, add_vec.Z)
                rc.Unitize()
                vec_move = rc * dis2
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim3_srf.Transform(xf)
                tim3_center_crv.Transform(xf)

            else:
                rc = Rhino.Geometry.Vector3d(add_vec.X, add_vec.Y, add_vec.Z)
                rc.Unitize()
                vec_move = rc * dis1
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim3_srf.Transform(xf)
                tim3_center_crv.Transform(xf)

            tim3_end_p = tim3_center_crv.PointAtEnd
            tim3_start_p = tim3_center_crv.PointAtStart

            # ----------------------------------------------------------------------------------------------------------
            # GLに接ししているか判定。
            if 4000 > tim3_end_p[2] > 100 and 4000 > tim3_start_p[2] > 100:
                gl_check = True
            else:
                gl_check = False

            # 生成可能範囲に収まっているか判定。
            counter = 0
            if (self.generate_range * 2) * self.population_id < tim3_start_p[0] < (self.generate_range * 2) * (
                    self.population_id) + self.generate_range\
                    and (self.generate_range * 2) * self.population_id < tim3_end_p[0] < (self.generate_range * 2) * (
                    self.population_id) + self.generate_range:
                counter += 1

            if -(self.generate_range) > tim3_start_p[1] > -(self.generate_range * 2) \
                    and -(self.generate_range) > tim3_end_p[1] > -(self.generate_range * 2):
                counter += 1

            if counter == 2:
                range_check = True
            else:
                range_check = False

            # 両条件を満たしていればOK
            if range_check and gl_check:
                pass
            else:
                continue

            contact_judge_flag = False
            # contact_judge_flag = self.contact_judgement_bridge(unused_timber.id, used_timber1.id, used_timber2.id)
            if contact_judge_flag:
                continue
            else:
                # print('bridge contact judgement is success: {}'.format(h))
                break

        # # layerを変更して正しいレイヤーへ
        # a = 'tim'
        # b = str(unused_timber.name)
        # print("unused_timber.name", unused_timber.name)
        # rs.CurrentLayer(a + b)
        #
        # cr = scriptcontext.doc.Objects.AddCurve(tim3_center_crv)
        # sf = scriptcontext.doc.Objects.AddBrep(tim3_srf)
        #

        # 使用domainの更新のための値
        select_domain_3_end = abs(int(t_ // domain_range3))
        # print("select_domain_3_end : %s" % (select_domain_3_end))
        used_timber1.select_domain_list.append([select_domain_1, unused_timber.id])
        used_timber2.select_domain_list.append([select_domain_2, unused_timber.id])
        unused_timber.select_domain_list.append([select_domain_3_start, used_timber1.id])
        unused_timber.select_domain_list.append([select_domain_3_end, used_timber2.id])

        # partner_tim 更新
        used_timber1.partner_tim.append(unused_timber.id)
        used_timber2.partner_tim.append(unused_timber.id)

        unused_timber.partner_tim.append(used_timber1.id)
        unused_timber.partner_tim.append(used_timber2.id)

        if used_timber1.id == unused_timber.id:
            raise Exception('partner_tim renewal fail')
        if used_timber2.id == unused_timber.id:
            raise Exception('partner_tim renewal fail')

        for i in range(len(self.used_list)):
            timber.distanceBetweenTimber_RhinoCommon(unused_timber, self.used_list[i])

        self.used_list.append(unused_timber)
        self.timber_list.pop(y)

        return True

    def bridge_specify(self, tim_preexist_num_1, tim_preexist_num_2, tim_add_num, already_regenerated_list,
                       limit_degree, generation_num, loop_num, loop, between_draw_rhino):
        # start_time = time.time()

        gl_distance = 0

        split_ = 200
        split_domain_range_num = 10

        # 各オブジェクトの取得　--->  Timber Instanceに置き換える
        used_timber1 = self.used_list[tim_preexist_num_1]
        used_timber2 = self.used_list[tim_preexist_num_2]
        unused_timber = self.used_list[tim_add_num]

        tim3_srf = self.used_list[tim_add_num].surface
        tim1_center_crv = self.used_list[tim_preexist_num_1].center_line
        tim2_center_crv = self.used_list[tim_preexist_num_2].center_line
        tim3_center_crv = self.used_list[tim_add_num].center_line

        # bridge可能か判断　その１
        distance = used_timber1.tim_distance[used_timber2.id][0]
        if distance + 100 > unused_timber.timber_length:
            return False

        # Get each crv domain
        domain_crv1 = tim1_center_crv.Domain
        domain_crv2 = tim2_center_crv.Domain
        domain_crv3 = tim3_center_crv.Domain
        split_range = (domain_crv3[1] - domain_crv3[0]) / split_

        # 指定したdomain内にある点を算出する。
        domain_range1 = abs((domain_crv1[1] - domain_crv1[0]) / split_domain_range_num)
        domain_range2 = abs((domain_crv2[1] - domain_crv2[0]) / split_domain_range_num)
        domain_range3 = abs((domain_crv3[1] - domain_crv3[0]) / split_domain_range_num)

        for i in range(10):
            select_domain_3_start = 0  # TODO 今のところ固定値
            for select_domain_loop in range(200):
                select_domain_1 = used_timber1.select_surface_domain()  # select_domain はドメインの値をintで返される。
                select_domain_2 = used_timber2.select_surface_domain()

                # TODO　ドメインの指定に関しては範囲内をランダムにする、中心線を単純にするなどによって精度を向上させること可能。
                tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + domain_range1 * select_domain_1)
                tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + domain_range2 * select_domain_2)

                # tim1, tim2間の点と点の長さを取得する
                distance_between = (tim1_point - tim2_point).Length

                # bridge可能か判断　その２
                length_tim3 = tim3_center_crv.GetLength() - tim3_center_crv.GetLength() / split_domain_range_num * 2
                if distance_between > length_tim3 - (length_tim3/10)* 4:
                    if select_domain_loop == 199:
                        return False

                    else:
                        continue
                else:
                    break
            # distance_betweenの距離よりもlength_tim3のほうが長かったとしても、EvaluateCurveで選択される点次第で長さが足りなくなることも十分に考えられるだろう。
            # t = domain_crv3[0] + split_range*20
            t = domain_crv3[0] + domain_range3 * select_domain_3_start
            tim3_start_point_coordinate = tim3_center_crv.PointAt(t)

            # distance_between と同じ長さとなるcrv3上のパラメータを取得。　点を加える。
            t_ = domain_crv3[0]
            flag_select = True
            avoid_ = 0
            while flag_select:
                avoid_ = avoid_ + 1
                t_ = t_ + split_range * 5  # ここを調整することでスピードを上げることができるはず。
                tim3_end_point_coordinate = tim3_center_crv.PointAt(t_)
                distance = (tim3_end_point_coordinate - tim3_start_point_coordinate).Length
                if distance > distance_between:
                    break
                if avoid_ > 100:
                    input("infinite loop: select_domain_3_end")

            # ObjectのMove
            vec_move = tim1_point - tim3_start_point_coordinate
            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim3_center_crv.Transform(xf)
            tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)

            # 1回目のRotate
            vec1 = tim1_point - tim3_end_point
            vec2 = tim1_point - tim2_point
            rotate_angle1 = oriRhino.VectorAngle_RhinoCommon(vec1, vec2)
            plane1 = Rhino.Geometry.Plane(tim1_point, tim3_end_point, tim2_point)
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle1, plane1[3], tim1_point)
            tim3_center_crv.Transform(xf)
            tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)

            # 2回目のRotate
            vec3 = tim3_end_point - tim1_point
            vec4 = tim2_point - tim1_point
            rotate_angle2 = oriRhino.VectorAngle_RhinoCommon(vec3, vec4)
            plane2 = Rhino.Geometry.Plane(tim1_point, tim3_end_point, tim2_point)

            if int(tim3_end_point[0]) - 10 <= int(tim2_point[0]) <= int(tim3_end_point[0]) + 10 or \
                    int(tim3_end_point[1]) - 10 <= int(tim2_point[1]) <= int(tim3_end_point[1] + 10 or \
                                                                             int(tim3_end_point[2]) - 10 <= int(
                tim2_point[2]) <= int(tim3_end_point[2])) + 10:  # TODO 範囲の式に書き換える。
                pass
            else:
                xf = Rhino.Geometry.Transform.Rotation(rotate_angle2, plane2[3], tim1_point)
                tim3_center_crv.Transform(xf)
                tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)
            tim3_start_point = tim3_center_crv.PointAt(t)

            # tim1とtim2のtim3にたいする外積をそれぞれ求める。
            vec_tim3 = tim3_end_point - tim3_start_point
            tim1_end_point = tim1_center_crv.PointAtEnd
            vec_tim1 = tim1_end_point - tim1_point
            tim2_end_point = tim2_center_crv.PointAtEnd
            vec_tim2 = tim2_end_point - tim2_point

            cross_vec1 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim1)
            cross_vec2 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim2)

            # 2つの外積で作成したベクトルを合成し描画する。
            add_vec = cross_vec1 + cross_vec2

            # 接合部の直径を求めることにより、移動距離を決定する。
            dis1, rp1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim3_srf, tim3_start_point)
            dis2, rp2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim3_srf, tim3_end_point)

            # 移動距離を決定。
            if dis1 >= dis2:
                rc = Rhino.Geometry.Vector3d(add_vec.X, add_vec.Y, add_vec.Z)
                rc.Unitize()
                vec_move = rc * dis2
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim3_srf.Transform(xf)
                tim3_center_crv.Transform(xf)

            else:
                rc = Rhino.Geometry.Vector3d(add_vec.X, add_vec.Y, add_vec.Z)
                rc.Unitize()
                vec_move = rc * dis1
                xf = Rhino.Geometry.Transform.Translation(vec_move)
                tim3_srf.Transform(xf)
                tim3_center_crv.Transform(xf)

            # ----------------------------------------------------------------------------------------------------------
            end_p = tim3_center_crv.PointAtEnd
            start_p = tim3_center_crv.PointAtStart

            if end_p[2] > gl_distance and start_p[2] > gl_distance:
                flag_gl_distance = True
                gl_check = True
            else:
                gl_check = False

            # 生成可能範囲に収まっているか判定。
            counter = 0
            if (self.generate_range * 2) * loop < start_p[0] < (self.generate_range * 2) * (
                    loop) + self.generate_range \
                    and (self.generate_range * 2) * loop < end_p[0] < (self.generate_range * 2) * (
                    loop) + self.generate_range:
                counter += 1

            if -(self.generate_range * 2) * (loop_num + 1) + self.generate_range > start_p[1] > -(self.generate_range * 2) * (loop_num + 1) - (self.generate_range * 2) \
                    and -(self.generate_range * 2) * (loop_num + 1) + self.generate_range > end_p[1] > -(self.generate_range * 2) * (loop_num + 1) - (self.generate_range * 2):
                counter += 1

            if counter == 2:
                range_check = True
            else:
                range_check = False

            # 両条件を満たしていればOK
            if range_check and gl_check:
                # print('Bridge_specify Success in {}'.format(i))
                pass
            else:
                # print('GL distance is not satisfied')
                return False

            # contact_judge_flag = False
            contact_judge_flag = self.contact_judgement_bridge_specify(unused_timber.id, used_timber1.id, used_timber2.id, already_regenerated_list)
            if contact_judge_flag:
                return False
            else:
                # print('bridge contact judgement is success : {}'.format(i))
                break

        # 使用domainの更新のための値
        select_domain_3_end = abs(int(t_ // domain_range3))
        # print("select_domain_3_end : %s" % (select_domain_3_end))
        used_timber1.select_domain_list.append([select_domain_1, unused_timber.id])
        used_timber2.select_domain_list.append([select_domain_2, unused_timber.id])
        unused_timber.select_domain_list.append([select_domain_3_start, used_timber1.id])
        unused_timber.select_domain_list.append([select_domain_3_end, used_timber2.id])

        # partner_timの更新
        used_timber1.partner_tim.append(unused_timber.id)
        used_timber2.partner_tim.append(unused_timber.id)

        unused_timber.partner_tim.append(used_timber1.id)
        unused_timber.partner_tim.append(used_timber2.id)
        if unused_timber.id == used_timber1.id:
            raise Exception('partner_tim renewal fail')
        if unused_timber.id == used_timber2.id:
            raise Exception('partner_tim renewal fail')

        # 木材同士の最短距離を計算する。
        for i in range(len(self.used_list)):
            already_exist_timber = self.used_list[i]
            already_exist_timber_name = self.used_list[i].id
            if already_exist_timber_name in already_regenerated_list:
                timber.distanceBetweenTimber_RhinoCommon(already_exist_timber, unused_timber)

        return True

    def contact_judgement_cantilever(self, judge_tim_id, ignore_tim_id):

        # 接触判定に使用する部材のsrf情報をリスト内に格納する。
        # deepcopyを使用するかどうかは挙動を見てから決定する。
        list_judge_srf = []
        for i in range(len(self.used_list)):
            if self.used_list[i].id != ignore_tim_id:
                # judge_srf = copy.deepcopy(self.used_list[i].surface)
                judge_srf = self.used_list[i].surface
                list_judge_srf.append(judge_srf)
            else:
                continue

        # print('list_judge_srf', list_judge_srf)

        # 接触判定に使用する部材のsurfaceを取得しておく。
        if len(self.timber_list) != 0:
            for i in range(len(self.timber_list)):
                if judge_tim_id == self.timber_list[i].id:
                    srf_judge_tim = self.timber_list[i].surface
                    break
        else:
            for i in range(len(self.used_list)):
                if judge_tim_id == self.used_list[i].id:
                    srf_judge_tim = self.used_list[i].surface
                    break

        segment_num = 20

        # surfaceを用いた接触判定をおこなう。
        # intersection_flag = False
        for i in range(len(list_judge_srf)):
            srf = list_judge_srf[i]
            tim1_segment_points, tim1_diameter = calculate_srf_segment_points(srf, segment_num)

            tim2_segment_points, tim2_diameter = calculate_srf_segment_points(srf_judge_tim, segment_num)

            tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points,
                                                                    segment_num)

            tim1_min_p = tim1_segment_points[tim1_index]
            tim2_min_p = tim2_segment_points[tim2_index]
            vec = tim1_min_p - tim2_min_p
            length = vec.Length

            judge_value = (tim1_diameter[tim1_index] / 2) + (tim2_diameter[tim2_index] / 2)

            # 接触していたらTrueしていなかったらFalse
            if length <= judge_value:
                intersection_flag = True
            else:
                intersection_flag = False

            if intersection_flag:
                break

        if intersection_flag:
            return True
        else:
            return False

    def contact_judgement_cantilever_specify(self, judge_tim_id, ignore_tim_id, already_regenerate):

        # 接触判定に使用する部材のsrf情報をリスト内に格納する。
        # deepcopyを使用するかどうかは挙動を見てから決定する。
        list_judge_srf = []
        for i in range(len(already_regenerate)):
            if already_regenerate[i] != ignore_tim_id:
                tim_id = already_regenerate[i]
                for j in range(len(self.used_list)):
                    if tim_id == self.used_list[j].id:
                        # judge_srf = copy.deepcopy(self.used_list[j].surface)
                        judge_srf = self.used_list[j].surface
                        list_judge_srf.append(judge_srf)
                        break
                    else:
                        continue

        # print('list_judge_srf', list_judge_srf)

        # 接触判定に使用する部材のsurfaceを取得しておく。
        if len(self.timber_list) != 0:
            for i in range(len(self.timber_list)):
                if judge_tim_id == self.timber_list[i].id:
                    srf_judge_tim = self.timber_list[i].surface
                    break
        else:
            for i in range(len(self.used_list)):
                if judge_tim_id == self.used_list[i].id:
                    srf_judge_tim = self.used_list[i].surface
                    break

        segment_num = 20

        # surfaceを用いた接触判定をおこなう。
        # intersection_flag = False
        for i in range(len(list_judge_srf)):
            srf = list_judge_srf[i]
            tim1_segment_points, tim1_diameter = calculate_srf_segment_points(srf, segment_num)

            tim2_segment_points, tim2_diameter = calculate_srf_segment_points(srf_judge_tim, segment_num)

            tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points,
                                                                    segment_num)

            tim1_min_p = tim1_segment_points[tim1_index]
            tim2_min_p = tim2_segment_points[tim2_index]
            vec = tim1_min_p - tim2_min_p
            length = vec.Length

            judge_value = (tim1_diameter[tim1_index] / 2) + (tim2_diameter[tim2_index] / 2)

            # 接触していたらTrueしていなかったらFalse
            if length <= judge_value:
                intersection_flag = True
            else:
                intersection_flag = False

            if intersection_flag:
                break

        if intersection_flag:
            return True
        else:
            return False

    def contact_judgement_bridge(self, judge_tim_id, ignore_tim_id1, ignore_tim_id2):

        # 接触判定に使用する部材のsrf情報をリスト内に格納する。
        # deepcopyを使用するかどうかは挙動を見てから決定する。
        list_judge_srf = []
        for i in range(len(self.used_list)):
            if self.used_list[i].id != ignore_tim_id1 or self.used_list[i].id != ignore_tim_id2:
                # judge_srf = copy.deepcopy(self.used_list[i].surface)
                judge_srf = self.used_list[i].surface
                list_judge_srf.append(judge_srf)
            else:
                continue

        # print('list_judge_srf', list_judge_srf)

        # 接触判定に使用する部材のsurfaceを取得しておく。
        if len(self.timber_list) != 0:
            for i in range(len(self.timber_list)):
                if judge_tim_id == self.timber_list[i].id:
                    srf_judge_tim = self.timber_list[i].surface
                    break
        else:
            for i in range(len(self.used_list)):
                if judge_tim_id == self.used_list[i].id:
                    srf_judge_tim = self.used_list[i].surface
                    break

        segment_num = 20

        # surfaceを用いた接触判定をおこなう。
        # intersection_flag = False
        for i in range(len(list_judge_srf)):
            srf = list_judge_srf[i]
            tim1_segment_points, tim1_diameter = calculate_srf_segment_points(srf, segment_num)

            tim2_segment_points, tim2_diameter = calculate_srf_segment_points(srf_judge_tim, segment_num)

            tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points,
                                                                    segment_num)

            tim1_min_p = tim1_segment_points[tim1_index]
            tim2_min_p = tim2_segment_points[tim2_index]
            vec = tim1_min_p - tim2_min_p
            length = vec.Length

            judge_value = (tim1_diameter[tim1_index] / 2) + (tim2_diameter[tim2_index] / 2)

            # 接触していたらTrueしていなかったらFalse
            if length <= judge_value:
                intersection_flag = True
            else:
                intersection_flag = False

            if intersection_flag:
                break

        if intersection_flag:
            return True
        else:
            return False

    def contact_judgement_bridge_specify(self, judge_tim_id, ignore_tim_id1, ignore_tim_id2, already_regenerate):

        # 接触判定に使用する部材のsrf情報をリスト内に格納する。
        # deepcopyを使用するかどうかは挙動を見てから決定する。
        list_judge_srf = []
        for i in range(len(already_regenerate)):
            if not already_regenerate[i] == ignore_tim_id1 and not already_regenerate[i] == ignore_tim_id2:
                tim_id = already_regenerate[i]
                # print('tim_id', tim_id)
                for j in range(len(self.used_list)):
                    if tim_id == self.used_list[j].id:
                        # judge_srf = copy.deepcopy(self.used_list[j].surface)
                        judge_srf = self.used_list[j].surface
                        list_judge_srf.append(judge_srf)
                        break
                    else:
                        continue

        # print('list_judge_srf', list_judge_srf)

        # 接触判定に使用する部材のsurfaceを取得しておく。
        if len(self.timber_list) != 0:
            for i in range(len(self.timber_list)):
                if judge_tim_id == self.timber_list[i].id:
                    srf_judge_tim = self.timber_list[i].surface
                    break
        else:
            for i in range(len(self.used_list)):
                if judge_tim_id == self.used_list[i].id:
                    srf_judge_tim = self.used_list[i].surface
                    break

        segment_num = 20

        # surfaceを用いた接触判定をおこなう。
        # intersection_flag = False
        for i in range(len(list_judge_srf)):
            srf = list_judge_srf[i]
            tim1_segment_points, tim1_diameter = calculate_srf_segment_points(srf, segment_num)

            tim2_segment_points, tim2_diameter = calculate_srf_segment_points(srf_judge_tim, segment_num)

            tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points,
                                                                    segment_num)

            tim1_min_p = tim1_segment_points[tim1_index]
            tim2_min_p = tim2_segment_points[tim2_index]
            vec = tim1_min_p - tim2_min_p
            length = vec.Length

            judge_value = (tim1_diameter[tim1_index] / 2) + (tim2_diameter[tim2_index] / 2)

            # 接触していたらTrueしていなかったらFalse
            if length <= judge_value:
                intersection_flag = True
            else:
                intersection_flag = False

            if intersection_flag:
                break

        if intersection_flag:
            return True
        else:
            return False


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
