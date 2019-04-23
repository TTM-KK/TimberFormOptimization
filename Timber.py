# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs
import random as rnd
import math
from forTimber import RhinoCommonOriginalMethods as rsOri


class Timber:

    # 初期化
    def __init__(self, center_line, surface, name):
        self.name = name  # timberのID
        self.num_joint = 0  # 接合数
        self.two_mark_line = None  # ロボットアームを使用する際に目印になる2本のライン
        self.center_line = center_line  # 中心線
        self.timber_length = None  # 中心線の長さ
        self.surface = surface  # timberサーフェス
        self.domainU = None  # timberサーフェスのdomainU
        self.domainV = None  # timberサーフェスのdomainV
        self.select_u = None  # 選択したあるUの値
        self.select_v = None  # 選択したあるVの値
        self.point = None  # サーフェス上の任意の一点(座標)
        self.closest_point = None  # 任意の一点(サーフェス上)から中心線に垂線を下した時の点
        self.section_curve = None  # 仮想断面線
        self.cross_vector = None  # 外積ベクトル(仮想断面上を平面として)
        self.offset_vector = None  # 断面と断面のオフセット距離
        self.split_surface_number = 10  # timberサーフェスをある分割数によって分割する際の値
        self.sum_distance_ends = None  # timberサーフェスの両端部(接合させない)の距離の合計（接合禁止エリアの指定のため）
        self.select_domain_list = []  # 接合する際にどの分割サーフェスエリアで接合したかを格納するリスト  ---> 構造として[[接合に使用しているドメイン, 接合している材], [], [].....]となる
        self.drill_line_list = []  # 接合部のドリルラインを格納するリスト
        self.joint_name_list = []  # timberAがどの部材(B,C,D...)と接続しているかを格納するリスト
        self.center_line_parameter_list = []  # 中心線のパラメータ値を格納するリスト(分割点)
        self.base_point_list = []  # 中心線の分割点情報を格納するリスト（split_surface_numberにとって数が決定する
        self.section_length = None  # timberの断面直径の推定値を格納する。

        self.partner_tim = []  # ttm add 1011
        self.temp_partner_tim = []  # ttm add
        self.tim_distance = None  # ttm add

    # 中心線の長さを測る
    def mesureLength(self):
        # print("center?line",self.center_line)
        length_timber = rs.CurveLength(self.center_line)
        self.timber_length = length_timber


    def mesureLength_RhinoCommon(self):
        # curve_domain = self.center_line.Domain
        # length_timber = (self.center_line.AtPoint(curve_domain[0]) - self.center_line.AtPoint(curve_domain[1])).Length
        length_timber = self.center_line.GetLength()
        self.timber_length = length_timber
        # print("length_timber", length_timber)
        # return length_timber

    # 断面の直径を取得する. RhinoCommonメソッド。
    def mesureSectionLength(self):
        rc, t = self.center_line.NormalizedLengthParameter(0.5)
        base_p = self.center_line.PointAt(t)
        length, list_p = rsOri.GetTimberSectionLength_RhinoCommon(self.surface, base_p)
        self.section_length = length

    # tim_distanceのリスト初期設定
    def initDistance(self, tim_number):
        self.tim_distance = []
        for i in range(tim_number):
            self.tim_distance.append([])

    # サーフェスのドメインを選択する --> 変更の余地あり
    def selectSurfaceDomain(self, select_num=None):

        # 接触部が1つの時  一定の距離を開けて生成するためのアルゴリズム
        if len(self.select_domain_list) == 1 and select_num is None:
            used_domain = self.select_domain_list[0]
            if used_domain < 4:  # used_domain   --> 1, 2, 3
                select_domain = used_domain + 4  # select_domain --> 5, 6, 7
            elif used_domain > 4:  # used_domain   --> 5, 6, 7
                select_domain = used_domain - 4  # select_domain --> 1, 2, 3
            else:  # used_domain   --> 4
                select_domain = rnd.choice([1, 7])  # select_domain --> 1, 7

        # 接触部が2つの時
        elif len(self.select_domain_list) == 2 and select_num is None:

            if 4 in self.select_domain_list and 7 in self.select_domain_list:
                select_domain = 1
            elif 4 in self.select_domain_list and 1 in self.select_domain_list:
                select_domain = 7
            elif 3 in self.select_domain_list and 5 in self.select_domain_list:
                select_domain = 7
            else:
                select_domain = int(round(abs(self.select_domain_list[0] + self.select_domain_list[1]) / 2))

        # 接触部がない時(初期生成)
        else:
            if select_num is None:
                select_domain = rnd.randint(0, 8)  # ttm change original is rnd.randint(1, 7)
            else:
                select_domain = select_num

        while True:
            # もし選んだselect domainが使用していないものであったら
            if select_domain not in self.select_domain_list:
                return select_domain
            # もし選んだselect domainがすでに使用されていたら
            else:
                select_domain = rnd.randint(1, 7)

    # サーフェスのドメインを選択する --> 変更の余地あり  select_domain_list change ver
    def selectSurfaceDomain_1(self, select_num=None):

        selected_domain = []
        for i in range(len(self.select_domain_list)):
            selected_domain.append(self.select_domain_list[i][0])

        # 接触部が1つの時  一定の距離を開けて生成するためのアルゴリズム
        if len(self.select_domain_list) == 1 and select_num is None:
            used_domain = self.select_domain_list[0][0]
            if used_domain < 4:  # used_domain   --> 1, 2, 3
                select_domain = used_domain + 4  # select_domain --> 5, 6, 7
            elif used_domain > 4:  # used_domain   --> 5, 6, 7
                select_domain = used_domain - 4  # select_domain --> 1, 2, 3
            else:  # used_domain   --> 4
                select_domain = rnd.choice([1, 7])  # select_domain --> 1, 7

        # 接触部が2つの時
        elif len(self.select_domain_list) == 2 and select_num is None:

            if 4 in selected_domain and 7 in selected_domain:
                select_domain = 1
            elif 4 in selected_domain and 1 in selected_domain:
                select_domain = 7
            elif 3 in selected_domain and 5 in selected_domain:
                select_domain = 7
            else:
                select_domain = int(round(abs(self.select_domain_list[0][0] + self.select_domain_list[1][0]) / 2))

        # 接触部がない時(初期生成)
        else:
            if select_num is None:
                select_domain = rnd.randint(0, 9)  # ttm change original is rnd.randint(1, 7)
            else:
                select_domain = select_num

        while True:
            # もし選んだselect domainが使用していないものであったら
            if select_domain not in selected_domain:
                return select_domain
            # もし選んだselect domainがすでに使用されていたら
            else:
                select_domain = rnd.randint(0, 9)  # ttm change original is rnd.randint(1, 7)


    def selectSurfaceDomain_2(self):

        selected_domain = []
        for i in range(len(self.select_domain_list)):
            selected_domain.append(self.select_domain_list[i][0])

        count = 0
        while True:
            count = count + 1
            select_domain = rnd.randint(1, 8)
            # もし選んだselect domainが使用していないものであったら
            if select_domain not in selected_domain:
                return select_domain
            if count > 100:
                # print("select_used_domain cuz all domains are used")
                # raise Exception('domain is not selected cuz all domain is used')
                return select_domain

    # サーフェスから制限範囲内のある一点のuパラメータを取得する
    def getSurfaceUparameter(self, select_domain):

        self.domainU = rs.SurfaceDomain(self.surface, 0)
        self.domainV = rs.SurfaceDomain(self.surface, 1)

        split_SurfaceArea = (self.domainU[1] - self.domainU[0]) / self.split_surface_number

        if select_domain == None:  # ttm add 1012 for error
            select_domain = rnd.randint(1,7)

        start_domain = split_SurfaceArea * select_domain
        end_domain = split_SurfaceArea * (select_domain + 1)

        sel_u = rnd.uniform(start_domain, end_domain)

        return sel_u

    # Timberのサーフェスの中心線の分割数における点情報とパラメータ値を生成する
    # TODO この段階で分割数分のBasepointを生成する必要性はあるのかという疑問がのこる
    def createSurfaceDomainInfo(self):

        self.domainU = rs.SurfaceDomain(self.surface, 0)
        self.domainV = rs.SurfaceDomain(self.surface, 1)
        split_SurfaceArea = (self.domainU[1] - self.domainU[0]) / self.split_surface_number

        # サーフェスをsplit_num分割した際の点のパラメータ値をリストに格納する
        for select_domain in range(0, self.split_surface_number):
            if select_domain == 0:
                base_point = rs.CurveEndPoint(self.center_line)
                self.base_point_list.append(base_point)
            elif select_domain == 9:
                base_point = rs.CurveStartPoint(self.center_line)
                self.base_point_list.append(base_point)
            else:
                sel_u = split_SurfaceArea * select_domain
                point_list = self.getPointsfromSectionCurve(3, sel_u)  # 断面曲線を作成するためのサーフェス上のポイント群を取得する
                section_polyline = rs.AddPolyline(point_list)  # point_listから断面曲線を作成
                base_point = self.createBasePointFromCurve(section_polyline)  # 断面曲線からサーフェスを作成。作成したサーフェスと材の中心曲線の交点をBasePointとしてreturnする。
                self.base_point_list.append(base_point)

                # objectを削除
                rs.DeleteObject(section_polyline)

        dis1 = rs.Distance(self.base_point_list[0], self.base_point_list[1])
        if dis1 > 700:

            for i in range(0, self.split_surface_number):
                if i == 0:
                    parameter = rs.CurveClosestPoint(self.center_line,
                                                     self.base_point_list[self.split_surface_number - 1])
                    self.center_line_parameter_list.append(parameter)
                elif i == 9:
                    parameter = rs.CurveClosestPoint(self.center_line, self.base_point_list[0])  # cureveのparameterを返り値として返す
                    self.center_line_parameter_list.append(parameter)
                else:
                    parameter = rs.CurveClosestPoint(self.center_line, self.base_point_list[i])
                    self.center_line_parameter_list.append(parameter)

            ends1 = rs.Distance(self.base_point_list[9], self.base_point_list[1])
            ends2 = 240  # ロボットアームの目印2本の範囲は接合しないため固定値になっている(関口)
            # ends2 = rs.Distance(self.base_point_list[8], self.base_point_list[0])

            self.sum_distance_ends = ends1 + ends2

        else:
            for i in range(0, self.split_surface_number):
                parameter = rs.CurveClosestPoint(self.center_line, self.base_point_list[i])
                self.center_line_parameter_list.append(parameter)

            ends1 = rs.Distance(self.base_point_list[0], self.base_point_list[1])
            ends2 = 240
            # ends2 = rs.Distance(self.base_point_list[8], self.base_point_list[9])

            self.sum_distance_ends = ends1 + ends2

    # ある点が分割サーフェスのどのドメインにあるか判断する
    def judgeSurfaceDomain(self, reference_point):

        closest_parameter = rs.CurveClosestPoint(self.center_line, reference_point)

        # reference pointのパラメータ値と分割サーフェスのパラメータ値を比較する
        for select_domain in range(self.split_surface_number - 1):
            para1 = self.center_line_parameter_list[select_domain]
            para2 = self.center_line_parameter_list[select_domain + 1]

            if para1 > para2:
                start = para2
                end = para1
            else:
                start = para1
                end = para2

            if start <= closest_parameter <= end:
                return select_domain

        return False

    # サーフェスから任意のある一点を取得する
    def getRandomSurfacePoint(self, sel_u):

        self.select_u = sel_u
        self.select_v = rnd.uniform(self.domainV[0], self.domainV[1])

        self.point = rs.EvaluateSurface(self.surface, self.select_u, self.select_v)

        return self.point

    # サーフェスを分割し、分割点情報を取得する(仮想断面線)
    def getPointsfromSectionCurve(self, split_num, sel_u):

        surface = self.surface
        point_list = []

        v = (self.domainV[1] - self.domainV[0]) / split_num

        for i in range(0, split_num + 1, 1):
            du = sel_u  # --> duの値が固定値の時、断面線上の点
            dv = ((v * i) * -1.0) + self.domainV[1]  # --> dvの値が固定値の時、Surface上の曲線点
            # print("du", du)
            # print("dv", dv)

            point = rs.EvaluateSurface(surface, du, dv)
            point_list.append(point)

        return point_list

    # polylineを分割し、その分割点情報を返す --> 変更する
    def createBasePointFromCurve(self, curve):

        # base pointを生成する
        if rs.IsCurve(curve):
            srf = rs.AddPlanarSrf(curve)

            # ttm add とてつもなく小さなサーフェスが生成されることが有り、それを取り除くため。
            if len(srf) != 1:
                area_list = []
                for i in range(len(srf)):
                    area = rs.Area(srf[i])
                    area_list.append(area)
                max_area = max(area_list)
                index = area_list.index(max_area)
                srf = srf[index]

            inter = rs.CurveSurfaceIntersection(self.center_line, srf)
        else:
            return False

        if inter is None:
            return False
        else:
            base_point = inter[0][1]

        # objectを削除
        rs.DeleteObject(srf)

        return base_point

    # ClosestPoint(中心点)を生成する --> 変更
    def createVectorClosestPointToCurve(self, eva_p):
        para = rs.CurveClosestPoint(self.center_line, eva_p)
        self.closest_point = rs.EvaluateCurve(self.center_line, para)


    def createCrossVectorOnSectionCurve(self, point_list):

        # 仮想断面を構成する任意の２点を選択する
        # index = rnd.sample(xrange(len(point_list)), 2)
        p1 = point_list[0]
        p2 = point_list[1]

        # base pointを生成する
        curve = rs.AddPolyline(point_list)  # timberの断面曲線
        srf = rs.AddPlanarSrf(curve)

        inter = rs.CurveSurfaceIntersection(self.center_line, srf)  # 中心線と断面平面の交点

        base_point = inter[0][1]

        # 外積を求めるための２つのベクトルを生成
        v1 = rs.VectorCreate(p1, base_point)
        v2 = rs.VectorCreate(p2, base_point)

        cross = rs.VectorCrossProduct(v1, v2)
        cross_unit = rs.VectorUnitize(cross)
        # print(cross_unit)
        self.cross_vector = rs.VectorScale(cross_unit, 100)  # 外積を変数として保持

        # section_curveを生成する

        # 平面を再定義
        self.setPlane(base_point, p1, p2)

        direction = rs.VectorCreate(p1, base_point)
        offset_curve = rs.OffsetCurve(curve, direction, 200)  # ttm change 50 --> 200
        offset_srf = rs.AddPlanarSrf(offset_curve)


        # cross_crv = rs.IntersectBreps(offset_srf, self.surface)  # ttm add 1013
        # if len(cross_crv) != 1:
        #     length_crv = []
        #     for i in range(len(cross_crv)):
        #         len_1 = rs.CurveLength(cross_crv[i])
        #         length_crv.append(len_1)
        #
        #     id = length_crv.index(max(length_crv))
        #     self.section_curve = cross_crv[id]
        #
        # else:
        #     self.section_curve = cross_crv
        # print("check offset_srf", offset_srf)
        # print("check self.surface",self.surface)
        self.section_curve = rs.IntersectBreps(offset_srf, self.surface)  # TODO　self.surfaceが上手く格納されてない可能性も大　


        # デフォルトxy平面に戻す
        self.setDefaultPlane()

        # 描画
        # self.AddVector(base_point, v1)
        # self.AddVector(base_point, v2)
        # self.AddVector(base_point, self.cross_vector)
        # rs.AddPoint(base_point)
        # rs.AddPoint(p3)
        # rs.AddPoint(self.point)

        # objectを削除
        rs.DeleteObject(srf)
        rs.DeleteObject(curve)
        rs.DeleteObject(offset_srf)
        rs.DeleteObject(offset_curve)

        return base_point

    # ドメインを選択しなおす
    def reselectSurfaceDomain(self, reset_domain_count, select_domain_list, select_domain=None):

        # 接点1のサーフェスドメインを変更する
        if reset_domain_count == 0 or reset_domain_count == 1:
            # 接合部がない場合
            if len(select_domain_list) == 0:
                ex_joint = select_domain
                if ex_joint < 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が1つの場合
            elif len(select_domain_list) == 1:
                ex_joint = select_domain_list[0]
                if ex_joint < 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が2つの場合
            elif len(select_domain_list) == 2:
                ex_joint = select_domain_list[1]
                if ex_joint <= 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が3つの場合
            elif len(select_domain_list) == 3:
                ex_joint = select_domain_list[2]
                if ex_joint <= 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain


    # ドメインを選択しなおす ---> select_domain_listの構造が異なるVer
    def reselectSurfaceDomain_1(self, reset_domain_count, select_domain_list, select_domain=None):

        # 接点1のサーフェスドメインを変更する
        if reset_domain_count == 0 or reset_domain_count == 1:
            # 接合部がない場合
            if len(select_domain_list) == 0:
                ex_joint = select_domain
                if ex_joint < 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が1つの場合
            elif len(select_domain_list) == 1:
                ex_joint = select_domain_list[0][0]
                if ex_joint < 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が2つの場合
            elif len(select_domain_list) == 2:
                ex_joint = select_domain_list[1][0]
                if ex_joint <= 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

            # 接合部が3つの場合
            elif len(select_domain_list) == 3:
                ex_joint = select_domain_list[2][0]
                if ex_joint <= 4:
                    choice_domain = ex_joint + rnd.randint(1, 3)
                    return choice_domain
                else:
                    choice_domain = ex_joint - rnd.randint(1, 3)
                    return choice_domain

    # timberを動かす(GLからの生成)
    def moveTimberToGL(self, p1, p2):
        trans = rs.VectorCreate(p1, p2)  # --> vector

        rs.MoveObject(self.surface, trans)  # move edges_list
        rs.MoveObject(self.center_line, trans)  # move line
        rs.MoveObject(self.two_mark_line[0], trans)  # move mark line1
        rs.MoveObject(self.two_mark_line[1], trans)  # move mark line2

    # timberを動かす
    def moveTimber(self, p1, p2):
        trans = rs.VectorCreate(p1, p2)  # --> vector

        rs.MoveObject(self.surface, trans)  # move edges_list
        rs.MoveObject(self.center_line, trans)  # move line
        rs.MoveObject(self.section_curve, trans)  # move section curve
        rs.MoveObject(self.two_mark_line[0], trans)  # move mark line1
        rs.MoveObject(self.two_mark_line[1], trans)  # move mark line2

        self.closest_point = rs.PointAdd(self.closest_point, trans)
        self.point = rs.PointAdd(self.point, trans)
        rs.PointAdd(p2, trans)

    # オフセットするベクトルを求め、そのベクトル方向の点を返す
    def selectOffsetVectorPoint(self, select_u, _base_point, _base_line, reference_p, cantilever_flag=False):

        if _base_line is None:
            return False

        split_num = 150
        point_list = self.getPointsfromSectionCurve(split_num, select_u)
        # point_list = select_u
        base_point = _base_point
        base_line = _base_line
        reference_point = reference_p

        # 条件を満たすオフセット点をリストに格納する
        offset_p_list = []

        for p in range(split_num):
            point = rs.AddPoint(point_list[p])
            line1 = rs.AddLine(base_point, point)
            line2 = base_line

            point1 = (rs.CurveStartPoint(line1), rs.CurveEndPoint(line1))
            point2 = (rs.CurveStartPoint(line2), rs.CurveEndPoint(line2))

            # 2直線のなす角を求める
            angle = rs.Angle2(point1, point2)

            if cantilever_flag is False:
                # オフセット条件(bridgeの場合)
                if 85 < angle[0] < 95:
                    offset_p_list.append(point)

                    # objectを削除
                    rs.DeleteObject(line1)

                # オフセット条件を満たさない場合
                else:
                    rs.DeleteObject(point)
                    rs.DeleteObject(line1)

            # オフセット条件(片持ちの場合)
            elif cantilever_flag is True:
                if 70 < angle[0] < 110:
                    offset_p_list.append(point)

                    # objectを削除
                    rs.DeleteObject(line1)

                # オフセット条件を満たさない場合
                else:
                    rs.DeleteObject(point)
                    rs.DeleteObject(line1)

        # 条件を満たしたオフセット点と基準点との距離をリストに格納する
        distance_point = []

        for p in range(0, len(offset_p_list)):
            point = offset_p_list[p]
            distance = rs.Distance(point, reference_point)
            distance_point.append(distance)

        # オフセット点がない場合
        if len(distance_point) == 0:
            return False

        select_p_index = distance_point.index(min(distance_point))
        select_p = offset_p_list[select_p_index]

        # objectを削除
        for point in offset_p_list:
            if point is select_p:
                continue
            rs.DeleteObject(point)

        return select_p

    def offsetTimber(self, cross_vec, centerPoint, trans_point, polyline2=None):

        # 外積で求めたベクトルからxy平面を再定義する
        origin_point = centerPoint
        x_point = rs.PointAdd(centerPoint, self.cross_vector)
        y_point = rs.PointAdd(centerPoint, cross_vec)

        vec1 = rs.VectorCreate(x_point, centerPoint)
        vec2 = rs.VectorCreate(y_point, centerPoint)

        # Planeを再定義する
        self.setPlane(origin_point, x_point, y_point)

        # new_planeに垂直なベクトル
        axis_vector = rs.VectorCrossProduct(vec1, vec2)
        axis_vector_unit = rs.VectorUnitize(axis_vector)

        if axis_vector_unit is not None:

            axis_vector = rs.VectorScale(axis_vector_unit, 100)

            # 2本のtimberのcrossベクトルの内積を求めそのなす角を求める
            dot = rs.VectorDotProduct(vec1, vec2)  # 内積
            vec1_length = rs.VectorLength(vec1)  # |vec1|
            vec2_length = rs.VectorLength(vec2)  # |vec2|
            cos_theta = dot / (vec1_length * vec2_length)  # cos_theta

            if cos_theta < -1.0:
                pass
                # print("cos_theta < -1.0")

            elif cos_theta > 1.0:
                pass
                # print("cos_theta > 1.0")

            else:
                theta = math.degrees(math.acos(cos_theta))  # 求めたい角度
                rs.RotateObject(self.surface, centerPoint, theta, axis_vector)
                rs.RotateObject(self.center_line, centerPoint, theta, axis_vector)
                rs.RotateObject(self.section_curve, centerPoint, theta, axis_vector)
                rs.RotateObject(self.two_mark_line[0], centerPoint, theta, axis_vector)
                rs.RotateObject(self.two_mark_line[1], centerPoint, theta, axis_vector)

        # timberの半径を考慮してオフセットをする
        line1 = rs.AddLine(trans_point, centerPoint)
        rs.ExtendCurveLength(line1, 0, 2, 400)

        # inter_point = rs.CurveCurveIntersection(line1, self.section_curve)  # surfaceにintersectできいればinter_point必ず出力されるのでは
        inter_point = rs.CurveSurfaceIntersection(line1, self.surface)  # ttm change

        if inter_point is None:
            inter_point = rs.CurveCurveIntersection(line1, polyline2)

        # if inter_point is None:  # ttm add 1012
        #     inter_point = centerPoint

        # print("inter_point", inter_point)  # TODO
        # print("inter_point, len() is unsized object", inter_point)  # TODO
        if len(inter_point) == 2:  # len() of unsized object
            inter_p1 = inter_point[1][1]
            inter_p2 = inter_point[0][1]

            distance1 = rs.Distance(trans_point, inter_p1)
            distance2 = rs.Distance(trans_point, inter_p2)

            if distance1 > distance2:
                select_point = inter_p1
            else:
                select_point = inter_p2

        elif len(inter_point) == 1:
            select_point = inter_point[0][1]
        else:
            # print("There is not select point")
            select_point = centerPoint

        self.offset_vector = rs.VectorCreate(trans_point, select_point)

        # 重なったtimberをoffset分だけ移動する
        rs.MoveObject(self.surface, self.offset_vector)
        rs.MoveObject(self.center_line, self.offset_vector)
        rs.MoveObject(self.section_curve, self.offset_vector)
        rs.MoveObject(self.two_mark_line[0], self.offset_vector)
        rs.MoveObject(self.two_mark_line[1], self.offset_vector)

        # 平面をもとのxy平面に戻す
        origin_point = (0, 0, 0)
        x_point = (100, 0, 0)
        y_point = (0, 100, 0)
        self.setPlane(origin_point, x_point, y_point)

        # objectを削除
        rs.DeleteObject(line1)

    # ある直線に沿って回転させる
    def rotateTimberBasedOnLine(self, _unused_surface, _unused_line, _unused_polyline, _unused_mark_line,
                                _used_polyline, _used2_section_curve, _select_p, _reference_point):

        unused_line = _unused_line
        unused_surface = _unused_surface
        unused_polyline = _unused_polyline
        unused_mark_line = _unused_mark_line
        used_polyline = _used_polyline
        used2_section_curve = _used2_section_curve
        select_p = _select_p
        reference_point = _reference_point

        # 内積求め回転させる--first--
        para = rs.CurveClosestPoint(used_polyline, select_p)
        base_p1 = rs.EvaluateCurve(used_polyline, para)

        origin_point = (base_p1[0], base_p1[1], base_p1[2])
        x_point = rs.CurveMidPoint(unused_line)
        y_point = reference_point

        vec1 = rs.VectorCreate(x_point, origin_point)
        vec2 = rs.VectorCreate(y_point, origin_point)

        # Planeを定義
        self.setPlane(origin_point, x_point, y_point)

        axis_vector = rs.VectorCrossProduct(vec1, vec2)
        axis_vector_unit = rs.VectorUnitize(axis_vector)
        axis_vector = rs.VectorScale(axis_vector_unit, 100)

        # vec1とvec2の内積を求めそのなす角を求める
        dot = rs.VectorDotProduct(vec1, vec2)  # 内積
        vec1_length = rs.VectorLength(vec1)  # |vec1|
        vec2_length = rs.VectorLength(vec2)  # |vec2|
        cos_theta = dot / (vec1_length * vec2_length)  # cos_theta

        if cos_theta < -1.0:
            pass
            # print("cos_theta < -1.0")

        elif cos_theta > 1.0:
            pass
            # print("cos_theta > 1.0")

        else:
            theta = math.degrees(math.acos(cos_theta))  # 求めたい角度
            rs.RotateObject(unused_surface, origin_point, theta, axis_vector)
            rs.RotateObject(unused_line, origin_point, theta, axis_vector)
            rs.RotateObject(unused_polyline, origin_point, theta, axis_vector)
            rs.RotateObject(unused_mark_line[0], origin_point, theta, axis_vector)
            rs.RotateObject(unused_mark_line[1], origin_point, theta, axis_vector)

        # 内積求め回転させる--second--
        para = rs.CurveClosestPoint(used_polyline, select_p)
        base_p = rs.EvaluateCurve(used_polyline, para)

        # base point
        origin_point = (base_p[0], base_p[1], base_p[2])

        # x point(仮)
        x_point_para = rs.CurveClosestPoint(unused_line, reference_point)
        x_point = rs.EvaluateCurve(unused_line, x_point_para)

        # y point
        y_point_para = rs.CurveClosestPoint(used2_section_curve, x_point)
        y_point = rs.EvaluateCurve(used2_section_curve, y_point_para)
        # rs.AddPoint(y_point)

        # # reference_line = rs.AddLine(x_point, y_point)
        # reference_parama = rs.SurfaceClosestPoint(unused_surface, x_point)
        # reference_closest_point = rs.EvaluateSurface(unused_surface, reference_parama[0], reference_parama[1])
        # reference_point_list = self.getPointsfromSectionCurve(3, reference_parama[0])
        # reference_curve = rs.AddPolyline(reference_point_list)
        #
        # direction = rs.VectorCreate(x_point, reference_closest_point)
        # offset_curve = rs.OffsetCurve(reference_curve, direction, 50)
        # offset_srf = rs.AddPlanarSrf(offset_curve)
        #
        # reference_section_curve = rs.IntersectBreps(offset_srf, self.surface)

        vec1 = rs.VectorCreate(x_point, origin_point)
        vec2 = rs.VectorCreate(y_point, origin_point)

        # Planeを定義
        self.setPlane(origin_point, x_point, y_point)

        axis_vector = rs.VectorCrossProduct(vec1, vec2)
        axis_vector_unit = rs.VectorUnitize(axis_vector)
        axis_vector = rs.VectorScale(axis_vector_unit, 100)

        # vec1とvec2の内積を求めそのなす角を求める
        dot = rs.VectorDotProduct(vec1, vec2)  # 内積
        vec1_length = rs.VectorLength(vec1)  # |vec1|
        vec2_length = rs.VectorLength(vec2)  # |vec2|
        cos_theta = dot / (vec1_length * vec2_length)  # cos_theta

        if cos_theta < -1.0:
            pass
            # print("cos_theta < -1.0")

        elif cos_theta > 1.0:
            pass
            # print("cos_theta > 1.0")

        else:
            theta = math.degrees(math.acos(cos_theta))  # 求めたい角度
            rs.RotateObject(unused_surface, origin_point, theta, axis_vector)
            rs.RotateObject(unused_line, origin_point, theta, axis_vector)
            rs.RotateObject(unused_polyline, origin_point, theta, axis_vector)
            rs.RotateObject(unused_mark_line[0], origin_point, theta, axis_vector)
            rs.RotateObject(unused_mark_line[1], origin_point, theta, axis_vector)

    def rotateTimber(self, rotate_p, angle=90):

        rotate_angle = angle

        rs.RotateObject(self.surface, rotate_p, rotate_angle, self.offset_vector)
        rs.RotateObject(self.center_line, rotate_p, rotate_angle, self.offset_vector)
        rs.RotateObject(self.section_curve, rotate_p, rotate_angle, self.offset_vector)
        rs.RotateObject(self.two_mark_line[0], rotate_p, rotate_angle, self.offset_vector)
        rs.RotateObject(self.two_mark_line[1], rotate_p, rotate_angle, self.offset_vector)

        rs.VectorRotate(self.cross_vector, rotate_angle, self.offset_vector)

        # print("-------------------------------------------------------")
        # print("rotate_angle = %s" % rotate_angle)

        return rotate_angle

    # 接合した数だけcountを増やし、接合可能か判断する
    def countjoint(self, max_num_count):
        self.num_joint += 1

        if self.num_joint >= max_num_count:
            return True
        else:
            return False

    # Planeを変更する
    def setPlane(self, base_point, x, y):
        origin_point = base_point
        x_point = x
        y_point = y
        new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
        rs.ViewCPlane(None, new_plane)

        return new_plane

    # デフォルトのPlaneに変更する
    def setDefaultPlane(self):
        origin_point = (0, 0, 0)
        x_point = (100, 0, 0)
        y_point = (0, 100, 0)
        new_plane = rs.PlaneFromPoints(origin_point, x_point, y_point)
        rs.ViewCPlane(None, new_plane)

        return new_plane

    # ベクトルを生成
    def AddVector(self, base, vec):
        tip = rs.PointAdd(base, vec)
        line = rs.AddLine(base, tip)
        rs.CurveArrows(line, 2)

        return line





