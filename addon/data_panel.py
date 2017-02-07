import bpy
import os.path as op
import numpy as np
import time
import traceback
import ns_utils


def import_voltage(t_start=0, t_end=-1):
    d = np.load(op.join(ns_utils.get_user_fol(), 'voltage.npz'))
    for data, obj_name in zip(d['voltage'], d['names']):
        if obj_name != 'soma':
            continue
        data = data[t_start:t_end]
        print(obj_name, data.shape)
        cur_obj = bpy.data.objects[obj_name]
        # ns_utils.insert_keyframe_to_custom_prop(cur_obj, obj_name, 0, 1)
        # ns_utils.insert_keyframe_to_custom_prop(cur_obj, obj_name, 0, len(data) + 2)
        print('keyframing ' + obj_name + ' object')
        now = time.time()
        N = len(data)
        for ind, timepoint in enumerate(data):
            ns_utils.time_to_go(now, ind, N, 1000)
            # print('keyframing '+obj_name+' object')
            ns_utils.insert_keyframe_to_custom_prop(cur_obj, obj_name, timepoint, ind)

        # remove the orange keyframe sign in the fcurves window
        # fcurves = bpy.data.objects[obj_name].animation_data.action.fcurves[0]
        # mod = fcurves.modifiers.new(type='LIMITS')

    ns_utils.view_all_in_graph_editor()
    for obj in bpy.data.objects:
        obj.select = False
    try:
        bpy.ops.graph.previewrange_set()
    except:
        pass


def data_draw(self, context):
    layout = self.layout
    layout.operator(ImportVoltage.bl_idname, text="Import voltage", icon='FCURVE')


class ImportVoltage(bpy.types.Operator):
    bl_idname = "ns.import_voltage"
    bl_label = "Load Morph"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        import_voltage(40000, 80000)
        return {'PASS_THROUGH'}


class DataPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "NeuroSurf"
    bl_label = "Data"
    addon = None
    init = False

    def draw(self, context):
        if DataPanel.init:
            data_draw(self, context)


def init(addon):
    print('Loading data panel')
    DataPanel.addon = addon
    register()
    DataPanel.init = True


def register():
    try:
        unregister()
        bpy.utils.register_class(DataPanel)
        bpy.utils.register_class(ImportVoltage)
    except:
        print("Can't register Data Panel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(DataPanel)
        bpy.utils.unregister_class(ImportVoltage)
    except:
        pass
