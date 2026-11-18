import bpy


class VIEW3D_MT_object_mode_itools(bpy.types.Menu):
    bl_label = "Interactive Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.super_smart_create", text="Super Smart Create")
        layout.operator("mesh.smart_delete", text="Smart Delete")
        layout.operator("mesh.smart_modify", text="Smart Modify")
        layout.operator("mesh.smart_extrude", text="Smart Extrude")

        layout.separator()
        layout.operator("mesh.quick_pivot", text="Quick Origin")
        layout.operator("mesh.simple_edit_pivot", text="Edit Origin")
        layout.operator("mesh.transform_options_pie", text="Quick Transform Orientation")
        layout.operator('mesh.quick_align', text="Quick Align")
        layout.operator('mesh.quick_lattice', text="Quick Lattice")
        layout.operator('mesh.rebase_cylinder', text="Edit Rebased Cylinder")
        layout.operator('mesh.radial_symmetry', text="Radial Symmetry")

        layout.separator()
        layout.operator('uv.seams_from_sharps', text="Seams From Sharps")
        layout.operator('uv.uvs_from_sharps', text="Uvs From Sharps")

        layout.separator()
        layout.operator("object.transform_apply", text="Apply Transforms")
        layout.operator("object.convert", text="Convert To...")
        layout.operator("object.duplicates_make_real", text="Make Instances Real")


class VIEW3D_MT_edit_mesh_itools(bpy.types.Menu):
    bl_label = "Interactive Tools"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.super_smart_create", text="Super Smart Create")
        layout.operator("mesh.smart_delete", text="Smart Delete")
        layout.operator("mesh.smart_modify", text="Smart Modify")
        layout.operator("mesh.smart_extrude", text="Smart Extrude")

        layout.separator()
        layout.operator("mesh.quick_pivot", text="Quick Origin")
        layout.operator("mesh.transform_options_pie", text="Quick Transform Orientation")
        layout.operator('mesh.quick_pipe', text="Quick Pipe")
        layout.operator('mesh.quick_lattice', text="Quick Lattice")
        layout.operator('mesh.rebase_cylinder', text="Rebase Cylinder")

        layout.separator()
        layout.operator('uv.seams_from_islands', text="Seams From Islands")
        layout.operator('uv.seams_from_sharps', text="Seams From Sharps")
        layout.operator('uv.uvs_from_sharps', text="Uvs From Sharps")


class VIEW3D_MT_edit_lattice_itools(bpy.types.Menu):
    bl_label = "Interactive Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.quick_lattice", text="Apply Lattice")
        layout.operator("mesh.lattice_resolution_2x2x2", text="Preset 2X2X2")
        layout.operator("mesh.lattice_resolution_3x3x3", text="Preset 3X3X3")
        layout.operator("mesh.lattice_resolution_4x4x4", text="Preset 4X4X4")


class VIEW3D_MT_edit_uvs_itools(bpy.types.Menu):
    bl_label = "Interactive Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator('uv.seams_from_islands', text="Seams From Islands")
        layout.operator('uv.seams_from_sharps', text="Seams From Sharps")
        layout.operator('uv.uvs_from_sharps', text="UVs From Sharps")
        layout.operator("mesh.smart_modify", text="Smart Modify")


def menu_object_mode_itools(self, context):
    self.layout.menu("VIEW3D_MT_object_mode_itools")
    self.layout.separator()


def menu_edit_mesh_itools(self, context):
    self.layout.menu("VIEW3D_MT_edit_mesh_itools")
    self.layout.separator()


def menu_edit_lattice_itools(self, context):
    self.layout.menu("VIEW3D_MT_edit_lattice_itools")
    self.layout.separator()


def menu_edit_uvs_itools(self, context):
    self.layout.menu("VIEW3D_MT_edit_uvs_itools")
    self.layout.separator()


# (menu class name, draw function). Menu names can change between Blender
# versions, a missing one is skipped instead of stopping the addon from loading.
def _menu_targets():
    return (
        ("VIEW3D_MT_object_context_menu", menu_object_mode_itools),
        ("VIEW3D_MT_edit_mesh_context_menu", menu_edit_mesh_itools),
        ("VIEW3D_MT_edit_lattice_context_menu", menu_edit_lattice_itools),
        ("IMAGE_MT_uvs_context_menu", menu_edit_uvs_itools),
    )


def load_menus_itools():
    for menu_name, draw_function in _menu_targets():
        menu = getattr(bpy.types, menu_name, None)

        if menu is None:
            print("Interactive Tools: menu %s not found, skipping" % menu_name)
            continue

        menu.prepend(draw_function)


def unload_menus_itools():
    for menu_name, draw_function in _menu_targets():
        menu = getattr(bpy.types, menu_name, None)

        if menu is None:
            continue

        try:
            menu.remove(draw_function)
        except (ValueError, RuntimeError):
            pass
