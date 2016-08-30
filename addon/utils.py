try:
    import bpy
except:
    pass
import os.path as op
import time
import math


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
