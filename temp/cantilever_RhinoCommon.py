# -*- coding:utf-8 -*-
import rhinoscriptsyntax as rs
import random as rnd
import math  # ttm add 181003
import time
import Rhino
import scriptcontext
import rhinoscript.utility as rhutil


def GetTimberSectionLength_RhinoCommon(tim_srf, base_point):
    """
    :param tim_srf: surface of timber , you want to measure the length
    :param base_point:  base point that Adding Timber having
    :return: section diameter length
    """
    rc, u, v = tim_srf.Faces[0].ClosestPoint(base_point)
    V = tim_srf.Faces[0].Domain(1).T0 , tim_srf.Faces[0].Domain(1).T1

    if V[0] < 0:
        divide_V = abs(V[0] / 10)
    else:
        divide_V = abs(V[1] / 10)

    list_point = []
    for i in range(10):
        point = tim_srf.Faces[0].PointAt(u, V[0] + divide_V * i)
        list_point.append(point)

    length = (list_point[0] - list_point[5]).Length

    return length, list_point[0]



divide_domain_num = 10


# 各オブジェクトの取得　--->  Timber Instanceに置き換える
tim1_srf = rhutil.coercebrep(rs.GetObject("select first srf", rs.filter.surface))
tim2_srf = rhutil.coercebrep(rs.GetObject("select second srf", rs.filter.surface))


tim1_center_crv = rhutil.coercecurve(rs.GetObject("select first center_crv", rs.filter.curve))
tim2_center_crv = rhutil.coercecurve(rs.GetObject("select second center_crv", rs.filter.curve))


# cantileverのRun timeを計測する
start_time = time.time()


domain_crv1 = tim1_center_crv.Domain
domain_crv2 = tim2_center_crv.Domain

each_domain_length1 = (domain_crv1[1] - domain_crv1[0]) / divide_domain_num
each_domain_length2 = (domain_crv2[1] - domain_crv2[0]) / divide_domain_num

select_domain1 = 2
select_domain2 = rnd.randint(0, 9)

tim1_point = tim1_center_crv.PointAt(select_domain1 * each_domain_length1)
tim2_point = tim2_center_crv.PointAt(select_domain2 * each_domain_length2)

vec_move = tim1_point - tim2_point

xf = Rhino.Geometry.Transform.Translation(vec_move)
tim2_center_crv.Transform(xf)
tim2_srf.Transform(xf)

tim1_start_point = tim1_center_crv.PointAt(domain_crv1[0])
tim1_end_point = tim1_center_crv.PointAt(domain_crv1[1])

p1 = Rhino.Geometry.Point3d(0,0,0)
p2 = Rhino.Geometry.Point3d(0,0,10)
p3 = Rhino.Geometry.Point3d(10,0,0)

plane1 = Rhino.Geometry.Plane(p1, p2, p3)
rotate_angle = math.radians(rnd.randint(0,360))
xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane1[3], tim1_point)
tim2_center_crv.Transform(xf)
tim2_srf.Transform(xf)
print("rotate angle", math.degrees(rotate_angle))


p1 = Rhino.Geometry.Point3d(0,0,0)
p2 = Rhino.Geometry.Point3d(0,10,0)
p3 = Rhino.Geometry.Point3d(10,0,0)

plane2 = Rhino.Geometry.Plane(p1,p2,p3)
rotate_angle = math.radians(rnd.randint(0,360))
xf = Rhino.Geometry.Transform.Rotation(rotate_angle, plane2[3], tim1_point)
tim2_center_crv.Transform(xf)
tim2_srf.Transform(xf)

length1, rc1 = GetTimberSectionLength_RhinoCommon(tim1_srf, tim1_point)
length2, rc2 = GetTimberSectionLength_RhinoCommon(tim2_srf, tim2_point)

print("rc1", rc1)
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
    vec_move = rc * ((length1 / 2)+(length2 / 3))
    xf = Rhino.Geometry.Transform.Translation(vec_move)
    tim2_srf.Transform(xf)
    tim2_center_crv.Transform(xf)


scriptcontext.doc.Objects.AddBrep(tim2_srf)
scriptcontext.doc.Objects.AddCurve(tim2_center_crv)
scriptcontext.doc.Views.Redraw()

end_time = time.time()
print("Processing Time : %s"%(end_time - start_time))

#
#
# # print("tim1 name", self.used_list[tim_preexist_num].name)
# # print("tim2 name", self.used_list[tim_add_num].name)
#
# for loop in range(100):
#
#     # 使用するtimberを選ぶ(初期生成)
#     if len(self.used_list) == 0:
#         # 使用していないtimberから任意に2本選ぶ(x, yはリストのインデックス)
#         x = 0
#         y = 1
#         used_timber = self.timber_list[x]
#         unused_timber = self.timber_list[y]
#
#         # console
#         # print("#######################################################")
#         # print("unused: %s | %s cantilever" % (used_timber.name, unused_timber.name))
#
#     # 使用するtimberを選ぶ(複数生成)
#     else:
#         if init_generate:
#             # 使用済みのtimberから任意に1本選ぶ --> used_list
#             x = rnd.randint(0, len(self.init_used_list) - 1)
#             used_timber = self.init_used_list[x]
#
#             # 使用していないtimberから任意に1本選ぶ --> timber_list
#             y = rnd.randint(0, len(self.timber_list) - 1)
#             unused_timber = self.timber_list[y]
#
#             # console
#             # print("#######################################################")
#             # print("used: %s | unused: %s cantilever" % (used_timber.name, unused_timber.name))
#
#         else:
#
#             used_timber = self.used_list[tim_preexist_num]
#
#             unused_timber = self.used_list[tim_add_num]
#
#             # console
#             # print("#######################################################")
#             # print("used: %s | unused: %s cantilever" % (used_timber.name, unused_timber.name))
#
#     # print("loop %s" % loop)
#
#     # 再生成に使用する材のselect_domain_listを初期化する
#     # print("START used_tim domain_list in cantilever", used_timber.select_domain_list)
#     unused_timber.select_domain_list = []
#     # print("START unused_timber domain_list in cantilever", unused_timber.select_domain_list)
#
#     # サーフェスのドメインを選択する
#     select_domain1 = used_timber.selectSurfaceDomain_1()
#     select_domain2 = unused_timber.selectSurfaceDomain_1()
#
#     # サーフェスから選択したドメイン内のある一点のuパラメータを取得する
#     select1_u = used_timber.getSurfaceUparameter(select_domain1)
#     select2_u = unused_timber.getSurfaceUparameter(select_domain2)
#
#     # サーフェス上の任意の点を取得する
#     p1 = used_timber.getRandomSurfacePoint(select1_u)
#     p2 = unused_timber.getRandomSurfacePoint(select2_u)
#
#     # 仮想断面(任意の点(p1, p2)が乗っている)を構成する点情報を取得する TODO splitで断面取得 --> 修正済み
#     point_list1 = used_timber.getPointsfromSectionCurve(3, used_timber.select_u)
#     point_list2 = unused_timber.getPointsfromSectionCurve(3, unused_timber.select_u)
#
#     # closest pointを生成する
#     used_timber.createVectorClosestPointToCurve(p1)
#     unused_timber.createVectorClosestPointToCurve(p2)
#
#     # 任意の仮想断面からの垂直ベクトルを生成し、仮想断面と中心線の交点を戻り値として返す
#     base_point1 = used_timber.createCrossVectorOnSectionCurve(point_list1)
#     base_point2 = unused_timber.createCrossVectorOnSectionCurve(
#         point_list2)  # Message: Could not convert None to a Vector3d
#
#     # timberを移動させる(base_point1 to base_point2)
#     unused_timber.moveTimber(base_point1, base_point2)
#
#     # timberをオフセットする
#     unused_timber.offsetTimber(used_timber.cross_vector, base_point1, p1, used_timber.section_curve)
#
#     # timberを任意の角度回転させる
#     unused_timber.rotateTimber(base_point1, rnd.randint(60, 120))
#
#
#     # unused_timber.temp_partner_tim.append(used_timber.name)  # 一旦このリストに接合関係を保存。
#     # used_timber.temp_partner_tim.append(unused_timber.name)
#
#     break
#
#     # 接点に近似させるために最適化を行い、交線を戻り値として返す
#
# #     curve_drill = opt.optimization(used_timber.closest_point, used_timber.point, used_timber.surface,
# #                                    unused_timber.surface, unused_timber.center_line,
# #                                    unused_timber.section_curve,
# #                                    unused_timber.two_mark_line, opt_tolerance)
# #
# #     re_loop_flag = False
# #
# #     # print("-------------------------------------------------------")
# #     for j in range(10):
# #         # もしこの時点でいずれかのtimberに接触している時の処理
# #         collision = detection.collisionDetectionTolerance(self.used_list, self.not_use_list, unused_timber, x,
# #                                                           dete_tolerance)
# #
# #         if collision:
# #             # print("There is Collision")
# #
# #             # 衝突してしまった場合の処理を書く TODO アルゴリズム作成 --> 少しずつ動かすなどの方法検討
# #             #########################################################################################
# #             unused_timber.rotateTimber(base_point1, j + 2)
# #             #
# #             #
# #             #########################################################################################
# #
# #             if j == 9:
# #                 re_loop_flag = True
# #                 rs.DeleteObject(used_timber.section_curve)
# #                 rs.DeleteObject(unused_timber.section_curve)
# #                 for k in range(len(curve_drill)):
# #                     rs.DeleteObject(curve_drill[k])
# #
# #                 break
# #
# #
# #         else:
# #             # print("There is not collision")
# #             break
# #
# #     if re_loop_flag is True:
# #         continue
# #     else:
# #         break
# #
# # # # 接点に近似させるために最適化を行い、交線を戻り値として返す
# # #
# # # curve_drill = opt.optimization(used_timber.closest_point, used_timber.point, used_timber.surface,
# # #                                unused_timber.surface, unused_timber.center_line, unused_timber.section_curve,
# # #                                unused_timber.two_mark_line, tolerance)
# #
# # # ドリル穴をあけるための線データを生成する
# # drill_line_info = drill.drilling(curve_drill, unused_timber.surface,
# #                                  used_timber.center_line, unused_timber.center_line,
# #                                  used_timber.closest_point)
# #
# # # ドリルラインをTimberのメンバー変数のリストに格納する
# # copy_drill_line = rs.CopyObject(drill_line_info[0], None)
# # used_timber.drill_line_list.append(drill_line_info[0])
# # unused_timber.drill_line_list.append(copy_drill_line)
#
# # objectを削除する
# for i in range(len(used_timber.section_curve)):
#     rs.DeleteObject(used_timber.section_curve[i])
#
# for i in range(len(unused_timber.section_curve)):
#     rs.DeleteObject(unused_timber.section_curve[i])
#
# # # 指定したドメインをTimberのメンバー変数リストに格納する
# used_timber.select_domain_list.append([select_domain1, unused_timber.name])  # ttm change 190128
# unused_timber.select_domain_list.append([select_domain2, used_timber.name])
#
# # print("END used_tim domain_list in cantilever", used_timber.select_domain_list)
# # print("END unused_timber domain_list in cantilever", unused_timber.select_domain_list)
#
# # 追加した材と既に生成されている材との距離を取得してくる。
# for i in range(len(self.used_list)):  # ttm add 190113
#     already_exist_timber_name = self.used_list[i].name
#     already_exist_timber = self.used_list[i]
#     if already_exist_timber_name in already_regenerated_list:
#         timber.distanceBetweenTimber(already_exist_timber, unused_timber)
#
# end_time = time.time()
#
# cantilever_run_time = end_time - start_time
# print("-------------------------------------------------------")
# print("cantilever Run time: %s" % cantilever_run_time)
#
# return True
# # used_timber.partner_tim.append(unused_timber.name)  # add the partner timber name ---> name is number
# # unused_timber.partner_tim.append(used_timber.name)
#
# # 接合数を更新する
# # 初期生成
# # if len(self.used_list) == 0:
# #
# #     used_timber.countjoint(num_count)
# #     unused_timber.countjoint(num_count)
# #
# #     # どの部材と接合したかをリストに格納する
# #     used_timber.joint_name_list.append(unused_timber.name)
# #     unused_timber.joint_name_list.append(used_timber.name)
# #
# #     # 一度使ったtimberはused_listに格納する
# #     if used_timber.num_joint > 0:
# #         # 使用済みのtimberをused_listに格納する
# #         self.used_list.append(used_timber)
# #
# #     if unused_timber.num_joint > 0:
# #         # 使用済みのtimberをused_listに格納する
# #         self.used_list.append(unused_timber)
# #
# #     # 使用したtimberはtimber_listクラスから除外する
# #     if used_timber.num_joint > 0:
# #         self.timber_list.pop(x)
# #
# #     if unused_timber.num_joint > 0:
# #         self.timber_list.pop(y - 1)
# #
# #     # 片持ち生成に成功した場合
# #     self.count_cantilever = self.count_cantilever + 1
# #
# #     # cantileverのRun timeを計測する
# #     end_time = time.time()
# #
# #     cantilever_run_time = end_time - start_time
# #     # print("-------------------------------------------------------")
# #     # print("cantilever Run time: %s" % cantilever_run_time)
# #
# # # 複数生成
# # else:
# #     count1 = used_timber.countjoint(num_count)  # used_timberの現状の接合数
# #
# #     unused_timber.countjoint(num_count)
# #     count2 = unused_timber.num_joint  # unused_timberの現状の接合数
# #
# #     # どの部材と接合したかをリストに格納する
# #     used_timber.joint_name_list.append(unused_timber.name)
# #     unused_timber.joint_name_list.append(used_timber.name)
# #
# #     # 部材が指定の接合数を満たした場合
# #     if count1:
# #         # もう使用しないnot_use_listに格納する
# #         self.not_use_list.append(used_timber)
# #
# #         # 使用したtimberはused_listから除外する
# #         self.used_list.pop(x)
# #
# #     # 一度使ったtimberはused_listに格納する
# #     if count2 > 0:
# #         # 使用済みのtimberをused_listに格納する
# #         self.used_list.append(unused_timber)
# #
# #         # 使用したtimberはtimber_listクラスから除外する
# #         self.timber_list.pop(y)
# #
# #     # init generate
# #     if init_generate:
# #         self.used_list.append(used_timber)
# #         self.init_used_list.pop(x)
# #
# #     # 片持ち生成に成功した場合
# #     self.count_cantilever = self.count_cantilever + 1
# #
#     # cantileverのRun timeを計測する
#     # end_time = time.time()
#     #
#     # cantilever_run_time = end_time - start_time
#     # print("-------------------------------------------------------")
#     # print("cantilever Run time: %s" % cantilever_run_time)
# #