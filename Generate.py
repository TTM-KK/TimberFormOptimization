# -*- coding:utf-8 -*-

from Timber import Timber
import random as rnd
import math  # ttm add 181003
from forGenerate import timberMethod as timber
import Rhino
from forGenerate import RhinoCommonOriginalMethods as oriRhino


class Generate:

    # 初期化
    def __init__(self, center_line, surface, id, sum_timber, population_id):
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

        # if generate range is predetermined for closed curve, get a point in it TODO 生成の際にぶつからないようにする。
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

        elif objects_point:
            select_index = rnd.randint(0, len(objects_point)-1)

            point_base = objects_point[select_index]
            del objects_point[select_index]  # TODO 他の場所と干渉する恐れがあるので要注意

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

        # 接点からのフリをランダムにする。 TODO 一旦部材がほとんど垂直に置かれていることを前提にアルゴリズムを構築
        restriction_angle = 45

        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 0, 10)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)

        plane1 = Rhino.Geometry.Plane(p1, p2, p3)
        rotate_angle = math.radians(rnd.randint(-restriction_angle, restriction_angle))
        xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], point_base)
        tim_srf.Transform(xf)
        tim_axis.Transform(xf)

        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 10, 0)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)

        plane2 = Rhino.Geometry.Plane(p1, p2, p3)
        rotate_angle = math.radians(rnd.randint(-restriction_angle, -restriction_angle))
        xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], point_base)
        tim_srf.Transform(xf)
        tim_axis.Transform(xf)

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

        for h in range(10):
            if h == 9:
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

            # tim1_srf = rhutil.coercebrep(used_timber.surface)
            # tim2_srf = rhutil.coercebrep(unused_timber.surface)
            tim1_srf = used_timber.surface
            tim2_srf = unused_timber.surface

            # tim1_center_crv = rhutil.coercecurve(used_timber.center_line)
            # tim2_center_crv = rhutil.coercecurve(unused_timber.center_line)
            tim1_center_crv = used_timber.center_line
            tim2_center_crv = unused_timber.center_line

            # cantileverのRun timeを計測する
            # start_time = time.time()

            domain_crv1 = tim1_center_crv.Domain
            domain_crv2 = tim2_center_crv.Domain

            each_domain_length1 = (domain_crv1[1] - domain_crv1[0]) / divide_domain_num
            each_domain_length2 = (domain_crv2[1] - domain_crv2[0]) / divide_domain_num

            select_domain1 = used_timber.select_surface_domain()
            select_domain2 = unused_timber.select_surface_domain()

            # select_domain1 = 2
            # select_domain2 = rnd.randint(0, 9)

            tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + select_domain1 * each_domain_length1)
            tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + select_domain2 * each_domain_length2)

            vec_move = tim1_point - tim2_point

            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            p1 = Rhino.Geometry.Point3d(0, 0, 0)
            p2 = Rhino.Geometry.Point3d(0, 0, 10)
            p3 = Rhino.Geometry.Point3d(10, 0, 0)

            plane1 = Rhino.Geometry.Plane(p1, p2, p3)

            # 部材をGLに生成しないようにする、部材端のz座標を計算している。
            flag_gl = True
            avoid_infinite_loop = 0
            while flag_gl:

                avoid_infinite_loop += 1

                rotate_angle = math.radians(rnd.randint(0, 360))
                xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], tim1_point)
                tim2_center_crv.Transform(xf)
                tim2_srf.Transform(xf)

                tim2_crv_end = tim2_center_crv.PointAtEnd
                tim2_crv_start = tim2_center_crv.PointAtStart

                if tim2_crv_end[2] > 100 and tim2_crv_start[2] > 100:
                    flag_gl = False

                if avoid_infinite_loop > 100:
                    print('infinite loop is occur')
                    break

            if flag_gl:
                continue
            else:
                pass

            # print("rotate angle", math.degrees(rotate_angle))

            # TODO 要検討
            # 角度制約を計算するためのコード
            # tim1_start_point = tim1_center_crv.PointAt(domain_crv1[0])
            # tim1_end_point = tim1_center_crv.PointAt(domain_crv1[1])
            #
            # tim2_start_point = tim2_center_crv.PointAt(domain_crv2[0])
            # tim2_end_point = tim2_center_crv.PointAt(domain_crv2[1])
            #
            # vec_tim1 = tim1_start_point - tim1_end_point
            # vec_tim2 = tim2_start_point - tim2_end_point
            #

            p1 = Rhino.Geometry.Point3d(0, 0, 0)
            p2 = Rhino.Geometry.Point3d(0, 10, 0)
            p3 = Rhino.Geometry.Point3d(10, 0, 0)

            plane2 = Rhino.Geometry.Plane(p1, p2, p3)

            # GLに部材を生成しないために部材端のz座標値を計算
            flag_gl = True
            avoid_infinite_loop = 0
            while flag_gl:

                avoid_infinite_loop += 1

                rotate_angle = math.radians(rnd.randint(0, 360))
                xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], tim1_point)
                tim2_center_crv.Transform(xf)
                tim2_srf.Transform(xf)

                tim2_crv_end = tim2_center_crv.PointAtEnd
                tim2_crv_start = tim2_center_crv.PointAtStart

                if tim2_crv_end[2] > 100 and tim2_crv_start[2] > 100:
                    flag_gl = False

                if avoid_infinite_loop > 100:
                    print('infinite loop is occur')
                    break

            if flag_gl:
                continue
            else:
                pass

            length1, rc1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim1_srf, tim1_point)
            length2, rc2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim2_srf, tim2_point)

            # print("rc1", rc1)
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

            if tim2_crv_end[2] > 100 and tim2_crv_start[2] > 100:
                break
            else:
                continue

        # a = 'tim'
        # b = str(unused_timber.name)
        # print("unused_timber.name", unused_timber.name)
        # rs.CurrentLayer(a + b)
        #
        # cr1 = scriptcontext.doc.Objects.AddCurve(tim2_center_crv)
        # sf1 = scriptcontext.doc.Objects.AddBrep(tim2_srf)
        #
        # a = 'tim'
        # b = str(used_timber.name)
        # print("used_timber.name", used_timber.name)
        # rs.CurrentLayer(a + b)
        #
        # cr2 = scriptcontext.doc.Objects.AddCurve(tim1_center_crv)
        # sf2 = scriptcontext.doc.Objects.AddBrep(tim1_srf)
        #
        # # 以下更新
        # # objectの更新
        # unused_timber.surface = sf1
        # unused_timber.center_line = cr1
        #
        # used_timber.surface = sf2
        # used_timber.center_line = cr2

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

        # end_time = time.time()
        # print("Processing Cantilever_RhinoCommon Time : %s" % (end_time - start_time))
        return True

    def cantilever_specify(self, tim_preexist_num, tim_add_num, already_regenerated_list, limit_degree,
                           generation_num, loop_num, between_draw_rhino):

        gl_distance = 0
        divide_domain_num = 10

        # 各オブジェクトの取得　--->  Timber Instanceに置き換える
        used_timber = self.used_list[tim_preexist_num]
        unused_timber = self.used_list[tim_add_num]

        # tim1_srf = rhutil.coercebrep(self.used_list[tim_preexist_num].surface)
        # tim2_srf = rhutil.coercebrep(self.used_list[tim_add_num].surface)
        #
        # tim1_center_crv = rhutil.coercecurve(self.used_list[tim_preexist_num].center_line)
        # tim2_center_crv = rhutil.coercecurve(self.used_list[tim_add_num].center_line)

        tim1_srf = self.used_list[tim_preexist_num].surface
        tim2_srf = self.used_list[tim_add_num].surface

        tim1_center_crv = self.used_list[tim_preexist_num].center_line
        tim2_center_crv = self.used_list[tim_add_num].center_line

        # cantileverのRun timeを計測する
        # start_time = time.time()

        domain_crv1 = tim1_center_crv.Domain
        domain_crv2 = tim2_center_crv.Domain

        each_domain_length1 = (domain_crv1[1] - domain_crv1[0]) / divide_domain_num
        each_domain_length2 = (domain_crv2[1] - domain_crv2[0]) / divide_domain_num

        select_domain1 = used_timber.select_surface_domain()
        select_domain2 = unused_timber.select_surface_domain()

        # select_domain1 = 2
        # select_domain2 = rnd.randint(0, 9)

        tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + select_domain1 * each_domain_length1)
        tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + select_domain2 * each_domain_length2)

        vec_move = tim1_point - tim2_point

        xf = Rhino.Geometry.Transform.Translation(vec_move)
        tim2_center_crv.Transform(xf)
        tim2_srf.Transform(xf)

        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 0, 10)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)

        plane1 = Rhino.Geometry.Plane(p1, p2, p3)

        # GL Method
        flag = True
        avoid_infinite_loop = 0
        while flag:
            avoid_infinite_loop += 1

            rotate_angle = math.radians(rnd.randint(0, 360))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], tim1_point)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            end_p = tim2_center_crv.PointAtEnd
            start_p = tim2_center_crv.PointAtStart

            if end_p[2] > gl_distance and start_p[2] > gl_distance:
                break
            else:
                pass

            if avoid_infinite_loop > 100:
                break

        if flag:
            return False

        # print("rotate angle", math.degrees(rotate_angle))

        # TODO 要検討
        # 角度制約を計算するためのコード
        # tim1_start_point = tim1_center_crv.PointAt(domain_crv1[0])
        # tim1_end_point = tim1_center_crv.PointAt(domain_crv1[1])
        #
        # tim2_start_point = tim2_center_crv.PointAt(domain_crv2[0])
        # tim2_end_point = tim2_center_crv.PointAt(domain_crv2[1])
        #
        # vec_tim1 = tim1_start_point - tim1_end_point
        # vec_tim2 = tim2_start_point - tim2_end_point
        #

        p1 = Rhino.Geometry.Point3d(0, 0, 0)
        p2 = Rhino.Geometry.Point3d(0, 10, 0)
        p3 = Rhino.Geometry.Point3d(10, 0, 0)

        plane2 = Rhino.Geometry.Plane(p1, p2, p3)

        # GL Method
        flag = True
        avoid_infinite_loop = 0
        while flag:
            avoid_infinite_loop += 1

            rotate_angle = math.radians(rnd.randint(0, 360))
            xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], tim1_point)
            tim2_center_crv.Transform(xf)
            tim2_srf.Transform(xf)

            end_p = tim2_center_crv.PointAtEnd
            start_p = tim2_center_crv.PointAtStart

            if end_p[2] > gl_distance and start_p[2] > gl_distance:
                break
            else:
                pass

            if avoid_infinite_loop > 100:
                break

        if flag:
            return False

        length1, rc1 = oriRhino.GetTimberSectionLength_RhinoCommon(tim1_srf, tim1_point)
        length2, rc2 = oriRhino.GetTimberSectionLength_RhinoCommon(tim2_srf, tim2_point)

        # print("rc1", rc1)
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


        # 以下更新
        # objectの更新
        # TODO いらないか確認
        # unused_timber.surface = tim2_center_crv
        # unused_timber.center_line = tim2_srf

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

        # end_time = time.time()
        # print("Processing Cantilever_RhinoCommon Time : %s" % (end_time - start_time))
        return True

    def bridge(self, limit_degree):
        # start_time = time.time()

        split_ = 200
        split_domain_range_num = 10

        for h in range(100):

            if h > 99:
                raise Exception('bridge GL method is not work well')

            for i in range(20):
                flag_select_timber_domain = True
                flag_select_timber_domain_success = False

                flag_select_timber = False
                for _ in range(1000):
                    # used_timberの選択
                    index = rnd.sample(xrange(len(self.used_list)), 2)
                    x1 = index[0]
                    x2 = index[1]
                    used_timber1 = self.used_list[x1]
                    used_timber2 = self.used_list[x2]

                    # unused_timberの選択
                    y = rnd.randint(0, len(self.timber_list) - 1)
                    unused_timber = self.timber_list[y]

                    length_of_between = used_timber1.tim_distance[used_timber2.id][0]
                    length_of_timber = unused_timber.timber_length
                    # print("length_of_between", length_of_between)
                    # print("length_of_timber", length_of_timber)

                    if length_of_timber < length_of_between:
                        # print("length of timber is lack of length")
                        continue
                    else:
                        flag_select_timber = True
                        break

                if not flag_select_timber:
                    input("check select timber")
                    return False

                # tim1_srf = rhutil.coercebrep(self.used_list[tim_preexist_num_1].surface)
                # tim2_srf = rhutil.coercebrep(self.used_list[tim_preexist_num_2].surface)
                # tim3_srf = rhutil.coercebrep(unused_timber.surface)
                tim3_srf = unused_timber.surface

                # tim1_center_crv = rhutil.coercecurve(used_timber1.center_line)
                # tim2_center_crv = rhutil.coercecurve(used_timber2.center_line)
                # tim3_center_crv = rhutil.coercecurve(unused_timber.center_line)
                tim1_center_crv = used_timber1.center_line
                tim2_center_crv = used_timber2.center_line
                tim3_center_crv = unused_timber.center_line

                # # bridge可能か判断　その１
                # distance = used_timber1.tim_distance[used_timber2.name][0]
                # if distance + 100 > unused_timber.timber_length:
                #     print("reselect timber cuz lack of length: in bridge")
                #     return False

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

                    # GL_01 に材が食い込むなら再選択
                    select_domain_1 = used_timber1.select_surface_domain()  # select_domain はドメインの値をintで返される。
                    select_domain_2 = used_timber2.select_surface_domain()

                    # print("select_domain_1", select_domain_1)
                    # print("select_domain_2", select_domain_2)

                    # TODO　ドメインの指定に関しては範囲内をランダムにする、中心線を単純にするなどによって精度を向上させること可能。
                    tim1_point = tim1_center_crv.PointAt(domain_crv1[0] + domain_range1 * select_domain_1)
                    tim2_point = tim2_center_crv.PointAt(domain_crv2[0] + domain_range2 * select_domain_2)

                    # tim1, tim2間の点と点の長さを取得する
                    distance_between = (tim1_point - tim2_point).Length

                    # bridge可能か判断　その２
                    # length_tim3 = tim3_center_crv.GetLength() - tim3_center_crv.GetLength() / split_domain_range_num * 2
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

                if not flag_select_timber_domain:
                    continue

                if not flag_select_timber_domain_success:
                    input("select timber domain is fail in Generate line 1422")
                else:
                    break
                    # # 制約条件 ---> 接合なす角
                    # if select_domain_loop < 50:
                    #     p1 = tim1_center_crv.PointAt(domain_crv1[0])
                    #     p2 = tim1_center_crv.PointAt(domain_crv1[1])
                    #     p3 = tim2_center_crv.PointAt(domain_crv2[0])
                    #     p4 = tim2_center_crv.PointAt(domain_crv2[1])
                    #
                    #     v1 = p1 - p2
                    #     v2 = p3 - p4
                    #     v3 = tim1_point - tim2_point
                    #
                    #     v1_length = v1.Length
                    #     v2_length = v2.Length
                    #     v3_length = v3.Length
                    #
                    #     cos_theta1 = (v1*v3) / (v1_length*v3_length)
                    #     cos_theta2 = (v2*v3) / (v2_length*v3_length)
                    #
                    #     degree1 = math.degrees(math.acos(cos_theta1))
                    #     degree2 = math.degrees(math.acos(cos_theta2))
                    #
                    #     if limit_degree[0]<  degree1 < limit_degree[1]  and limit_degree[0]<  degree2 < limit_degree[1] :
                    #         # print("OK")
                    #         break
                    #     else:
                    #         # print("NO")
                    #         continue
                    # else:
                    #     break

            # distance_betweenの距離よりもlength_tim3のほうが長かったとしても、EvaluateCurveで選択される点次第で長さが足りなくなることも十分に考えられるだろう。
            # t = domain_crv3[0] + split_range*20
            t = domain_crv3[0] + domain_range3 * select_domain_3_start  # このｔの値が変化することによってかけられるDomainの範囲が自由になる。
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
            # tim3_start_point = tim3_center_crv.PointAt(t)

            # print("tim3_end_point", tim3_end_point)
            # print("tim3_start_point", tim3_start_point)

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

            # tim1とtim2のtim3にたいする外積をそれぞれ求める。
            vec_tim3 = tim3_end_point - tim3_start_point
            tim1_end_point = tim1_center_crv.PointAtEnd
            vec_tim1 = tim1_end_point - tim1_point
            tim2_end_point = tim2_center_crv.PointAtEnd

            vec_tim2 = tim2_end_point - tim2_point

            cross_vec1 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim1)
            cross_vec2 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim2)
            # cross_angle = oriRhino.VectorAngle_RhinoCommon(cross_vec1, cross_vec2)

            # 2つの外積で作成したベクトルを合成し描画する。
            # tim3_center_p_coordinate = tim3_center_crv.PointAt((t_ - t) / 2 + t)
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

            # ここで2つの端部の座標がマイナスになっていなければ処理を続行。マイナスならもう一度Domainの選択からやり直し
            if tim3_end_p[2] > 100 and tim3_start_p[2] > 100:
                break
            else:
                pass

        # # layerを変更して正しいレイヤーへ
        # a = 'tim'
        # b = str(unused_timber.name)
        # print("unused_timber.name", unused_timber.name)
        # rs.CurrentLayer(a + b)
        #
        # cr = scriptcontext.doc.Objects.AddCurve(tim3_center_crv)
        # sf = scriptcontext.doc.Objects.AddBrep(tim3_srf)
        #
        # # 以下更新
        # unused_timber.surface = sf
        # unused_timber.center_line = cr
        #

        # print("tim_srf", tim3_srf)
        # print("tim_center_crv", tim3_center_crv)
        # print("unused_timber.surface", unused_timber.surface)
        # print("unused_timber.center_line", unused_timber.center_line)

        # TODO 多分レイヤーの更新しないといけない。

        # 使用domainの更新のための値
        select_domain_3_end = abs(int(t_ // domain_range3))
        # print("select_domain_3_end : %s" % (select_domain_3_end))
        used_timber1.select_domain_list.append([select_domain_1, unused_timber.id])
        used_timber2.select_domain_list.append([select_domain_2, unused_timber.id])
        unused_timber.select_domain_list.append([select_domain_3_start, used_timber1.id])
        unused_timber.select_domain_list.append([select_domain_3_end, used_timber2.id])

        # partner_tim 更新

        used_timber1.partner_tim.append(unused_timber.id)  # add the partner timber name ---> name is number
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


        # end_time = time.time()
        # print("Processing bridge_RhinoCommon Time : %s" % (end_time - start_time))
        return True

    def bridge_specify(self, tim_preexist_num_1, tim_preexist_num_2, tim_add_num, already_regenerated_list,
                       limit_degree, generation_num, loop_num, between_draw_rhino):
        # start_time = time.time()

        gl_distance = 0

        split_ = 200
        split_domain_range_num = 10

        # 各オブジェクトの取得　--->  Timber Instanceに置き換える
        used_timber1 = self.used_list[tim_preexist_num_1]
        used_timber2 = self.used_list[tim_preexist_num_2]
        unused_timber = self.used_list[tim_add_num]

        # tim1_srf = rhutil.coercebrep(self.used_list[tim_preexist_num_1].surface)
        # tim2_srf = rhutil.coercebrep(self.used_list[tim_preexist_num_2].surface)
        # tim3_srf = rhutil.coercebrep(self.used_list[tim_add_num].surface)
        #
        # tim1_center_crv = rhutil.coercecurve(self.used_list[tim_preexist_num_1].center_line)
        # tim2_center_crv = rhutil.coercecurve(self.used_list[tim_preexist_num_2].center_line)
        # tim3_center_crv = rhutil.coercecurve(self.used_list[tim_add_num].center_line)

        tim3_srf = self.used_list[tim_add_num].surface

        tim1_center_crv = self.used_list[tim_preexist_num_1].center_line
        tim2_center_crv = self.used_list[tim_preexist_num_2].center_line
        tim3_center_crv = self.used_list[tim_add_num].center_line

        # bridge可能か判断　その１
        distance = used_timber1.tim_distance[used_timber2.id][0]
        if distance + 100 > unused_timber.timber_length:
            # print("reselect timber cuz lack of length: in bridge")
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

        # GL Method
        flag_gl_distance = False
        for i in range(10):

            select_domain_3_start = 0  # TODO 今のところ固定値
            for select_domain_loop in range(200):
                select_domain_1 = used_timber1.select_surface_domain()  # select_domain はドメインの値をintで返される。
                select_domain_2 = used_timber2.select_surface_domain()

                # print("select_domain_1", select_domain_1)
                # print("select_domain_2", select_domain_2)

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
                    # # 制約条件 ---> 接合なす角
                    # if select_domain_loop < 50:
                    #     p1 = tim1_center_crv.PointAt(domain_crv1[0])
                    #     p2 = tim1_center_crv.PointAt(domain_crv1[1])
                    #     p3 = tim2_center_crv.PointAt(domain_crv2[0])
                    #     p4 = tim2_center_crv.PointAt(domain_crv2[1])
                    #
                    #     v1 = p1 - p2
                    #     v2 = p3 - p4
                    #     v3 = tim1_point - tim2_point
                    #
                    #     v1_length = v1.Length
                    #     v2_length = v2.Length
                    #     v3_length = v3.Length
                    #
                    #     cos_theta1 = (v1*v3) / (v1_length*v3_length)
                    #     cos_theta2 = (v2*v3) / (v2_length*v3_length)
                    #
                    #     degree1 = math.degrees(math.acos(cos_theta1))
                    #     degree2 = math.degrees(math.acos(cos_theta2))
                    #
                    #     if limit_degree[0]<  degree1 < limit_degree[1]  and limit_degree[0]<  degree2 < limit_degree[1] :
                    #         # print("OK")
                    #         break
                    #     else:
                    #         # print("NO")
                    #         continue
                    # else:
                    #     break

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
                tim3_end_point_coordinate = tim3_center_crv.PointAt(t_)  # RhinoCommon
                distance = (tim3_end_point_coordinate - tim3_start_point_coordinate).Length  # RhinoCommon
                if distance > distance_between:
                    break
                if avoid_ > 100:
                    input("infinite loop: select_domain_3_end")

            # ObjectのMove
            vec_move = tim1_point - tim3_start_point_coordinate  # RhinoCommon
            # print("vec_move", vec_move)
            xf = Rhino.Geometry.Transform.Translation(vec_move)
            tim3_center_crv.Transform(xf)
            tim3_srf.Transform(xf)

            # 再計測
            tim3_end_point = tim3_center_crv.PointAt(t_)
            # tim3_start_point = tim3_center_crv.PointAt(t)

            # print("tim3_end_point", tim3_end_point)
            # print("tim3_start_point", tim3_start_point)

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

            # tim1とtim2のtim3にたいする外積をそれぞれ求める。
            vec_tim3 = tim3_end_point - tim3_start_point
            tim1_end_point = tim1_center_crv.PointAtEnd
            vec_tim1 = tim1_end_point - tim1_point
            tim2_end_point = tim2_center_crv.PointAtEnd
            vec_tim2 = tim2_end_point - tim2_point

            cross_vec1 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim1)
            cross_vec2 = Rhino.Geometry.Vector3d.CrossProduct(vec_tim3, vec_tim2)
            # cross_angle = oriRhino.VectorAngle_RhinoCommon(cross_vec1, cross_vec2)

            # 2つの外積で作成したベクトルを合成し描画する。
            # tim3_center_p_coordinate = tim3_center_crv.PointAt((t_ - t) / 2 + t)
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

            end_p = tim3_center_crv.PointAtEnd
            start_p = tim3_center_crv.PointAtStart

            if end_p[2] > gl_distance and start_p[2] > gl_distance:
                flag_gl_distance = True
                break
            else:
                continue

        if flag_gl_distance:
            pass
        else:
            print('GL distance is not satisfied')
            return False

        # 以下更新
        # unused_timber.surface = sf
        # unused_timber.center_line = cr
        # print("tim_srf", tim3_srf)
        # print("tim_center_crv", tim3_center_crv)
        # print("unused_timber.surface", unused_timber.surface)
        # print("unused_timber.center_line", unused_timber.center_line)

        # TODO 多分レイヤーの更新しないといけない。

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

        # end_time = time.time()
        # print("Processing bridge_RhinoCommon Time : %s" % (end_time - start_time))
        return True

    # 接合数を確かめ、それに応じてlayer分けする
    # def checkjointCount(self, run_time):
    #
    #     # add layer
    #     prototype = "prototype" + str(self.prototype_name)
    #     parent_layer = rs.AddLayer(prototype, [0, 0, 0], True, False, None)
    #     not_use_list = rs.AddLayer("not_use_list", [0, 0, 0], True, False, parent_layer)
    #     used_list = rs.AddLayer("used_list", [0, 0, 0], True, False, parent_layer)
    #     text_layer = rs.AddLayer("Text", [0, 0, 0], True, False, parent_layer)
    #     rs.AddLayer("collision", [255, 0, 0], True, False, parent_layer)
    #
    #     # draw text
    #     text_content = prototype + "\n" \
    #                    + "Number of timber = " + str(self.sum_timber) + "\n" \
    #                    + "Run time: " + str(run_time)
    #
    #     text_coordinate = [5000 * self.prototype_name, 330, 0]
    #     text = rs.AddText(text_content, text_coordinate, 100, "Arial")
    #     rs.ObjectLayer(text, text_layer)
    #
    #     # used_list
    #     for i in range(0, len(self.used_list)):
    #         if i == 0:
    #             # print("#######################################################")
    #             # print("used_list : %s timber" %(len(self.used_list)))
    #             # print("%s : Number of joint = %s | Select surface domain = %s | Joint name = %s"
    #             #       % (self.used_list[i].name, self.used_list[i].num_joint,
    #             #          self.used_list[i].select_domain_list, self.used_list[i].joint_name_list))
    #
    #             # layer分けをする
    #             Parent_layer = used_list
    #             child1_layer = self.used_list[i].id
    #
    #             # child1 layer
    #             timber_ID = rs.AddLayer(child1_layer, [0, 0, 0], True, False, Parent_layer)
    #
    #             # child2 layer
    #             surface = rs.AddLayer("surface", [220, 220, 220], True, False, timber_ID)
    #             center_line = rs.AddLayer("center line", [0, 0, 0], True, False, timber_ID)
    #             drill_line = rs.AddLayer("drill line", [0, 0, 0], True, False, timber_ID)
    #
    #             rs.ObjectLayer(self.used_list[i].surface, surface)
    #             rs.ObjectLayer(self.used_list[i].center_line, center_line)
    #             for j in range(0, len(self.used_list[i].drill_line_list)):
    #                 rs.ObjectLayer(self.used_list[i].drill_line_list[j], drill_line)
    #
    #         else:
    #             # # print("%s : Number of joint = %s | Select surface domain = %s | Joint name = %s"
    #             #       % (self.used_list[i].name, self.used_list[i].num_joint,
    #             #          self.used_list[i].select_domain_list, self.used_list[i].joint_name_list))
    #
    #             # layer分けをする
    #             Parent_layer = used_list
    #             child1_layer = self.used_list[i].id
    #
    #             # child1 layer
    #             timber_ID = rs.AddLayer(child1_layer, [0, 0, 0], True, False, Parent_layer)
    #
    #             # child2 layer
    #             surface = rs.AddLayer("surface", [220, 220, 220], True, False, timber_ID)
    #             center_line = rs.AddLayer("center line", [0, 0, 0], True, False, timber_ID)
    #             drill_line = rs.AddLayer("drill line", [0, 0, 0], True, False, timber_ID)
    #
    #             rs.ObjectLayer(self.used_list[i].surface, surface)
    #             rs.ObjectLayer(self.used_list[i].center_line, center_line)
    #             for j in range(0, len(self.used_list[i].drill_line_list)):
    #                 rs.ObjectLayer(self.used_list[i].drill_line_list[j], drill_line)
    #
    #     # do not use list
    #     for i in range(0, len(self.not_use_list)):
    #         if i == 0:
    #             # print("-------------------------------------------------------")
    #             # print("not_use_list : %s timber" %(len(self.not_use_list)))
    #             # print("%s :Number of joint = %s | Select surface domain = %s | Joint name = %s"
    #             #       % (self.not_use_list[i].name, self.not_use_list[i].num_joint,
    #             #          self.not_use_list[i].select_domain_list, self.not_use_list[i].joint_name_list))
    #
    #             # layer分けをする
    #             Parent_layer = not_use_list
    #             child1_layer = self.not_use_list[i].id
    #
    #             # child1 layer
    #             timber_ID = rs.AddLayer(child1_layer, [0, 0, 0], True, False, Parent_layer)
    #
    #             # child2 layer
    #             surface = rs.AddLayer("surface", [255, 0, 0], True, False, timber_ID)
    #             center_line = rs.AddLayer("center line", [0, 0, 0], True, False, timber_ID)
    #             drill_line = rs.AddLayer("drill line", [0, 0, 0], True, False, timber_ID)
    #
    #             rs.ObjectLayer(self.not_use_list[i].surface, surface)
    #             rs.ObjectLayer(self.not_use_list[i].center_line, center_line)
    #             for j in range(0, len(self.not_use_list[i].drill_line_list)):
    #                 rs.ObjectLayer(self.not_use_list[i].drill_line_list[j], drill_line)
    #
    #         else:
    #             # print("%s : Number of joint = %s | Select surface domain = %s | Joint name = %s"
    #             #       % (self.not_use_list[i].name, self.not_use_list[i].num_joint,
    #             #          self.not_use_list[i].select_domain_list, self.not_use_list[i].joint_name_list))
    #
    #             # layer分けをする
    #             Parent_layer = not_use_list
    #             child1_layer = self.not_use_list[i].id
    #
    #             # child1 layer
    #             timber_ID = rs.AddLayer(child1_layer, [0, 0, 0], True, False, Parent_layer)
    #
    #             # child2 layer
    #             surface = rs.AddLayer("surface", [255, 0, 0], True, False, timber_ID)
    #             center_line = rs.AddLayer("center line", [0, 0, 0], True, False, timber_ID)
    #             drill_line = rs.AddLayer("drill line", [0, 0, 0], True, False, timber_ID)
    #
    #             rs.ObjectLayer(self.not_use_list[i].surface, surface)
    #             rs.ObjectLayer(self.not_use_list[i].center_line, center_line)
    #             for j in range(0, len(self.not_use_list[i].drill_line_list)):
    #                 rs.ObjectLayer(self.not_use_list[i].drill_line_list[j], drill_line)

    # def checkPartner(self, loop_num):
    #
    #     if loop_num == 0:
    #         for i in range(len(self.used_list)):
    #             timber = self.used_list[i]
    #             srf1 = self.used_list[i].surface
    #
    #             count = 0
    #             for j in range(len(self.used_list) - 1):
    #                 if count == i:
    #                     count = count + 1
    #                 else:
    #                     curve = rs.IntersectBreps(srf1, self.used_list[count].surface)
    #                     if curve is None:
    #                         count = count + 1
    #                         continue
    #                     else:
    #                         timber.partner_tim.append(self.used_list[count])
    #                         count = count + 1
    #                         for k in range(len(curve)):
    #                             rs.DeleteObject(curve[k])
    #
    #         return timber.partner_tim
    #
    #     else:
    #         for i in range(len(self.used_list)):
    #             timber = self.used_list[i]
    #             srf = self.used_list[i].surface
    #
    #             count = 0
    #             for j in range(len(self.used_list) - 1):
    #                 if count == i:
    #                     count = count + 1
    #                 else:
    #                     curve = rs.IntersectBreps(srf, self.used_list[count].surface)
    #                     if curve is None:
    #                         count = count + 1
    #                         continue
    #                     else:
    #                         timber.partner_tim = []
    #                         timber.partner_tim.append(self.used_list[count])
    #                         count = count + 1
    #                         for k in range(len(curve)):
    #                             rs.DeleteObject(curve[k])
