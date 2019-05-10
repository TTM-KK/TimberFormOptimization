# coding: utf-8

import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import time


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


def transform_object_rhinocommon(object, vec_move):
    xf = Rhino.Geometry.Transform.Translation(vec_move)
    object.Transform(xf)
    

segment_num = 20


tim_srf_1 = rs.GetObject('select the surface tim1', rs.filter.surface)
tim_srf_2 = rs.GetObject('select the surface tim2', rs.filter.surface)
tim_axis_1 = rs.GetObject('select the axis tim1', rs.filter.curve)
tim_axis_2 = rs.GetObject('select the axis tim2', rs.filter.curve)

tim_srf_1 = rs.coercebrep(tim_srf_1)
tim_srf_2 = rs.coercebrep(tim_srf_2)
tim_axis_1 = rs.coercecurve(tim_axis_1)
tim_axis_2 = rs.coercecurve(tim_axis_2)

time_start = time.time()

# 精度を求めるならばVが2,7のときの直径を求め、その値もリストに格納しておく。
tim1_segment_points, tim1_diameter = calculate_srf_segment_points(tim_srf_1, segment_num)
tim2_segment_points, tim2_diameter = calculate_srf_segment_points(tim_srf_2, segment_num)


tim1_index, tim2_index = calculate_connect_part_indices(tim1_segment_points, tim2_segment_points, segment_num)


tim1_min_p = tim1_segment_points[tim1_index]
tim2_min_p = tim2_segment_points[tim2_index]

vec_move = tim1_min_p - tim2_min_p
print(vec_move.Length)

transform_object_rhinocommon(tim_srf_2, vec_move)
transform_object_rhinocommon(tim_axis_2, vec_move)


vec_move.Unitize()
vec_move.Reverse()
vec_move = vec_move * ((tim1_diameter[tim1_index] / 2) + ((tim2_diameter[tim2_index] / 2) / 2))

transform_object_rhinocommon(tim_srf_2, vec_move)
transform_object_rhinocommon(tim_axis_2, vec_move)


time_end = time.time()

print("Processing Time : {}".format(time_end - time_start))

scriptcontext.doc.Objects.AddBrep(tim_srf_2)
scriptcontext.doc.Objects.AddCurve(tim_axis_2)
scriptcontext.doc.Objects.AddLine(tim1_min_p, tim2_min_p)
