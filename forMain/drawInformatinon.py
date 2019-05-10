# coding: utf-8
import rhinoscriptsyntax as rs
import scriptcontext

def drawEvaluateValue(list_evaluate):
    frame = 5000
    original_point = 5000
    step_x_axis = 100

    plane = rs.WorldXYPlane()
    xform = rs.XformTranslation([0, 5000, 0])
    plane1 = rs.PlaneTransform(plane, xform)
    rs.AddRectangle(plane1, frame, frame)

    evaluate_sum = []
    for i in range(len(list_evaluate)):
        evaluate_sum.append(sum(list_evaluate[i]))

    max_value = max(evaluate_sum)
    min_value = min(evaluate_sum)

    # if 1000 > max_value > 100:
    #
    # if 10000 > max_value >= 1000:

    point_list = []
    for i in range(len(evaluate_sum)):
        value = evaluate_sum[i]
        # print("evaluate_sum", evaluate_sum[i])
        new_value = remap(value, max_value, 0, 5000, 0)
        # print("new_value", new_value)
        pt = rs.AddPoint(i*step_x_axis, original_point + new_value, 0)
        point_list.append(pt)

    rs.AddPolyline(point_list)


def remap(value, old_max, old_min, new_max, new_min):
    new_value = ((new_max - new_min) / (old_max - old_min)) * (value)
    return new_value


def draw_rhino_object(pop_num, num_timber, dic):
    '''
    Rhinoにオブジェクトを描画する
    :param pop_num:
    :param num_timber:
    :param dic:
    :return:
    '''
    for i in range(pop_num):
        for j in range(num_timber):
            sf = scriptcontext.doc.Objects.AddBrep(dic['generate' + str(i)].used_list[j].surface)
            cr = scriptcontext.doc.Objects.AddCurve(dic['generate' + str(i)].used_list[j].center_line)
