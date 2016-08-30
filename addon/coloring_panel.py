import bpy
import os.path as op
import numpy as np

import utils


def color_compartments():
    d = np.load(op.join(utils.get_user_fol(), 'voltage.npz'))
    for name, color in zip(d['names'], d['colors']):
        rgb = color[bpy.context.scene.frame_current, :]
        obj = bpy.data.objects[name]
        utils.object_coloring(obj, rgb)


def coloring_draw(self, context):
    layout = self.layout
    layout.operator(ColorCompartment.bl_idname, text="Color", icon='EYEDROPPER')


class ColorCompartment(bpy.types.Operator):
    bl_idname = "ns.load_morph"
    bl_label = "Load Morph"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        color_compartments()
        return {'PASS_THROUGH'}


class ColoringPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "NS"
    bl_label = "Coloring"
    addon = None
    init = False

    def draw(self, context):
        if ColoringPanel.init:
            coloring_draw(self, context)


def init(addon):
    print('Loading coloring panel')
    ColoringPanel.addon = addon
    register()
    ColoringPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(ColoringPanel)
        bpy.utils.register_class(ColorCompartment)
    except:
        print("Can't register Coloring Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(ColoringPanel)
        bpy.utils.unregister_class(ColorCompartment)
    except:
        pass
