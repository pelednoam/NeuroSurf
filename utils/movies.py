import matplotlib.animation as animation
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os.path as op
import glob
from PIL import Image
import time
import numbers
import numpy as np
import re
from utils import utils
from utils import movies_utils as mu

LINKS_DIR = utils.get_links_dir()
BLENDER_ROOT_FOLDER = op.join(LINKS_DIR, 'mmvt')


def ani_frame(time_range, xticks, images, dpi, fps, video_fname, cb_data_type,
        data_to_show_in_graph, fol, fol2, cb_title='', cb_min_max_eq=True, color_map='jet', bitrate=5000, images2=(),
        ylim=(), ylabels=(), xticklabels=(), xlabel='Time (ms)', show_first_pic=False):


    def two_brains_two_graphs():
        brain_ax = plt.subplot(gs[:-g2, :g3])
        brain_ax.set_aspect('equal')
        brain_ax.get_xaxis().set_visible(False)
        brain_ax.get_yaxis().set_visible(False)

        image = mpimg.imread(images[0])
        im = brain_ax.imshow(image, animated=True)#, cmap='gray',interpolation='nearest')

        brain_ax2 = plt.subplot(gs[:-g2, g3:-1])
        brain_ax2.set_aspect('equal')
        brain_ax2.get_xaxis().set_visible(False)
        brain_ax2.get_yaxis().set_visible(False)

        image2 = mpimg.imread(images2[0])
        im2 = brain_ax2.imshow(image2, animated=True)#, cmap='gray',interpolation='nearest')

        graph1_ax = plt.subplot(gs[-g2:, :])
        graph2_ax = graph1_ax.twinx()
        if cb_data_type != '':
            ax_cb = plt.subplot(gs[:-g2, -1])
        else:
            ax_cb = None
        plt.tight_layout()
        resize_and_move_ax(brain_ax, dx=0.04)
        resize_and_move_ax(brain_ax2, dx=-0.00)
        if cb_data_type != '':
            resize_and_move_ax(ax_cb, ddw=0.5, ddh=0.8, dx=-0.01, dy=0.06)
        for graph_ax in [graph1_ax, graph2_ax]:
            resize_and_move_ax(graph_ax, dx=0.04, dy=0.03, ddw=0.89)
        return ax_cb, im, im2, graph1_ax, graph2_ax

    def one_brain_one_graph(gs, g2, two_graphs=False):
        brain_ax = plt.subplot(gs[:-g2, :-1])
        brain_ax.set_aspect('equal')
        brain_ax.get_xaxis().set_visible(False)
        brain_ax.get_yaxis().set_visible(False)

        image = mpimg.imread(images[0])
        im = brain_ax.imshow(image, animated=True)#, cmap='gray',interpolation='nearest')

        graph1_ax = plt.subplot(gs[-g2:, :])
        graph2_ax = graph1_ax.twinx() if two_graphs else None
        ax_cb = plt.subplot(gs[:-g2, -1])
        plt.tight_layout()
        # resize_and_move_ax(brain_ax, dx=0.03)
        resize_and_move_ax(ax_cb, ddw=1, dx=-0.06)
        resize_and_move_ax(graph1_ax, dx=0.05, dy=0.03, ddw=0.89)
        if not graph2_ax is None:
            resize_and_move_ax(graph2_ax, dx=0.05, dy=0.03, ddw=0.89)
        return ax_cb, im, graph1_ax, graph2_ax

    first_image = Image.open(images[0])
    img_width, img_height = first_image.size
    print('video: width {} height {} dpi {}'.format(img_width, img_height, dpi))
    img_width_fac = 2 if fol2 != '' else 1.1
    w, h = img_width/dpi * img_width_fac, img_height/dpi * 3/2
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    fig.canvas.draw()
    g = 15
    g2 = int(g / 3)
    g3 = int ((g-1) / 2)
    gs = gridspec.GridSpec(g, g)#, height_ratios=[3, 1])

    if fol2 != '':
        ax_cb, im, im2, graph1_ax, graph2_ax = two_brains_two_graphs()
    else:
        two_graphes = len(data_to_show_in_graph) == 2
        ax_cb, im, graph1_ax, graph2_ax = one_brain_one_graph(gs, g2, two_graphes)
        im2 = None

    # gs.update(left=0.05, right=0.48, wspace=0.05)
    # graph_data, graph_colors, t_line, ymin, ymax = plot_graph(
    #     graph1_ax, data_to_show_in_graph, fol, fol2, graph2_ax, ylabels)

    graph_data, graph_colors, t_line, ymin, ymax = plot_graph(
        graph1_ax, data_to_show_in_graph, time_range, xticks, fol, fol2,
        graph2_ax, xlabel, ylabels, xticklabels, ylim, images)

    plot_color_bar(ax_cb, graph_data, cb_title, cb_data_type, cb_min_max_eq, color_map)

    now = time.time()
    if show_first_pic:
        plt.show()

    def init_func():
        return update_img(0)

    def update_img(image_index):
        # print(image_fname)
        utils.time_to_go(now, image_index, len(images))
        image = mpimg.imread(images[image_index])
        im.set_data(image)
        if im2:
            image2 = mpimg.imread(images2[image_index])
            im2.set_data(image2)

        current_t = get_t(images, image_index, time_range)
        t_line.set_data([current_t, current_t], [ymin, ymax])
        return [im]

    ani = animation.FuncAnimation(fig, update_img, len(images), init_func=init_func, interval=30, blit=True)
    writer = animation.writers['ffmpeg'](fps=fps, bitrate=bitrate)
    ani.save(op.join(fol, video_fname),writer=writer,dpi=dpi)
    return ani


def get_t(images, image_index, time_range):
    if images is None:
        return 0
    pic_name = utils.namebase(images[image_index])
    if '_t' in pic_name:
        t = int(pic_name.split('_t')[1])
        # t = time_range[1:-1:4][t]
    else:
        t = int(re.findall('\d+', pic_name)[0])
    return time_range[t - time_range[0]]


def plot_graph(graph1_ax, data_to_show_in_graph, time_range, xticks, fol, fol2='', graph2_ax=None, xlabel='',
               ylabels=(), xticklabels=(), ylim=None, images=None, green_line=True):
    graph_data, graph_colors = utils.load(op.join(fol, 'data.pkl'))
    if fol2 != '' and op.isfile(op.join(fol2, 'data.pkl')):
        graph_data2, graph_colors2 = utils.load(op.join(fol2, 'data.pkl'))
        if len(graph_data.keys()) == 1 and len(graph_data2.keys()) == 1:
            graph2_data_item = list(graph_data2.keys())[0]
            graph_data['{}2'.format(graph2_data_item)] = graph_data2[graph2_data_item]
    axes = [graph1_ax]
    if graph2_ax:
        axes = [graph1_ax, graph2_ax]

    ind = 0
    # colors = cu.get_distinct_colors(6) / 255# ['r', 'b', 'g']
    colors = ['r', 'b', 'g']
    for data_type, data_values in graph_data.items():
        if isinstance(data_values, numbers.Number):
            continue
        if data_type not in data_to_show_in_graph:
            continue
        ax = axes[ind]
        if ylabels:
            ylabel = data_type if len(ylabels) <= ind else ylabels[ind]
        else:
            ylabel = data_type
        ax.set_ylabel(ylabel, color=colors[ind] if graph2_ax else 'k')
        if graph2_ax:
            for tl in ax.get_yticklabels():
                tl.set_color(colors[ind])
        for k, values in data_values.items():
            if np.allclose(values, 0):
                continue
            color = colors[ind] if len(data_to_show_in_graph) == 2 else tuple(graph_colors[data_type][k])
            # todo: tuple doesn't have ndim, not sure what to do here
            # if graph_colors[data_type][k].ndim > 1:
            if data_type[-1] == '2':
                data_type = data_type[:-1]
            # color = graph_colors[data_type][k]
            # alpha = 0.2
            # dash = [5, 5] if ind == 1 else []
            # if color == (1.0, 1.0, 1.0):
            #     color = np.array(cu.name_to_rgb('orange')) / 255.0
            # ax.plot(time_range[1:-1:4], values, label=k, color=color, alpha=0.9, clip_on=False)#, dashes=dash)# color=tuple(graph_colors[data_type][k]))
            if len(time_range) > len(values):
                time_range = time_range[:len(values)]
            ax.plot(time_range, values, label=k, color=color,
                    alpha=0.9)  # , clip_on=False)#, dashes=dash)# color=tuple(graph_colors[data_type][k]))
        ind += 1

    graph1_ax.set_xlabel(xlabel)
    if not xticklabels is None:
        x_labels = xticks
        for xlable_time, xticklabel in xticklabels:
            if xlable_time in xticks:
                x_labels[x_labels.index(xlable_time)] = xticklabel
        graph1_ax.set_xticklabels(x_labels)

    graph1_ax.set_xlim([time_range[0], time_range[-1]])
    if graph2_ax:
        if ylim:
            ymin, ymax = ylim
        else:
            ymin1, ymax1 = graph1_ax.get_ylim()
            ymin2, ymax2 = graph2_ax.get_ylim()
            ymin = min([ymin1, ymin2])
            ymax = max([ymax1, ymax2])

        graph1_ax.set_ylim([ymin, ymax])
        graph2_ax.set_ylim([ymin, ymax])
    else:
        ymin, ymax = ylim if ylim else graph1_ax.get_ylim()
        graph1_ax.set_ylim([ymin, ymax])

    if green_line:
        t0 = get_t(images, 0, time_range)
        t_line, = graph1_ax.plot([t0, t0], [ymin, ymax], 'g-')
    else:
        t_line = None
    # plt.legend()
    return graph_data, graph_colors, t_line, ymin, ymax


def plot_color_bar(ax, graph_data, cb_title, data_type='', cb_min_max_eq=True, color_map='jet'):
    if data_type == '':
        return
    import matplotlib as mpl
    data_max = max([max(v) for v in graph_data[data_type].values()])
    data_min = min([min(v) for v in graph_data[data_type].values()])
    if cb_min_max_eq:
        data_max_min = utils.get_max_abs(data_max, data_min)
        vmin, vmax = -data_max_min, data_max_min
    else:
        vmin, vmax = data_min, data_max
    # cmap = color_map # mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = mpl.colorbar.ColorbarBase(ax, cmap=color_map, norm=norm, orientation='vertical')#, ticks=color_map_bounds)
    cb.set_label(cb_title)


def resize_and_move_ax(ax, dx=0, dy=0, dw=0, dh=0, ddx=1, ddy=1, ddw=1, ddh=1):
    ax_pos = ax.get_position() # get the original position
    ax_pos_new = [ax_pos.x0 * ddx + dx, ax_pos.y0  * ddy + dy,  ax_pos.width * ddw + dw, ax_pos.height * ddh + dh]
    ax.set_position(ax_pos_new) # set a new position


def create_movie(time_range, xticks, fol, dpi, fps, video_fname, cb_data_type,
    data_to_show_in_graph, cb_title='', cb_min_max_eq=True, color_map='jet', bitrate=5000, fol2='', ylim=(),
    ylabels=(), xticklabels=(), xlabel='Time (ms)', pics_type='png', show_first_pic=False, n_jobs=1):

    images1 = get_pics(fol, pics_type)
    images1_chunks = utils.chunks(images1, len(images1) / n_jobs)
    if fol2 != '':
        images2 = get_pics(fol2, pics_type)
        if len(images2) != len(images1):
            raise Exception('fol and fol2 have different number of pictures!')
        images2_chunks = utils.chunks(images2, int(len(images2) / n_jobs))
    else:
        images2_chunks = [''] * int(len(images1) / n_jobs)
    params = [(images1_chunk, images2_chunk, time_range, xticks, dpi, fps,
               video_fname, cb_data_type, data_to_show_in_graph, cb_title, cb_min_max_eq, color_map, bitrate,
               ylim, ylabels, xticklabels, xlabel, show_first_pic, fol, fol2, run) for \
              run, (images1_chunk, images2_chunk) in enumerate(zip(images1_chunks, images2_chunks))]
    utils.run_parallel(_create_movie_parallel, params, n_jobs)
    video_name, video_type = op.splitext(video_fname)
    mu.combine_movies(fol, video_name, video_type[1:])


def _create_movie_parallel(params):
    (images1, images2, time_range, xticks, dpi, fps,
        video_fname, cb_data_type, data_to_show_in_graph, cb_title, cb_min_max_eq, color_map, bitrate, ylim, ylabels,
        xticklabels, xlabel, show_first_pic, fol, fol2, run) = params
    video_name, video_type = op.splitext(video_fname)
    video_fname = '{}_{}{}'.format(video_name, run, video_type)
    ani_frame(time_range, xticks, images1, dpi, fps, video_fname, cb_data_type,
        data_to_show_in_graph, fol, fol2, cb_title, cb_min_max_eq, color_map, bitrate, images2, ylim, ylabels,
        xticklabels, xlabel, show_first_pic)


def sort_pics_key(pic_fname):
    pic_name = utils.namebase(pic_fname)
    if '_t' in pic_name:
        pic_name = pic_name.split('_t')[0]
    return int(re.findall('\d+', pic_name)[0])


def get_pics(fol, pics_type='png'):
    # return sorted(glob.glob(op.join(fol, '*.{}'.format(pics_type))), key=lambda x:int(utils.namebase(x)[1:]))
    # return sorted(glob.glob(op.join(fol, '*.{}'.format(pics_type))), key=lambda x:re.findall('\d+', utils.namebase(x)))
    return sorted(glob.glob(op.join(fol, '*.{}'.format(pics_type))), key=sort_pics_key)


def plot_only_graph(fol, data_to_show_in_graph, time_range_tup, xtick_dt, xlabel='', ylabels=(),
        xticklabels=(), ylim=None, images=None, fol2='', graph2_ax=None, do_show=False):
    import matplotlib.pyplot as plt
    plt = plt.figure()
    ax = plt.add_subplot(111)
    if len(time_range_tup) == 3:
        time_range = np.arange(time_range_tup[0], time_range_tup[1], time_range_tup[2])
        xticks = np.arange(time_range_tup[0], len(time_range), xtick_dt).tolist()
    else:
        time_range = np.arange(time_range_tup[0])
        xticks = None
    plot_graph(ax, data_to_show_in_graph, time_range, xticks, fol, fol2='', graph2_ax=None, xlabel=xlabel,
               ylabels=ylabels, xticklabels=xticklabels, ylim=ylim, images=None, green_line=False)
    if do_show:
        plt.show()
    plt.savefig(op.join(fol, 'graph.jpg'))


def duplicate_frames(fol, multiplier=50, pics_type='png'):
    import shutil
    pics = get_pics(fol, pics_type)
    new_fol = '{}_dup'.format(fol)
    utils.delete_folder_files(new_fol)
    pic_ind = 0
    shutil.copy(op.join(fol, 'data.pkl'), op.join(new_fol, 'data.pkl'))
    for t, pic in enumerate(pics):
        for _ in range(multiplier):
            new_pic_name = op.join(new_fol, '{}_t{}.{}'.format(pic_ind, t, pics_type))
            shutil.copy(pic, new_pic_name)
            pic_ind += 1


def save_soma():
    fol = '/home/noam/NeuroSurf/DCN/figures'
    fol2 = ''
    data_to_show_in_graph = ('voltage')
    video_fname = 'voltage.mp4'
    cb_title = 'voltage'
    time_range = range(8163,8242)
    xticks = [] #time_range
    ylim = ()
    ylabels = ["soma's voltage"]
    xticklabels = []
    xlabel = 'Time'
    cb_data_type = 'voltage'
    fps = 10
    cb_min_max_eq = False
    color_map = 'jet'

    dpi = 100
    bitrate = 5000
    pics_type = 'png'
    show_first_pic = False
    n_jobs = 1

    create_movie(time_range, xticks, fol, dpi, fps, video_fname, cb_data_type, data_to_show_in_graph, cb_title,
        cb_min_max_eq, color_map, bitrate, fol2, ylim, ylabels, xticklabels, xlabel, pics_type, show_first_pic, n_jobs)


if __name__ == '__main__':
    save_soma()
    exit

    import argparse
    from utils import args_utils as au
    parser = argparse.ArgumentParser(description='MMVT making movie')
    parser.add_argument('-f', '--function', help='function name', required=False, default='all', type=au.str_arr_type)
    parser.add_argument('--dpi', help='stim dpi', required=False, type=int, default=100)
    parser.add_argument('--fps', help='fps', required=False, type=int, default=10)
    parser.add_argument('--bitrate', help='bitrate', required=False, type=int, default=5000)
    parser.add_argument('--pics_type', help='pics_type', required=False, default='png')
    parser.add_argument('--show_first_pic', help='show_first_pic', required=False, type=au.is_true, default=0)
    parser.add_argument('--images_folder', help='images_folder', required=False)
    parser.add_argument('--data_in_graph', help='data_in_graph', required=False)
    parser.add_argument('--time_range', help='time_range_from', required=False, type=au.float_arr_type)
    parser.add_argument('--xtick_dt', help='xtick_dt', required=False, type=float)
    parser.add_argument('--xlabel', help='xlabel', required=False)
    parser.add_argument('--ylabels', help='ylabels', required=False, type=au.str_arr_type)
    parser.add_argument('--xticklabels', help='xticklabels', required=False, type=au.str_arr_type)
    parser.add_argument('--ylim', help='ylim', required=False, type=au.float_arr_type)
    parser.add_argument('--do_show', help='do_show', required=False, type=au.is_true, default=0)
    parser.add_argument('--n_jobs', help='cpu num', required=False, default=-1)
    args = utils.Bag(au.parse_parser(parser))
    args.xticklabels = au.str_arr_to_markers(args, 'xticklabels')
    print(args)
    n_jobs = utils.get_n_jobs(args.n_jobs)

    # fol = '/home/noam/Pictures/mmvt/mg99'
    # fol = '/homes/5/npeled/space1/Pictures/mmvt/stim/mg99/lvf6_5'
    # fol2 = ''
    # data_to_show_in_graph = 'stim'
    # video_fname = 'mg99_LVF6-5_stim.mp4'
    # cb_title = 'Electrodes PSD'
    # ylabels = ['Electrodes PSD']
    # time_range = np.arange(-1, 1.5, 0.01)
    # xticks = [-1, -0.5, 0, 0.5, 1]
    # xticklabels = [(-1, 'stim onset'), (0, 'end of stim')]
    # ylim = (0, 500)
    # xlabel = 'Time(s)'
    # cb_data_type = 'stim'
    # cb_min_max_eq = False
    # color_map = 'OrRd'


    # dpi = 100
    # bitrate = 5000
    # pics_type = 'png'
    # show_first_pic = False
    # n_jobs = 4
    # fps = 10

    '''
    Example for a call:
    make_movie -f plot_only_graph --xticklabels '-1,stim_onset,0,end_of_stim' --data_in_graph stim --time_range '-1,1.5,0.01' --xtick_dt 0.5 --xlabel time(s) --ylabels Electrodes_PSD --ylim 0,1200 --images_folder '.'

    '''

    if 'all' in args.function:
        # Call the function with --verbose-debug if you have problems with ffmpeg!
        create_movie(time_range, xticks, fol, args.dpi, args.fps, video_fname, cb_data_type, data_to_show_in_graph, cb_title,
            cb_min_max_eq, color_map, args.bitrate, fol2, ylim, ylabels, xticklabels, xlabel, args.pics_type,
            args.show_first_pic, n_jobs)
    if 'plot_only_graph' in args.function:
        plot_only_graph(args.images_folder, args.data_in_graph, args.time_range, args.xtick_dt,
                        xlabel=args.xlabel, ylabels=args.ylabels, xticklabels=args.xticklabels,
                        ylim=args.ylim, images=None, fol2='', graph2_ax=None, do_show=args.do_show)

