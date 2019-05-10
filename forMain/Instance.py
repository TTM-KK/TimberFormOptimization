# coding: utf-8
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import rhinoscript.utility as rhutil


def axis_instance(pop_num, center_line):  # ver RhinoCommon
    temp_center_line = []
    dic1 = {}
    for foo in range(pop_num):
        dic1['centerLine' + str(foo)] = foo

    for i in range(pop_num):
        dic1['centerLine' + str(i)] = []
        for j in range(len(center_line)):
            # ce = rs.CopyObject(center_line[j])
            ce = rhutil.coercecurve(center_line[j])
            dic1['centerLine' + str(i)].append(ce)
        temp_center_line.append(dic1['centerLine' + str(i)])

    return temp_center_line

def surface_instance(pop_num, all_surface):  # ver RhinoCommon
    temp_surface = []
    dic2 = {}
    for foo in range(pop_num):
        dic2['allSurface' + str(foo)] = foo

    for i in range(pop_num):
        dic2['allSurface' + str(i)] = []
        for j in range(len(all_surface)):
            # srf = rs.CopyObject(all_surface[j])
            srf = rhutil.coercebrep(all_surface[j])
            dic2['allSurface' + str(i)].append(srf)
        temp_surface.append(dic2['allSurface' + str(i)])

    return temp_surface


def mark_instance(pop_num, all_mark):
    temp_mark = []
    dic3 = {}
    for foo in range(pop_num):
        dic3['allMark' + str(foo)] = foo

    for i in range(pop_num):
        dic3['allMark' + str(i)] = []
        for j in range(len(all_mark)):
            mark_1 = rs.CopyObject(all_mark[j][0])
            mark_2 = rs.CopyObject(all_mark[j][1])
            mark = [mark_1, mark_2]
            dic3['allMark' + str(i)].append(mark)
        temp_mark.append(dic3['allMark' + str(i)])

    return temp_mark
