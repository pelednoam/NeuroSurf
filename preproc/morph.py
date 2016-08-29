import numpy as np
import os.path as op

HOC_DIR = '/home/noam/hoc/'

def parse_hoc_file(model, file_name):
    hoc_fname = op.join(HOC_DIR, model, file_name)
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
    all_points = np.array(all_points)
    rad = np.array(rad)
    np.savez(op.join(HOC_DIR, model, 'morph'), point=all_points, names=comp_names, radiu=rad)
    return comp_names, all_points, rad


if __name__ == '__main__':
    model = 'KV1'
    file_name = 'DCN_morph.hoc'
    comp_names, all_points, rad = parse_hoc_file(model, file_name)
    print('finish!')