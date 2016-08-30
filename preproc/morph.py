import numpy as np
import os.path as op

from preproc import utils

LINKS_DIR = utils.get_links_dir()
NEURO_SURF_DIR = utils.get_link_dir(LINKS_DIR, 'NeuroSurf')


def parse_hoc_file(hoc_fname):
    all_points, comp_names, rad = [], [], []
    with open(hoc_fname, 'r') as f:
        for line in f:
            if 'pt3dclear()' in line and 'pt3dadd' in line:
                comp_names.append(line[:line.index('{')].strip())
                points = line.split('(')[2:]
                points1 = list(map(float, points[0].split(',')[:3]))
                points2 = list(map(float, points[1].split(',')[:3]))
                rad.append(np.mean([float(points[k].split(',')[-1].split(')')[0].strip()) for k in range(2)]))
                all_points.append(points1 + points2)
    return comp_names, np.array(all_points), np.array(rad)


if __name__ == '__main__':
    model = 'DCN'
    file_name = 'DCN_morph.hoc'
    hoc_fname = op.join(NEURO_SURF_DIR, model, file_name)
    comp_names, all_points, rad = parse_hoc_file(hoc_fname)
    np.savez(op.join(NEURO_SURF_DIR, model, 'morph'), point=all_points, names=comp_names, radiu=rad)
    print('finish!')