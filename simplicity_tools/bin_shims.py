import sys
import subprocess
from .core import SimplicityTools

def slc_cli_shim():
    tools = SimplicityTools()
    slc_path = tools.get_slc_path()
    sys.exit(subprocess.call([str(slc_path)] + sys.argv[1:]))

def zap_cli_shim():
    tools = SimplicityTools()
    zap_path = tools.get_tool_path('zap')
    sys.exit(subprocess.call([str(zap_path)] + sys.argv[1:])) 