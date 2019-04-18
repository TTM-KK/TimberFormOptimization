# -*- coding:utf-8 -*-

import Rhino
import rhinoscriptsyntax as rs
import rhinoscript.utility as rhutil
import scriptcontext

# select the object
person = rs.GetObject("select the Person model")
surface = rs.GetObject("Select the Plan")

mesh_check = False
surface_check = False

# convert the System.Guid to Rhino.Geometry
try:
    mesh = rhutil.coercebrep(person, True)
except:
    mesh = rhutil.coercemesh(person, True)
    print("This object is Mesh")
    mesh_check = True
else:
    print("This object is Surface")
    surface_check = True

srf = rhutil.coercesurface(surface, True)

if mesh_check:
    # convert the mesh object to surface object
    pieces = mesh.SplitDisjointPieces()
    breps = [Rhino.Geometry.Brep.CreateFromMesh(piece, True) for piece in pieces]

    # move the object and the try Intersection
    move_distance = 10000  # 10m離れていたら機能しないので注意。本当はWhileで行いたいが無限ループが怖いので。
    translation = rhutil.coerce3dvector([0, 0, -1], True)
    xf = Rhino.Geometry.Transform.Translation(translation)  # create the translation for transform
    for _ in range(move_distance):
        flag = False
        for i in range(len(breps)):
            breps[i].Transform(xf)
            mesh.Transform(xf)
            rc = Rhino.Geometry.Intersect.Intersection.BrepSurface(breps[0], srf, 0.01)
            if not rc[1]:
                continue
            elif rc[1]:
                flag = True
                break
        if flag:
            break

elif surface_check:
    move_distance = 500
    translation = rhutil.coerce3dvector([0,0,-1], True)
    xf = Rhino.Geometry.Transform.Translation(translation)
    for i in range(move_distance):
        mesh.Transform(xf)
        rc = Rhino.Geometry.Intersect.Intersection.BrepSurface(mesh, srf, 0.01)
        if not rc[1]:
            continue
        elif rc[1]:
            break

# Bake the mesh object
if mesh_check:
    scriptcontext.doc.Objects.AddMesh(mesh)  # in meshToSurface There [0] in object surface
    rs.DeleteObjects(person)  # Delete the Original Object
elif surface_check:
    scriptcontext.doc.Objects.AddBrep(mesh)
    rs.DeleteObjects(person)

scriptcontext.doc.Views.Redraw()  # Redraw the View of Rhino