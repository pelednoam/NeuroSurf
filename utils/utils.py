import os
import os.path as op
import subprocess
import traceback
from sys import platform as _platform

from addon import  utils as au
from utils import windows_utils as wu

get_parent_fol = au.get_parent_fol
namebase = au.namebase
time_to_go = au.time_to_go
make_dir = au.make_dir
load = au.load
save = au.save

IS_LINUX = _platform == "linux" or _platform == "linux2"
IS_MAC = _platform == "darwin"
IS_WINDOWS = _platform == "win32"
print('platform: {}'.format(_platform))

def is_mac():
    return IS_MAC


def is_windows():
    return IS_WINDOWS


def is_linux():
    return IS_LINUX


def get_links_dir(links_fol_name='links'):
    parent_fol = get_parent_fol(levels=2)
    links_dir = op.join(parent_fol, links_fol_name)
    return links_dir


def get_link_dir(links_dir, link_name, var_name='', default_val='', throw_exception=False):
    val = op.join(links_dir, link_name)
    # check if this is a windows folder shortcup
    if op.isfile('{}.lnk'.format(val)):
        sc = wu.MSShortcut('{}.lnk'.format(val))
        return op.join(sc.localBasePath, sc.commonPathSuffix)
        # return read_windows_dir_shortcut('{}.lnk'.format(val))
    if not op.isdir(val) and default_val != '':
        val = default_val
    if not op.isdir(val):
        val = os.environ.get(var_name, '')
    if not op.isdir(val):
        if throw_exception:
            raise Exception('No {} dir!'.format(link_name))
        else:
            print('No {} dir!'.format(link_name))
    return val


def chunks(l, n):
    # todo: change the code to use np.array_split
    n = max(1, int(n))
    return [l[i:i + n] for i in range(0, len(l), n)]


def run_parallel(func, params, njobs=1):
    import multiprocessing
    if njobs == 1:
        results = [func(p) for p in params]
    else:
        pool = multiprocessing.Pool(processes=njobs)
        results = pool.map(func, params)
        pool.close()
    return results


def get_max_abs(data_max, data_min):
    return max(map(abs, [data_max, data_min]))


def remove_file(fname, raise_error_if_does_not_exist=False):
    try:
        if op.isfile(fname):
            os.remove(fname)
    except:
        if raise_error_if_does_not_exist:
            raise Exception(traceback.format_exc())
        else:
            print(traceback.format_exc())


def run_script(cmd, verbose=False):
    if verbose:
        print('running: {}'.format(cmd))
    if is_windows():
        output = subprocess.call(cmd)
    else:
        output = subprocess.check_output('{} | tee /dev/stderr'.format(cmd), shell=True)

    print(output)
    return output
