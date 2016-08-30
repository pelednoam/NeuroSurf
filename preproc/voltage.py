import os.path as op
import numpy as np

from preproc import utils

LINKS_DIR = utils.get_links_dir()
NEURO_SURF_DIR = utils.get_link_dir(LINKS_DIR, 'NeuroSurf')


def load_voltage_file(model, voltage_fname, comp_name):
    voltage = np.genfromtxt(voltage_fname, delimiter='\t')[:, 0]
    voltage = voltage.reshape((len(voltage), 1))
    np.savez(op.join(NEURO_SURF_DIR, model, '{}_voltage'.format(comp_name)), voltage=voltage, names=[comp_name])

if __name__ == '__main__':
    model = 'DCN'
    file_name = 'I020pA_Kdr100_soma_8s_trace.dat'
    voltage_fname = op.join(NEURO_SURF_DIR, model, file_name)
    load_voltage_file(model, voltage_fname, 'soma')
    print('finish!')