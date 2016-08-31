import bpy
import os.path as op
import numpy as np
import glob
import utils


def color_compartments():
    d = ColoringPanel.data
    # for name, color in zip(d['names'], d['colors']):
    for name,
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
    data = None

    def draw(self, context):
        if ColoringPanel.init:
            coloring_draw(self, context)


def init(addon):
    print('Loading coloring panel')
    ColoringPanel.addon = addon
    # ColoringPanel.data = np.load(op.join(utils.get_user_fol(), 'voltage.npz'))
    ColoringPanel.data = {}
    data_fol = op.join(utils.get_user_fol(), 'voltage')
    for voltage_fname in glob.glob(op.join(data_fol, '*.npy')):
        comp_name = utils.namebase(voltage_fname)
        ColoringPanel.data[comp_name] = np.load(voltage_fname)
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
