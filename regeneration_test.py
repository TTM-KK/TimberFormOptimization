import rhinoscriptsyntax as rs
import Rhino
import scriptcontext


segment_num = 10
segment_index = 5


tim_srf_1 = rs.GetObject('select the surface tim1', rs.filter.surface)
tim_srf_2 = rs.GetObject('select the surface tim2', rs.filter.surface)

tim_axis_1 = rs.GetObject('select the axis tim1', rs.filter.curve)
tim_axis_2 = rs.GetObject('select the axis tim2', rs.filter.curve)

tim_srf_1 = rs.coercesurface(tim_srf_1)
tim_srf_2 = rs.coercesurface(tim_srf_2)

tim_axis_1 = rs.coercecurve(tim_axis_1)
tim_axis_2 = rs.coercecurve(tim_axis_2)

axis_domain_1 = tim_axis_1.Domain
axis_domain_2 = tim_axis_2.Domain

domain_segment_length_1 = (axis_domain_1[1] - axis_domain_1[0]) / segment_num
domain_segment_length_2 = (axis_domain_2[1] - axis_domain_2[0]) / segment_num

srf_domainU_1 = tim_srf_1.Domain(0)
srf_domainU_2 = tim_srf_2.Domain(0)
srf_domainV_1 = tim_srf_1.Domain(1)
srf_domainV_2 = tim_srf_2.Domain(1)

srf_domainU_segment_1 = (srf_domainU_1[1] - srf_domainU_1[0]) / segment_num
srf_domainU_segment_2 = (srf_domainU_2[1] - srf_domainU_2[0]) / segment_num

srf_domainV_segment_1 = (srf_domainV_1[1] - srf_domainV_1[0]) / segment_num
srf_domainV_segment_2 = (srf_domainV_2[1] - srf_domainV_2[0]) / segment_num

tim_segment_diameter_1 = []
tim_segment_diameter_2 = []
# 精度を求めるならばVが2,7のときの直径を求め、その値もリストに格納しておく。
for i in range(segment_num):
    p1_U = srf_domainU_1[0] + (srf_domainU_segment_1 * i)
    p1_V = srf_domainV_1[0] + (srf_domainV_segment_1 * 0)

    p2_U = srf_domainU_1[0] + (srf_domainU_segment_1 * i)
    p2_V = srf_domainV_1[0] + (srf_domainV_segment_1 * 5)

    srf_point1 = tim_srf_1.PointAt(p1_U, p1_V)
    srf_point2 = tim_srf_1.PointAt(p2_U, p2_V)

    diameter_vec = srf_point2 - srf_point1
    diameter_length = diameter_vec.Length

    # scriptcontext.doc.Objects.AddLine(srf_point2, srf_point1)

    tim_segment_diameter_1.append(diameter_length)

print(tim_segment_diameter_1)
#
# crv_point1 = tim_axis_1.PointAt(domain_segment_length_1 * segment_index)
# crv_point2 = tim_axis_1.PointAt(domain_segment_length_1 * (segment_index + 1))
#
# scriptcontext.doc.Objects.AddPoint(crv_point1)
# scriptcontext.doc.Objects.AddPoint(crv_point2)
# scriptcontext.doc.Objects.AddPoint(srf_point1)
# scriptcontext.doc.Objects.AddPoint(srf_point2)
