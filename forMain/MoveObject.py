import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import rhinoscript.utility as rhutil
import copy

def MoveTimberObjects(timber_1, timber_2, vector_move):
    xf = Rhino.Geometry.Transform.Translation(vector_move)

    timber_1.center_line.Transform(xf)
    timber_1.surface.Transform(xf)

    timber_2.center_line.Transform(xf)
    timber_2.surface.Transform(xf)

    # rs.MoveObject(timber_1.center_line, vector_move)
    # rs.MoveObject(timber_1.surface, vector_move)
    # # rs.MoveObject(timber_1.two_mark_line[0], vector_move)
    # # rs.MoveObject(timber_1.two_mark_line[1], vector_move)
    # # rs.MoveObject(timber_1.drill_line_list, vector_move)
    #
    # rs.MoveObject(timber_2.center_line, vector_move)
    # rs.MoveObject(timber_2.surface, vector_move)
    # # rs.MoveObject(timber_2.two_mark_line[0], vector_move)
    # # rs.MoveObject(timber_2.two_mark_line[1], vector_move)
    # # rs.MoveObject(timber_2.drill_line_list, vector_move)
    # rhutil.coercecurve(timber_1.center_line)
    # rhutil.coercecurve(timber_2.center_line)
    # rhutil.coercebrep(timber_1.surface)
    # rhutil.coercebrep(timber_2.surface)

def CopyTimberObjects(timber_instance, list_srf_temp, list_center_line_temp):
    # center_line = rs.CopyObject(timber_instance.center_line)
    # srf = rs.CopyObject(timber_instance.surface)
    center_line = copy.deepcopy(timber_instance.center_line)
    srf = copy.deepcopy(timber_instance.surface)
    # mark_line1 = rs.CopyObject(timber_instance.two_mark_line[0])
    # mark_line2 = rs.CopyObject(timber_instance.two_mark_line[1])
    # rs.CopyObject(timber_1.drill_line_list, vector_move)
    list_srf_temp.append(srf)
    list_center_line_temp.append(center_line)
    # list_two_mark_line_temp.append([mark_line1, mark_line2])

def SingleTimberMoveObjects(timber_instance, vector_move, generation_num, loop_num, between_draw_num):
    # rs.MoveObject(timber_instance.center_line, vector_move)
    # rs.MoveObject(timber_instance.surface, vector_move)

    xf = Rhino.Geometry.Transform.Translation(vector_move)
    # print("timber_instance", timber_instance.center_line)
    # print("timber_instance", timber_instance.surface)
    if type(timber_instance.center_line) is list:
        timber_instance.center_line = timber_instance.center_line[0]
        timber_instance.center_line.Transform(xf)
    else:
        timber_instance.center_line.Transform(xf)

    if type(timber_instance.surface) is list:
        timber_instance.surface = timber_instance.surface[0]
        timber_instance.surface.Transform(xf)
    else:
        timber_instance.surface.Transform(xf)


    if generation_num - 1 == loop_num:
        scriptcontext.doc.Objects.AddBrep(timber_instance.surface)
        scriptcontext.doc.Objects.AddCurve(timber_instance.center_line)

    # if generation_num - 1 != loop_num and loop_num % between_draw_num:
    #     scriptcontext.doc.Objects.AddBrep(timber_instance.surface)
    #     scriptcontext.doc.Objects.AddCurve(timber_instance.center_line)
    # rs.MoveObject(timber_instance.two_mark_line[0], vector_move)
    # rs.MoveObject(timber_instance.two_mark_line[1], vector_move)
    # rs.MoveObject(timber_1.drill_line_list, vector_move)