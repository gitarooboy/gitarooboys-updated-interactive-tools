import bpy
import bmesh
import math
from ..utils import itools as itools


def selected_uv_verts_pos():
    """
    Positions of the selected UVs.

    BMLoopUV.select was removed in Blender 5.0 (UV selection is stored
    separately from the UV coordinates now). Nothing in the addon depends on
    this anymore, so on versions without the attribute it returns an empty list
    instead of raising.
    """
    bm = itools.get_bmesh()
    uv_layer = bm.loops.layers.uv.verify()

    try:
        return [loop[uv_layer].uv.copy() for face in bm.faces
                for loop in face.loops if loop[uv_layer].select]
    except AttributeError:
        return []


def sharp_to_seams(context, selection=[]):
    mode = itools.get_mode()
    me = context.object.data

    itools.set_mode('EDGE')

    if len(selection) < 1:
        bm = itools.get_bmesh()
        selection = [edge for edge in bm.edges]

    for edge in selection:
        edge.seam = False

    for edge in selection:
        if not edge.smooth:
            edge.seam = True

    itools.set_mode('OBJECT')
    itools.set_mode(mode)


class QuickRotateUv90Pos(bpy.types.Operator):
    bl_idname = "uv.rotate_90_pos"
    bl_label = "Rotate UV 90 +"
    bl_description = "Rotate Uvs +90 degrees"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # The UV positions used to be read before and after the rotation, but
        # the result was never used and reading UV selection raises on Blender 5.0+
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Z')
        return{'FINISHED'}


class QuickRotateUv90Neg(bpy.types.Operator):
    bl_idname = "uv.rotate_90_neg"
    bl_label = "Rotate UV 90 -"
    bl_description = "Rotate Uvs -90 degrees"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.transform.rotate(value=math.radians(-90), orient_axis='Z')
        return{'FINISHED'}


class SeamsFromSharps(bpy.types.Operator):
    bl_idname = "uv.seams_from_sharps"
    bl_label = "Seams From Sharps"
    bl_description = "Convets hard edges to seams"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mode = itools.get_mode()
        selection = []

        if mode in ['VERT', 'EDGE', 'FACE']:
            bm = itools.get_bmesh()
            itools.set_mode('EDGE')
            selection = itools.get_selected()

        sharp_to_seams(context, selection)
        itools.set_mode(mode)
        return{'FINISHED'}


class UvsFromSharps(bpy.types.Operator):
    bl_idname = "uv.uvs_from_sharps"
    bl_label = "UVs From Sharps"
    bl_description = "Convets hard edges to seams and unwraps the model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mode = itools.get_mode()
        selection = []

        itools.set_mode('EDGE')
        bm = itools.get_bmesh()
        selection = itools.get_selected()
        sharp_to_seams(context, selection)

        if len(selection) < 1:
            bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
        bpy.ops.mesh.select_all(action='SELECT')
        return{'FINISHED'}
