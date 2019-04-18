# -*- coding:utf-8 -*-

import rhinoscriptsyntax as rs


def scanObjectSort(num_timber, get_center_line, get_surface):
    # オブジェクトの順番を整理したリスト
    center_line_list = []  # 整理した順番に中心線を格納するリスト
    surface_list = []  # 整理した順番に曲面サーフェスを格納するリスト
    mark_line_list = []  # 整理した順番にmark lineを格納するリスト

    # 全部材の中心線のスタートポイントの座標値を調べ、リストに格納する --> 中心線について
    end_point_list = []

    for i in range(0, num_timber):
        start_end_point = rs.CurveStartPoint(get_center_line[i])  # 中心線のスタートポイントを取得する
        end_point_list.append(start_end_point[0])  # x座標値のみをリストに格納していく

    # スタートポイントの座標値が小さい順に新しいリストに格納していく
    for _ in range(0, num_timber):
        select_index = end_point_list.index(min(end_point_list))
        select_timber_center_line = get_center_line[select_index]

        # 選択した材の中心線を新しいリストに格納する
        center_line_list.append(select_timber_center_line)

        # 選択した材はリストから除外する
        get_center_line.pop(select_index)
        end_point_list.pop(select_index)

    # 全部材の曲面サーフェスのある一点を取得し、リストに格納していく --> サーフェスについて
    point_on_surface_list = []

    for i in range(0, num_timber):
        domainU = rs.SurfaceDomain(get_surface[i], 0)
        domainV = rs.SurfaceDomain(get_surface[i], 1)
        u = domainU[1] / 2.0
        v = domainV[1] / 2.0
        point = rs.EvaluateSurface(get_surface[i], u, v)

        # あるサーフェス上のある一点のx座標値を格納する
        point_on_surface_list.append(point[0])

    # あるサーフェス上のある一点を格納したリストの座標値が小さい順に新しいリストに格納していく
    for _ in range(0, num_timber):
        select_index = point_on_surface_list.index(min(point_on_surface_list))
        select_timber_surface = get_surface[select_index]

        # 選択した材のサーフェスを新しいリストに格納する
        surface_list.append(select_timber_surface)

        # 選択した材のサーフェス情報はリストから削除する
        get_surface.pop(select_index)
        point_on_surface_list.pop(select_index)

    # 全部材のmark lineを取得し、シルトにか格納していく --> mark lineについて
    # point_on_mark_line = []
    #
    # for i in range(0, len(get_mark_line)):
    #     mid_point = rs.CurveMidPoint(get_mark_line[i])
    #     point_on_mark_line.append(mid_point[0])
    #
    # # スタートポイントの座標値が小さい順に新しいリストに格納していく
    # for _ in range(0, num_timber):
    #     select_index1 = point_on_mark_line.index(min(point_on_mark_line))
    #     select_timber_mark_line1 = get_mark_line[select_index1]
    #
    #     # 選択した材はリストから除外する
    #     point_on_mark_line.pop(select_index1)
    #     get_mark_line.pop(select_index1)
    #
    #     select_index2 = point_on_mark_line.index(min(point_on_mark_line))
    #     select_timber_mark_line2 = get_mark_line[select_index2]
    #
    #     # 選択した材はリストから除外する
    #     point_on_mark_line.pop(select_index2)
    #     get_mark_line.pop(select_index2)
    #
    #     # 選択した材の中心線を新しいリストに格納する
    #     two_mark_line = [select_timber_mark_line1, select_timber_mark_line2]
    #
    #     mark_line_list.append(two_mark_line)

    return [center_line_list, surface_list]