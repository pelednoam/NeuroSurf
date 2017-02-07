try:
    import bpy
except:
    pass
import os.path as op
import time
import math
import numpy as np
import pickle
import os
from collections import OrderedDict


def make_dir(fol):
    if not os.path.isdir(fol):
        os.makedirs(fol)
    return fol


def save(obj, fname):
    with open(fname, 'wb') as fp:
        pickle.dump(obj, fp, protocol=4)


def load(fname):
    with open(fname, 'rb') as fp:
        obj = pickle.load(fp)
    if obj is None:
        print('the data in {} is None!'.format(fname))
    return obj


def get_user_fol():
    root_fol = bpy.path.abspath('//')
    neuron_name = get_neuron_name()
    return op.join(root_fol, neuron_name)


def get_neuron_name():
    return namebase(bpy.data.filepath).split('_')[0]


def namebase(file_name):
    return op.splitext(op.basename(file_name))[0]


def create_empty_if_doesnt_exists(name, brain_layer, layers_array, parent_obj_name='Neuron'):
    if bpy.data.objects.get(name) is None:
        layers_array[brain_layer] = True
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=(0, 0, 0), layers=layers_array)
        bpy.data.objects['Empty'].name = name
        if name != parent_obj_name:
            bpy.data.objects[name].parent = bpy.data.objects[parent_obj_name]


def get_current_fol():
    return op.dirname(op.realpath(__file__))


def get_parent_fol(curr_dir='', levels=1):
    if curr_dir == '':
        curr_dir = get_current_fol()
    parent_fol = op.split(curr_dir)[0]
    for _ in range(levels - 1):
        parent_fol = get_parent_fol(parent_fol)
    return parent_fol


def get_preproc_fol():
    return op.join(get_parent_fol(), 'preproc')


def time_to_go(now, run, runs_num, runs_num_to_print=10):
    if run % runs_num_to_print == 0 and run != 0:
        time_took = time.time() - now
        more_time = time_took / run * (runs_num - run)
        print('{}/{}, {:.2f}s, {:.2f}s to go!'.format(run, runs_num, time_took, more_time))


def create_spline(points, layers_array, bevel_depth=0.045, resolution_u=5):
    # points = [ [1,1,1], [-1,1,1], [-1,-1,1], [1,-1,-1] ]
    curvedata = bpy.data.curves.new(name="Curve", type='CURVE')
    curvedata.dimensions = '3D'
    curvedata.fill_mode = 'FULL'
    curvedata.bevel_depth = bevel_depth
    ob = bpy.data.objects.new("CurveObj", curvedata)
    bpy.context.scene.objects.link(ob)

    spline = curvedata.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for num in range(len(spline.bezier_points)):
        spline.bezier_points[num].co = points[num]
        spline.bezier_points[num].handle_right_type = 'AUTO'
        spline.bezier_points[num].handle_left_type = 'AUTO'
    spline.resolution_u = resolution_u
    #spline.order_u = 6
    #spline.use_bezier_u = True
    #spline.radius_interpolation = 'BSPLINE'
    #print(spline.type)
    #spline.use_smooth = True
    bpy.ops.object.move_to_layer(layers=layers_array)
    return ob


def create_cylinder(p1, p2, r, layers_array):
    # From http://blender.stackexchange.com/questions/5898/how-can-i-create-a-cylinder-linking-two-points-with-python
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=dist, location=(dx/2 + x1, dy/2 + y1, dz/2 + z1))#, layers=layers_array)

    phi = math.atan2(dy, dx)
    theta = math.acos(dz/dist)
    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi
    bpy.ops.object.move_to_layer(layers=layers_array)


def create_material(name, diffuseColors, transparency, copy_material=True):
    curMat = bpy.context.active_object.active_material
    if copy_material or 'MyColor' not in curMat.node_tree.nodes:
        #curMat = bpy.data.materials['OrigPatchesMat'].copy()
        curMat = bpy.data.materials['OrigPatchMatTwoCols'].copy()
        curMat.name = name
        bpy.context.active_object.active_material = curMat
    curMat.node_tree.nodes['MyColor'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyColor1'].inputs[0].default_value = diffuseColors
    curMat.node_tree.nodes['MyTransparency'].inputs['Fac'].default_value = transparency
    bpy.context.active_object.active_material.diffuse_color = diffuseColors[:3]


def insert_keyframe_to_custom_prop(obj, prop_name, value, keyframe):
    bpy.context.scene.objects.active = obj
    obj.select = True
    obj[prop_name] = value
    obj.keyframe_insert(data_path='[' + '"' + prop_name + '"' + ']', frame=keyframe)


def view_all_in_graph_editor(context=None):
    try:
        if context is None:
            context = bpy.context
        graph_area = [context.screen.areas[k] for k in range(len(context.screen.areas)) if
                      context.screen.areas[k].type == 'GRAPH_EDITOR'][0]
        graph_window_region = [graph_area.regions[k] for k in range(len(graph_area.regions)) if
                               graph_area.regions[k].type == 'WINDOW'][0]

        c = context.copy()  # copy the context
        c['area'] = graph_area
        c['region'] = graph_window_region
        bpy.ops.graph.view_all(c)
    except:
        pass


def can_color_obj(obj):
    cur_mat = obj.active_material
    return 'RGB' in cur_mat.node_tree.nodes


def object_coloring(obj, rgb):
    if not obj:
        print('object_coloring: obj is None!')
        return False
    bpy.context.scene.objects.active = obj
    # todo: do we need to select the object here? In diff mode it's a problem
    # obj.select = True
    cur_mat = obj.active_material
    cur_mat.diffuse_color = rgb
    diffuse_colors = np.hstack((rgb, [0.]))
    cur_mat.node_tree.nodes['MyColor'].inputs[0].default_value = diffuse_colors
    cur_mat.node_tree.nodes['MyColor1'].inputs[0].default_value = diffuse_colors

    # if can_color_obj(obj):
    #     cur_mat.node_tree.nodes["RGB"].outputs[0].default_value = new_color
        # new_color = get_obj_color(obj)
        # print('{} new color: {}'.format(obj.name, new_color))
    # else:
    #     print("Can't color {}".format(obj.name))
    #     return False
    return True


def evaluate_fcurves(parent_obj, time_range):
    data = OrderedDict()
    colors = OrderedDict()
    for fcurve in parent_obj.animation_data.action.fcurves:
        if fcurve.hide:
            continue
        name = fcurve.data_path.split('"')[1]
        print('{} extrapolation'.format(name))
        # todo: we should return the interpolation to its previous value
        # for kf in fcurve.keyframe_points:
        #     kf.interpolation = 'BEZIER'
        data[name] = []
        for t in time_range:
            d = fcurve.evaluate(t)
            data[name].append(d)
        colors[name] = tuple(fcurve.color)
    return data, colors
