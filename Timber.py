# -*- coding:utf-8 -*-

import random as rnd
from forTimber import RhinoCommonOriginalMethods as rsOri


class Timber:

    # 初期化
    def __init__(self, center_line, surface, id):
        self.id = id  # timberのID
        self.num_joint = 0  # 接合数
        self.two_mark_line = None  # ロボットアームを使用する際に目印になる2本のライン
        self.center_line = center_line  # 中心線
        self.timber_length = None  # 中心線の長さ
        self.surface = surface  # timberサーフェス
        self.section_curve = None  # 仮想断面線
        self.select_domain_list = []  # 接合する際にどの分割サーフェスエリアで接合したかを格納するリスト
        self.drill_line_list = []  # 接合部のドリルラインを格納するリスト
        self.center_line_parameter_list = []  # 中心線のパラメータ値を格納するリスト(分割点)
        self.section_length = None  # timberの断面直径の推定値を格納する。

        self.partner_tim = []  # ttm add 1011
        self.temp_partner_tim = []  # ttm add
        self.tim_distance = None  # ttm add 部材間の最小値を計算しリストに格納している。

    def measure_length(self):
        # curve_domain = self.center_line.Domain
        # length_timber = (self.center_line.AtPoint(curve_domain[0]) - self.center_line.AtPoint(curve_domain[1])).Length
        length_timber = self.center_line.GetLength()
        self.timber_length = length_timber
        # print("length_timber", length_timber)
        # return length_timber

    # 断面の直径を取得する. RhinoCommonメソッド。
    def measure_section_length(self):
        rc, t = self.center_line.NormalizedLengthParameter(0.5)
        base_p = self.center_line.PointAt(t)
        length, list_p = rsOri.GetTimberSectionLength_RhinoCommon(self.surface, base_p)
        self.section_length = length

    # tim_distanceのリスト初期設定
    def init_tim_distance(self, tim_number):
        self.tim_distance = []
        for i in range(tim_number):
            self.tim_distance.append([])

    def select_surface_domain(self):
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
