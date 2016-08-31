import os.path as op
import numpy as np
import glob

from preproc import utils
from preproc import colormaps_utils as cu

LINKS_DIR = utils.get_links_dir()
NEURO_SURF_DIR = utils.get_link_dir(LINKS_DIR, 'NeuroSurf')


def load_voltage_file(model, voltage_fname, comp_name):
    voltage = np.genfromtxt(voltage_fname, delimiter='\t')[:, 0]
    colors = cu.arr_to_colors(voltage, np.min(voltage), np.max(voltage), colors_map='jet')[:, :3]
    colors = colors.reshape((1, colors.shape[0], colors.shape[1]))
    voltage = voltage.reshape((1, len(voltage)))
    np.savez(op.join(NEURO_SURF_DIR, model, 'voltage'), voltage=voltage, names=[comp_name], colors=colors)


def load_voltage_fol(fol):
    voltage_files = glob.glob(op.join(fol, '*.npy'))
    voltage = np.load(voltage_files)
    voltages = np.zeros((len(voltage_files), voltage.shape[0], 4))
    for ind, voltage_fname in enumerate(voltage_files):
        print('Loading {}'.format())
        voltage = np.load(voltage_files)
        voltages[ind, :, 0] = voltage
        voltages[ind, :, 1:] = cu.mat_to_colors_two_colors_maps()
        pass


if __name__ == '__main__':
    model = 'DCN'
    file_name = 'I020pA_Kdr100_soma_8s_trace.dat'
    voltage_fname = op.join(NEURO_SURF_DIR, model, file_name)
    load_voltage_file(model, voltage_fname, 'soma')
    print('finish!')