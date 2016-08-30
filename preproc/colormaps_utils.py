import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cmx


def get_scalar_map(x_min, x_max, color_map='jet'):
    cm = plt.get_cmap(color_map)
    cNorm = matplotlib.colors.Normalize(vmin=x_min, vmax=x_max)
    return cmx.ScalarMappable(norm=cNorm, cmap=cm)


def arr_to_colors(x, x_min=None, x_max=None, colors_map='jet', scalar_map=None):
    if scalar_map is None:
        x_min, x_max = check_min_max(x, x_min, x_max)
        scalar_map = get_scalar_map(x_min, x_max, colors_map)
    return scalar_map.to_rgba(x)


def mat_to_colors(x, x_min=None, x_max=None, colorsMap='jet', scalar_map=None, flip_cm=False):
    if flip_cm:
        x = -x
        x_min = np.min(x) if x_max is None else -x_max
        x_max = np.max(x) if x_min is None else -x_min

    x_min, x_max = check_min_max(x, x_min, x_max)
    colors = arr_to_colors(x, x_min, x_max, colorsMap, scalar_map)
    if colors.ndim == 2:
        return colors[:, :3]
    elif colors.ndim == 3:
        return colors[:, :, :3]
    raise Exception('colors ndim not 2 or 3!')


def check_min_max(x, x_min=None, x_max=None, norm_percs=None):
    if x_min is None:
        x_min = np.min(x) if norm_percs is None else np.percentile(x, norm_percs[0])
    if x_max is None:
        x_max = np.max(x) if norm_percs is None else np.percentile(x, norm_percs[1])
    return x_min, x_max


def arr_to_colors_two_colors_maps(x, x_min=None, x_max=None, cm_big='YlOrRd', cm_small='PuBu', threshold=0, default_val=0,
                                  scalar_map_big=None, scalar_map_small=None, flip_cm_big=False, flip_cm_small=False):
    colors = np.ones((len(x), 3)) * default_val
    x_min, x_max = check_min_max(x, x_min, x_max)

    if np.sum(x >= threshold) > 0:
        if not flip_cm_big:
            big_colors = arr_to_colors(x[x>=threshold], threshold, x_max, cm_big, scalar_map_big)[:, :3]
        else:
            big_colors = arr_to_colors(-x[x>=threshold], -x_max, -threshold, cm_big, scalar_map_big)[:, :3]
        colors[x>=threshold, :] = big_colors
    if np.sum(x <= -threshold) > 0:
        if not flip_cm_small:
            small_colors = arr_to_colors(x[x<=-threshold], x_min, -threshold, cm_small, scalar_map_small)[:, :3]
        else:
            small_colors = arr_to_colors(-x[x<=-threshold], threshold, -x_min, cm_small, scalar_map_small)[:, :3]
        colors[x<=-threshold, :] = small_colors
    return colors


def mat_to_colors_two_colors_maps(x, x_min=None, x_max=None, cm_big='YlOrRd', cm_small='PuBu', threshold=0, default_val=0,
        scalar_map_big=None, scalar_map_small=None, flip_cm_big=False, flip_cm_small=False, min_is_abs_max=False,
        norm_percs = None):
    colors = np.ones((x.shape[0],x.shape[1], 3)) * default_val
    x_min, x_max = check_min_max(x, x_min, x_max, norm_percs)
    if min_is_abs_max:
        x_max = max(map(abs, [x_min, x_max]))
        x_min = -x_max
    # scalar_map_pos = get_scalar_map(threshold, x_max, cm_big)
    # scalar_map_neg = get_scalar_map(x_min, -threshold, cm_small)
    # todo: calculate the scaler map before the loop to speed up
    scalar_map_pos, scalar_map_neg = None, None
    for ind in range(x.shape[0]):
        colors[ind] = arr_to_colors_two_colors_maps(x[ind], x_min, x_max, cm_big, cm_small, threshold,
            default_val, scalar_map_pos, scalar_map_neg, flip_cm_big, flip_cm_small)
    return np.array(colors)
