bl_info = {
    'name': 'NeuroSurf',
    'author': 'Avi Libster & Noam Peled',
    'version': (1, 0),
    'blender': (2, 7, 2),
    'location': 'Press [Space], search for "NeuroSurf"',
    'category': 'Development',
}

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import sys
import os
import os.path as op
import importlib as imp
import glob

# How to crate a launcher in mac:
# http://apple.stackexchange.com/questions/115114/how-to-put-a-custom-launcher-in-the-dock-mavericks

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def mmvt_dir():
    return bpy.path.abspath('//')

# https://github.com/sybrenstuvel/random-blender-addons/blob/master/remote_debugger.py
class NeuroSurfLoaderAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    neurosurf_folder = StringProperty(
        name='Path of the NeuroSurf addon folder', description='', subtype='DIR_PATH',
        default='') #os.path.join(mmvt_dir(), 'mmvt_addon'))
    # python_cmd = StringProperty(
    #     name='Path to python (anaconda 3.5)', description='', subtype='FILE_PATH', default='python')
    # freeview_cmd = StringProperty(
    #     name='Path to freeview command', description='', subtype='FILE_PATH', default='freeview')
    # freeview_cmd_verbose = BoolProperty( name='Use the verbose flag', default=False)
    # freeview_cmd_stdin = BoolProperty(name='Use the stdin flag', default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'neurosurf_folder')
        # layout.prop(self, 'python_cmd')
        # layout.prop(self, 'freeview_cmd')
        # layout.prop(self, 'freeview_cmd_verbose')
        # layout.prop(self, 'freeview_cmd_stdin')


class NeuroSurfLoaderAddon(bpy.types.Operator):
    bl_idname = 'neurosurf_addon.run_addon'
    bl_label = 'Run NeuroSurf addon'
    bl_description = 'Runs the NeuroSurf addon'

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        # mmvt_root = os.path.abspath(addon_prefs.mmvt_folder)
        neurosurf_root = bpy.path.abspath(addon_prefs.neurosurf_folder)
        print('neurosurf root: {}'.format(neurosurf_root))
        sys.path.append(neurosurf_root)
        import neurosurf_addon
        # If you change the code and rerun the addon, you need to reload MMVT_Addon
        imp.reload(neurosurf_addon)
        print(neurosurf_addon)
        neurosurf_addon.main(addon_prefs)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(NeuroSurfLoaderAddon)
    bpy.utils.register_class(NeuroSurfLoaderAddonPreferences)


def unregister():
    bpy.utils.unregister_class(NeuroSurfLoaderAddon)
    bpy.utils.unregister_class(NeuroSurfLoaderAddonPreferences)


if __name__ == '__main__':
    register()