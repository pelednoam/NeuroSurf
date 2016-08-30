import importlib
import traceback
import sys
import os.path as op
import glob

import morph_panel
importlib.reload(morph_panel)
import data_panel
importlib.reload(data_panel)
import coloring_panel
importlib.reload(coloring_panel)


def main(addon_prefs=None):
    # Some initialization stuff
    try:
        print('loading panels')
        current_module = sys.modules[__name__]
        morph_panel.init(current_module)
        data_panel.init(current_module)
        coloring_panel.init(current_module)
    except:
        print('The classes are already registered!')
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
