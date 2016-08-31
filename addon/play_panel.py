import bpy
import os.path as op
import numpy as np
import traceback
import time
import os
from collections import OrderedDict
import utils 

bpy.types.Scene.play_from = bpy.props.IntProperty(default=0, min=0, description="When to filter from")
bpy.types.Scene.play_to = bpy.props.IntProperty(default=bpy.context.scene.frame_end, min=0,
                                                  description="When to filter to")
bpy.types.Scene.play_dt = bpy.props.IntProperty(default=50, min=1, description="play dt (ms)")
bpy.types.Scene.play_time_step = bpy.props.FloatProperty(default=0.1, min=0,
                                                  description="How much time (s) to wait between frames")
bpy.types.Scene.render_movie = bpy.props.BoolProperty(default=False, description="Render the movie")
bpy.types.Scene.play_type = bpy.props.EnumProperty(
    items=[("voltage", "Voltage", "", 1)], description='Type pf data to play')


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    # limits = bpy.props.IntProperty(default=bpy.context.scene.play_from)
    limits = bpy.context.scene.play_from
    _timer = None
    _time = time.time()

    def modal(self, context, event):
        # First frame initialization:
        if PlayPanel.init_play:
            self.limits = bpy.context.scene.frame_current

        if not PlayPanel.is_playing:
            return {'PASS_THROUGH'}

        if event.type in {'RIGHTMOUSE', 'ESC'} or self.limits > bpy.context.scene.play_to:
            plot_something(context, bpy.context.scene.play_to)
            self.limits = bpy.context.scene.play_from
            PlayPanel.is_playing = False
            bpy.context.scene.update()
            self.cancel(context)
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            if time.time() - self._time > bpy.context.scene.play_time_step:
                bpy.context.scene.frame_current = self.limits
                print(self.limits, time.time() - self._time)
                self._time = time.time()
                try:
                    plot_something(context, self.limits)
                except:
                    print(traceback.format_exc())
                    print('Error in plotting at {}!'.format(self.limits))
                self.limits = self.limits - bpy.context.scene.play_dt if PlayPanel.play_reverse else \
                        self.limits + bpy.context.scene.play_dt
                bpy.context.scene.frame_current = self.limits

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self.cancel(context)
        ModalTimerOperator._timer = wm.event_timer_add(time_step=0.05, window=context.window)
        self._time = time.time()
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # if ModalTimerOperator._timer:
        if ModalTimerOperator._timer:
            wm = context.window_manager
            wm.event_timer_remove(ModalTimerOperator._timer)


def render_movie(play_type, play_from, play_to, play_dt=1):
    bpy.context.scene.play_type = play_type
    bpy.context.scene.render_movie = True
    print('In play movie!')
    for limits in range(play_from, play_to + 1, play_dt):
        print('limits: {}'.format(limits))
        bpy.context.scene.frame_current = limits
        try:
            plot_something(bpy.context, limits)
        except:
            print(traceback.format_exc())
            print('Error in plotting at {}!'.format(limits))


def plot_something(context, cur_frame):
    if bpy.context.scene.frame_current > bpy.context.scene.play_to:
        return

    play_type = bpy.context.scene.play_type
    successful_ret = True
    if play_type in ['voltage']:
        PlayPanel.addon.color_compartments()
    if bpy.context.scene.render_movie:
        if successful_ret:
            PlayPanel.addon.render_image()
        else:
            print("The image wasn't rendered due to an error in the plotting.")


def capture_graph(play_type=None, output_path=None, selection_type=None):
    if play_type:
        bpy.context.scene.play_type = play_type
    if output_path:
        bpy.context.scene.output_path = output_path
    if selection_type:
        bpy.context.scene.selection_type = selection_type

    play_type = bpy.context.scene.play_type
    image_fol = bpy.path.abspath(bpy.context.scene.output_path)
    if not op.isdir(image_fol):
        raise Exception('You need to set first the images folder in the Render panel!')
    graph_data, graph_colors = {}, {}

    if play_type in ['voltage']:
        graph_data['voltage'], graph_colors['voltage'] = capture_graph_data()
    save_graph_data(graph_data, graph_colors, image_fol)


def save_graph_data(data, graph_colors, image_fol):
    if not os.path.isdir(image_fol):
        os.makedirs(image_fol)
    utils.save((data, graph_colors), op.join(image_fol, 'data.pkl'))
    print('Saving data into {}'.format(op.join(image_fol, 'data.pkl')))


def get_meg_data(per_condition=True):
    time_range = range(PlayPanel.addon.get_max_time_steps())
    brain_obj = bpy.data.objects['Brain']
    if per_condition:
        meg_data, meg_colors = OrderedDict(), OrderedDict()
        rois_objs = bpy.data.objects['Cortex-lh'].children + bpy.data.objects['Cortex-rh'].children
        for roi_obj in rois_objs:
            if roi_obj.animation_data:
                meg_data_roi, meg_colors_roi = mu.evaluate_fcurves(roi_obj, time_range)
                meg_data.update(meg_data_roi)
                meg_colors.update(meg_colors_roi)
    else:
        meg_data, meg_colors = mu.evaluate_fcurves(brain_obj, time_range)
    return meg_data, meg_colors


def init_plotting():
    pass


def set_play_from(play_from):
    bpy.context.scene.frame_current = play_from
    bpy.context.scene.play_from = play_from
    bpy.data.scenes['Scene'].frame_preview_start = play_from
    ModalTimerOperator.limits = play_from


def set_play_to(play_to):
    bpy.context.scene.play_to = play_to
    bpy.data.scenes['Scene'].frame_preview_end = play_to


def set_play_dt(play_dt):
    bpy.context.scene.play_dt = play_dt


def set_play_type(play_type):
    bpy.context.scene.play_type = play_type


class PlayPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "ns"
    bl_label = "Play"
    addon = None
    data = None
    loop_indices = None
    is_playing = False
    play_reverse = False
    first_time = True
    init_play = True

    def draw(self, context):
        play_panel_draw(context, self.layout)


def play_panel_draw(context, layout):
    row = layout.row(align=0)
    row.prop(context.scene, "play_from", text="From")
    row.operator(GrabFromPlay.bl_idname, text="", icon='BORDERMOVE')
    row.prop(context.scene, "play_to", text="To")
    row.operator(GrabToPlay.bl_idname, text="", icon='BORDERMOVE')
    row = layout.row(align=0)
    row.prop(context.scene, "play_dt", text="dt")
    row.prop(context.scene, "play_time_step", text="time step")
    layout.prop(context.scene, "play_type", text="")
    row = layout.row(align=True)
    # row.operator(Play.bl_idname, text="", icon='PLAY' if not PlayPanel.is_playing else 'PAUSE')
    row.operator(PrevKeyFrame.bl_idname, text="", icon='PREV_KEYFRAME')
    row.operator(Reverse.bl_idname, text="", icon='PLAY_REVERSE')
    row.operator(Pause.bl_idname, text="", icon='PAUSE')
    row.operator(Play.bl_idname, text="", icon='PLAY')
    row.operator(NextKeyFrame.bl_idname, text="", icon='NEXT_KEYFRAME')
    layout.prop(context.scene, 'render_movie', text="Render to a movie")
    layout.operator(ExportGraph.bl_idname, text="Export graph", icon='SNAP_NORMAL')


class Play(bpy.types.Operator):
    bl_idname = "ns.play"
    bl_label = "play"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = True
        PlayPanel.play_reverse = False
        PlayPanel.init_play = True
        if PlayPanel.first_time:
            print('Starting the play timer!')
            # PlayPanel.first_time = False
            ModalTimerOperator.limits = bpy.context.scene.play_from
            bpy.ops.wm.modal_timer_operator()
        return {"FINISHED"}


class Reverse(bpy.types.Operator):
    bl_idname = "ns.reverse"
    bl_label = "reverse"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = True
        PlayPanel.play_reverse = True
        if PlayPanel.first_time:
            PlayPanel.first_time = False
            PlayPanel.timer_op = bpy.ops.wm.modal_timer_operator()
        return {"FINISHED"}


class Pause(bpy.types.Operator):
    bl_idname = "ns.pause"
    bl_label = "pause"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        plot_something(context, bpy.context.scene.frame_current)
        return {"FINISHED"}


class PrevKeyFrame(bpy.types.Operator):
    bl_idname = 'ns.prev_key_frame'
    bl_label = 'prevKeyFrame'
    bl_options = {'UNDO'}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        bpy.context.scene.frame_current -= bpy.context.scene.play_from
        plot_something(context, bpy.context.scene.frame_current)
        return {'FINISHED'}


class NextKeyFrame(bpy.types.Operator):
    bl_idname = "ns.next_key_frame"
    bl_label = "nextKeyFrame"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        PlayPanel.is_playing = False
        bpy.context.scene.frame_current += bpy.context.scene.play_dt
        plot_something(context, bpy.context.scene.frame_current)
        return {"FINISHED"}


class GrabFromPlay(bpy.types.Operator):
    bl_idname = "ns.grab_from_play"
    bl_label = "grab from"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        set_play_from(bpy.context.scene.frame_current)
        return {"FINISHED"}


class GrabToPlay(bpy.types.Operator):
    bl_idname = "ns.grab_to_play"
    bl_label = "grab to"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        set_play_to(bpy.context.scene.frame_current)
        return {"FINISHED"}


class ExportGraph(bpy.types.Operator):
    bl_idname = "ns.export_graph"
    bl_label = "ns export_graph"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        capture_graph()
        return {"FINISHED"}


def init(addon):
    register()
    PlayPanel.addon = addon
    init_plotting()


def register():
    try:
        unregister()
        bpy.utils.register_class(PlayPanel)
        bpy.utils.register_class(GrabFromPlay)
        bpy.utils.register_class(GrabToPlay)
        bpy.utils.register_class(Play)
        bpy.utils.register_class(Reverse)
        bpy.utils.register_class(PrevKeyFrame)
        bpy.utils.register_class(NextKeyFrame)
        bpy.utils.register_class(Pause)
        bpy.utils.register_class(ModalTimerOperator)
        bpy.utils.register_class(ExportGraph)
    except:
        print("Can't register PlayPanel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(PlayPanel)
        bpy.utils.unregister_class(GrabFromPlay)
        bpy.utils.unregister_class(GrabToPlay)
        bpy.utils.unregister_class(Play)
        bpy.utils.unregister_class(Reverse)
        bpy.utils.unregister_class(PrevKeyFrame)
        bpy.utils.unregister_class(NextKeyFrame)
        bpy.utils.unregister_class(Pause)
        bpy.utils.unregister_class(ModalTimerOperator)
        bpy.utils.unregister_class(ExportGraph)
    except:
        pass
