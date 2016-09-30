import os
import os.path as op
from preproc import  windows_utils as wu
from addon import  ns_utils as au

get_parent_fol = au.get_parent_fol
namebase = au.namebase
time_to_go = au.time_to_go
make_dir = au.make_dir


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
