import bpy
import os.path as op
import glob


def update_something():
    pass


def do_somthing():
    pass


def template_files_update(self, context):
    if MorphPanel.init:
        update_something()


def template_draw(self, context):
    layout = self.layout
    layout.operator(LoadButton.bl_idname, text="Do something", icon='ROTATE')


class LoadButton(bpy.types.Operator):
    bl_idname = "ns.load_button"
    bl_label = "Morph botton"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        do_somthing()
        return {'PASS_THROUGH'}


class MorphPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "NS"
    bl_label = "Morphology"
    addon = None
    init = False

    def draw(self, context):
        if MorphPanel.init:
            template_draw(self, context)


def init(addon):
    MorphPanel.addon = addon
    register()
    MorphPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(MorphPanel)
        bpy.utils.register_class(LoadButton)
    except:
        print("Can't register Morph Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(MorphPanel)
        bpy.utils.unregister_class(LoadButton)
    except:
        pass
