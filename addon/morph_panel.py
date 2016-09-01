import bpy
import os.path as op
import importlib
import glob
import sys
import time
import numpy as np

import utils
importlib.reload(utils)

sys.path.append(utils.get_preproc_fol())
import morph as preproc
importlib.reload(preproc)


NEURON_EMPTY_LAYER = 0
NEURON_MORPH_LAYER = 1

bpy.types.Scene.hoc_file = bpy.props.StringProperty(
    name="hoc file",
    description="",
    subtype="FILE_PATH")


def load_hoc_file():
    hoc_fname = bpy.path.abspath(bpy.context.scene.hoc_file)
    print('Loading hoc file {}'.format(hoc_fname))
    comp_names, points, rad = preproc.parse_hoc_file(hoc_fname)
    return comp_names, points/10.0, rad/10.0


def initialize_neuron():
    neuron_layer = NEURON_EMPTY_LAYER
    bpy.context.scene.layers = [ind == neuron_layer for ind in range(len(bpy.context.scene.layers))]
    layers_array = bpy.context.scene.layers
    emptys_names = ["Neuron", "Morph"]
    for name in emptys_names:
        utils.create_empty_if_doesnt_exists(name, neuron_layer, layers_array)
    bpy.context.scene.layers = [ind == NEURON_MORPH_LAYER for ind in range(len(bpy.context.scene.layers))]


def plot_neuron(all_points, radius, names):
    parent_obj = bpy.data.objects['Morph']
    layers_morph = [ind == NEURON_MORPH_LAYER for ind in range(len(bpy.context.scene.layers))]
    now = time.time()
    N = len(names)
    con_color = np.random.uniform(0.2, 0.2, [N, 3])
    for ind, (points, rad, name) in enumerate(zip(all_points[:N], radius[:N], names[:N])):
        curr_con_color = np.hstack((con_color[ind, :], [0.]))
        utils.time_to_go(now, ind, N, 100)
        utils.create_cylinder(points[:3], points[3:], rad, layers_morph)
        # cur_obj = utils.create_spline([points[:3], points[3:]], layers_morph, bevel_depth=rad)
        cur_obj = bpy.context.active_object
        cur_obj.name = name
        cur_obj.parent = parent_obj
        utils.create_material('{}_mat'.format(name), curr_con_color, 1)

    print('{} compartments were created!'.format(N))
    for name in names:
        bpy.data.objects[name].data.use_auto_smooth = True


def morph_draw(self, context):
    layout = self.layout
    layout.label(text='hoc file:')
    layout.prop(context.scene, 'hoc_file', text="")
    layout.operator(LoadButton.bl_idname, text="Load hoc file", icon='LOAD_FACTORY')


class LoadButton(bpy.types.Operator):
    bl_idname = "ns.load_morph"
    bl_label = "Load Morph"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        names, points, rad = load_hoc_file()
        plot_neuron(points, rad, names)
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
            morph_draw(self, context)


def init(addon):
    print('Loading morph panel')
    initialize_neuron()
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
