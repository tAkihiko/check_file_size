
from distutils.core import setup
import py2exe
import sys
sys.path.append(r'./bin')

sys.argv.append('py2exe')

py2exe_options = {
        "compressed": 1,
        "optimize": 2,
        "bundle_files": 2,
        }

setup(
        options = {"py2exe": py2exe_options},
#       console = [{
#           "script" : "check_file_size.py",
#           #"icon_resources": [(1,"py.ico")],
#           }],
        windows = [{
            "script" : "check_file_size_gui.py",
            #"icon_resources": [(1,"py.ico")],
            }],
        zipfile = None,
        )
