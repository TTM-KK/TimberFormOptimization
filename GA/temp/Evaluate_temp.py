import Rhino
import scriptcontext
import rhinoscriptsyntax as rs


def overlap_num2_for_check(tim_number, instance_pop):
    intersect_num = 0
    for i in range(tim_number):
        tim = instance_pop.timber_list[i].center_line
        tim_end_1 = tim.PointAtEnd
        tim_start_1 = tim.PointAtStart
        tim_line = Rhino.Geometry.Line(tim_end_1, tim_start_1)
        for j in range(tim_number):
            if j == i:
                continue
            else:
                tim_other = instance_pop.timber_list[j].center_line
                tim_end = tim_other.PointAtEnd
                tim_start = tim_other.PointAtStart
                tim_other_line = Rhino.Geometry.Line(tim_end, tim_start)

                distance = tim_line.MinimumDistanceTo(tim_other_line)

                if distance < instance_pop.timber_list[i].section_length/2 + instance_pop.timber_list[j].\
                        section_length/2 + 50:
                    intersect_num = intersect_num + 1
                else:
                    # intersect_num = intersect_num + 1
                    continue
    return intersect_num


def overlap_length(tim_number, instance_pop):
    '''
    :param tim_number: 1つの個体に使用する木材の本数
    :param instance_pop: Generate クラスインスタンス
    :return: surface同士のintersection部のcurveの長さの合計値。
    '''
    cur_length = 0
    for i in range(tim_number):
        tim1_srf = instance_pop.used_list[i].surface
        for j in range(tim_number):
            if i != j:
                tim2_srf = instance_pop.used_list[j].surface
                flag = rs.IntersectBreps(tim1_srf, tim2_srf)
                if flag is None:
                    continue
                else:
                    for k in range(len(flag)):
                        cur_length = cur_length + rs.CurveLength(flag[k])

    return cur_length


def overlap_num_rhinocommon(tim_number, instance_pop):  # Evaluate the Intersection number -----> type is int
    '''
    intersection を使用しているため非常に遅く使えない。
    :param tim_number:
    :param instance_pop:
    :return:
    '''
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance

    intersect_num = 0
    for i in range(tim_number):
        # tim = rhutil.coercebrep(instance_pop.used_list[i].surface)
        tim = instance_pop.used_list[i].surface

        for j in range(tim_number):

            if j == i:
                continue
            else:
                # tim_other = rhutil.coercebrep(instance_pop.used_list[j].surface)
                tim_other = instance_pop.used_list[j].surface

                rc = Rhino.Geometry.Intersect.Intersection.BrepBrep(tim, tim_other, tolerance)

                if rc is None:
                    continue

                else:

                    out_curves = rc[1]
                    merged_curves = Rhino.Geometry.Curve.JoinCurves(out_curves, 2.1 * tolerance)

                    list_length = len(merged_curves)
                    # print("list_length", list_length)
                    # print(merged_curves)
                    # input("dd")
                    for k in range(list_length):
                        intersect_num = intersect_num + 1

    return intersect_num


def overlap_num(tim_number, instance_pop):  # Evaluate the Intersection number -----> type is int

    intersect_num = 0
    for i in range(tim_number):
        tim = instance_pop.used_list[i].surface
        for j in range(tim_number):

            if j == i:
                continue
            else:
                tim_other = instance_pop.used_list[j].surface
                flag = rs.IntersectBreps(tim, tim_other)
                if flag is None:
                    continue

                if rs.IsCurve(flag[0]):
                    intersect_num = intersect_num + 1

                    for k in range(len(flag)):
                        rs.DeleteObject(flag[k])

    return intersect_num
