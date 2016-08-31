import os.path as op
import numpy as np
import glob
import time
import matplotlib.pyplot as plt

from preproc import utils
from preproc import colormaps_utils as cu

LINKS_DIR = utils.get_links_dir()
NEURO_SURF_DIR = utils.get_link_dir(LINKS_DIR, 'NeuroSurf')


def load_voltage_file(neuron_name, voltage_fname, comp_name, color_map='jet'):
    voltage = np.genfromtxt(voltage_fname, delimiter='\t')[:, 0]
    colors = cu.arr_to_colors(voltage, np.min(voltage), np.max(voltage), colors_map=color_map)[:, :3]
    colors = colors.reshape((1, colors.shape[0], colors.shape[1]))
    voltage = voltage.reshape((1, len(voltage)))
    np.savez(op.join(NEURO_SURF_DIR, neuron_name, 'voltage'), voltage=voltage, names=[comp_name], colors=colors)


def load_voltage_fol(neuron_name, fol, color_map='jet', do_plot=False):
    voltage_files = glob.glob(op.join(fol, '*.npy'))
    voltage = np.load(voltage_files[0])
    voltages = np.zeros((len(voltage_files), voltage.shape[0]))
    if do_plot:
        figure_fol = op.join(NEURO_SURF_DIR, neuron_name, 'figure', 'voltage')
        utils.make_dir(figure_fol)
    names = []
    now = time.time()
    N = len(voltage_files)
    for ind, voltage_fname in enumerate(voltage_files):
        utils.time_to_go(now, ind, N, int(N/10))
        comp_name = utils.namebase(voltage_fname)
        if comp_name == 'time':
            continue
        voltage = np.load(voltage_fname)
        voltages[ind, :] = voltage
        names.append(comp_name)
        if do_plot:
            plt.figure()
            plt.plot(voltage)
            plt.savefig(op.join(figure_fol, '{}.jpg'.format(comp_name)))
            plt.close()
    data_max, data_min = np.max(voltages[:, :]), np.min(voltages[:, :])
    colors = cu.mat_to_colors(voltages[:, :], data_min, data_max, color_map)
    np.savez(op.join(NEURO_SURF_DIR, neuron_name, 'voltage'), voltage=voltages, names=names, colors=colors)


if __name__ == '__main__':
    neuron_name = 'DCN'
    file_name = 'I020pA_Kdr100_soma_8s_trace.dat'
    voltage_fname = op.join(NEURO_SURF_DIR, neuron_name, file_name)
    # load_voltage_file(neuron_name, voltage_fname, 'soma')
    load_voltage_fol(neuron_name, op.join(NEURO_SURF_DIR, neuron_name, 'voltage'), do_plot=False)
    print('finish!')