# -*- coding:UTF-8 -*-
import rhinoscriptsyntax as rs
import time
import Rhino
import scriptcontext
import rhinoscript.utility as rhutil
import math


#-----------------------------------------------------------------------------------------------------------------------
def AddVectorArrow(base, vector):
    vec_normal = rs.VectorUnitize(vector)
    vec_scale = rs.VectorScale(vec_normal, 200)
    p = rs.PointAdd(base, vec_scale)
    line = rs.AddLine(base, p)
    rs.CurveArrows(line, 2)

    return p

def SetPlaneOrigin():
    plane_origin = rs.PlaneFromPoints((0, 0, 0), (100, 0, 0), (0, 100, 0))
    rs.ViewCPlane(None, plane_origin)


def GetTimberSectionLenght(tim_srf, base_point):
    closest_pra = rs.SurfaceClosestPoint(tim_srf.Faces[0], base_point)
    V = rs.SurfaceDomain(tim_srf.Faces[0], 1)

    if V[0] < 0:
        divide_V = abs(V[0] / 10)
    else:
        divide_V = abs(V[1] / 10)

    list_point = []
    for i in range(10):
        point = rs.EvaluateSurface(tim_srf.Faces[0], closest_pra[0], V[0] + divide_V * i)
        list_point.append(point)

    length = rs.Distance(list_point[0], list_point[5])

    return length

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

    return length , list_point[0]


def VectorAngle_RhinoCommon(vector1, vector2):
    """
    RhinoCommon method
    :param vector1:  3D vector
    :param vector2:  3D vector
    :return: 2つのベクトルの角度
    """
    vector1 = Rhino.Geometry.Vector3d(vector1.X, vector1.Y, vector1.Z)
    vector2 = Rhino.Geometry.Vector3d(vector2.X, vector2.Y, vector2.Z)
    if not vector1.Unitize() or not vector2.Unitize():
        raise ValueError("unable to unitize vector")
    dot = vector1 * vector2
    dot = rhutil.clamp(-1,1,dot)
    radians = math.acos(dot)
    # return math.degrees(radians)
    return radians
#-----------------------------------------------------------------------------------------------------------------------

def addVector(end_point, start_point):
    vec = end_point - start_point

    return vec

