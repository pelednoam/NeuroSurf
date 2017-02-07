
import bpy
import os.path as op
import numpy as np
import glob
import traceback
import ns_utils


def color_compartments():
    if bpy.data.objects.get('Morph', None) is None:
        return
    d = ColoringPanel.data
    print('Start coloring the comps')
    t = bpy.context.scene.frame_current + ColoringPanel.t_start
    for name, color, val in zip(d['names'], d['colors'], d['voltage']):
        rgb = color[t, :]
        obj = bpy.data.objects.get(name, None)
        if obj is None:
            continue
        if name == 'soma':
            print(name, rgb, t, val[t])
        ns_utils.object_coloring(obj, rgb)
    print('Finish coloring the comps')


def coloring_draw(self, context):
    layout = self.layout
    soma_voltage = ColoringPanel.data['voltage'][ColoringPanel.soma_index,
                                                 bpy.context.scene.frame_current + ColoringPanel.t_start]
    layout.label(text='{}'.format(soma_voltage))
    layout.operator(ColorCompartment.bl_idname, text="Color", icon='EYEDROPPER')


class ColorCompartment(bpy.types.Operator):
    bl_idname = "ns.color_compartments"
    bl_label = "Load Morph"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        color_compartments()
        return {'PASS_THROUGH'}


class ColoringPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "NeuroSurf"
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
    ColoringPanel.data = np.load(op.join(ns_utils .get_user_fol(), 'voltage.npz'))
    ColoringPanel.soma_index = np.where(ColoringPanel.data['names'] == 'soma')[0]
    ColoringPanel.t_start = 40000
    # ColoringPanel.data = {}
    # data_fol = op.join(ns_utils .get_user_fol(), 'voltage')
    # for voltage_fname in glob.glob(op.join(data_fol, '*.npy')):
    #     comp_name = ns_utils .namebase(voltage_fname)
    #     ColoringPanel.data[comp_name] = np.load(voltage_fname)
    register()
    ColoringPanel.init = True
    print('Finish loading coloring panel')


def register():
    try:
        unregister()
        bpy.utils .register_class(ColoringPanel)
        bpy.utils .register_class(ColorCompartment)
    except:
        print("Can't register Coloring Panel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils .unregister_class(ColoringPanel)
        bpy.utils .unregister_class(ColorCompartment)
    except:
        pass
